#!/usr/bin/env python3

"""
Bitcoin Trivia Card Generator
Creates printable cards (9 per A4 page) based on the provided JSON question file.
"""

import json
import os
import argparse
import sys
import traceback
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, 
    Paragraph, 
    Table, 
    TableStyle, 
    Spacer,
    Image
)
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Define card dimensions for 3x3 grid on A4 paper
A4_WIDTH, A4_HEIGHT = A4
MARGIN = 10 * mm
CARD_WIDTH = (A4_WIDTH - 2 * MARGIN) / 3
CARD_HEIGHT = (A4_HEIGHT - 2 * MARGIN) / 3
SPACING = 2 * mm

# Define colors based on difficulty levels
DIFFICULTY_COLORS = {
    "curious": colors.Color(0.5, 0.8, 1),  # Light blue
    "bitcoiner": colors.Color(1, 0.8, 0.3),  # Gold
    "satoshi": colors.Color(1, 0.5, 0.5)   # Light red
}

# Define category icons/colors (can be enhanced with actual icons)
CATEGORY_COLORS = {
    "Bitcoin History and Adoption": colors.Color(0.2, 0.7, 0.4),  # Green
    "Technology and Security": colors.Color(0.3, 0.3, 0.9),      # Blue
    "Proof of Work and Mining": colors.Color(0.9, 0.6, 0.2)      # Orange
}

class Card(Flowable):
    """Custom flowable for a trivia card."""
    
    def __init__(self, question_data, width, height):
        Flowable.__init__(self)
        self.question_data = question_data
        self.width = width
        self.height = height
        
    def draw(self):
        # Set up the canvas for this card
        c = self.canv
        
        try:
            # Draw card background/border
            difficulty = self.question_data.get("difficulty", "curious")
            difficulty_color = DIFFICULTY_COLORS.get(difficulty, colors.white)
            category = self.question_data.get("category", "Unknown")
            category_color = CATEGORY_COLORS.get(category, colors.gray)
            
            # Draw main card background
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.black)
            c.roundRect(0, 0, self.width, self.height, 5, fill=1, stroke=1)
            
            # Draw difficulty header
            header_height = self.height / 10
            c.setFillColor(difficulty_color)
            c.rect(0, self.height - header_height, self.width, header_height, fill=1, stroke=0)
            
            # Draw category footer
            footer_height = self.height / 10
            c.setFillColor(category_color)
            c.rect(0, 0, self.width, footer_height, fill=1, stroke=0)
            
            # Add Bitcoin symbol
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(self.width - 15, self.height - 15, "₿")
            
            # Add difficulty label
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(self.width / 2, self.height - header_height / 2 - 4, difficulty.upper())
            
            # Add category label
            c.setFont("Helvetica", 7)
            c.drawCentredString(self.width / 2, footer_height / 2 - 3, category)
            
            # Add question
            c.setFont("Helvetica-Bold", 11)
            question_text = self.question_data.get("question", "Missing question")
            
            # Simple text wrapping logic - can be improved
            max_chars = 30
            if len(question_text) > max_chars:
                words = question_text.split()
                lines = []
                current_line = ""
                
                for word in words:
                    if len(current_line + " " + word) <= max_chars:
                        current_line += " " + word if current_line else word
                    else:
                        lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                    
                for i, line in enumerate(lines):
                    c.drawCentredString(self.width / 2, self.height - header_height - 15 - (i * 12), line)
            else:
                c.drawCentredString(self.width / 2, self.height - header_height - 15, question_text)
            
            # Add answer options
            options = self.question_data.get("options", [])
            if options:  # Only process if options exist and are not empty
                answer_idx = self.question_data.get("answer", 0)
                
                option_letters = ["A", "B", "C", "D"]
                start_y = self.height / 2
                
                c.setFont("Helvetica", 9)
                for i, option in enumerate(options):
                    if i < len(option_letters):  # Sicherstellen, dass wir genügend Buchstaben haben
                        y_pos = start_y - (i * 15)
                        prefix = f"{option_letters[i]}."
                        
                        # Draw the option text
                        c.drawString(10, y_pos, f"{prefix} {option}")
        
        except Exception as e:
            print(f"Fehler beim Zeichnen der Karte: {str(e)}")
            print(f"Frage-Daten: {self.question_data}")
            traceback.print_exc()


def create_trivia_cards(json_file, output_pdf):
    """Create a PDF with trivia cards from the JSON data."""
    
    # Load the question data
    try:
        print(f"Versuche JSON-Datei zu lesen: {json_file}")
        
        # Überprüfen, ob die Datei existiert
        if not os.path.exists(json_file):
            print(f"FEHLER: JSON-Datei nicht gefunden: {json_file}")
            print(f"Aktuelles Verzeichnis: {os.getcwd()}")
            print(f"Verfügbare Dateien im Ordner: {os.listdir(os.path.dirname(json_file) if os.path.dirname(json_file) else '.')}")
            return
            
        with open(json_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        print(f"JSON erfolgreich geladen: {len(questions)} Fragen gefunden.")
    except Exception as e:
        print(f"Fehler beim Laden der JSON-Datei: {str(e)}")
        traceback.print_exc()
        return
    
    if not questions:
        print("Fehler: Keine Fragen in der JSON-Datei gefunden.")
        return
    
    # Set up the PDF document
    try:
        print(f"Erstelle PDF-Dokument: {output_pdf}")
        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN
        )
        
        # Create the story (content)
        story = []
        
        # Group cards into pages (9 cards per page)
        for i in range(0, len(questions), 9):
            page_questions = questions[i:i+9]
            print(f"Verarbeite Fragen {i+1} bis {i+len(page_questions)}")
            
            # Create a 3x3 grid for the cards
            data = []
            row = []
            
            for j, q in enumerate(page_questions):
                # Create card
                card = Card(q, CARD_WIDTH - SPACING, CARD_HEIGHT - SPACING)
                
                # Add to row
                row.append(card)
                
                # After 3 cards, start a new row
                if (j + 1) % 3 == 0:
                    data.append(row)
                    row = []
            
            # If we have an incomplete row, add it
            if row:
                # Pad with empty cells
                while len(row) < 3:
                    row.append("")
                data.append(row)
            
            # Create table with the cards
            table = Table(data, colWidths=[CARD_WIDTH]*3, rowHeights=[CARD_HEIGHT]*len(data))
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), SPACING/2),
                ('RIGHTPADDING', (0, 0), (-1, -1), SPACING/2),
                ('TOPPADDING', (0, 0), (-1, -1), SPACING/2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), SPACING/2),
            ]))
            
            story.append(table)
            
        # DAS IST DER WICHTIGSTE TEIL DER FEHLTE - PDF ERSTELLEN!
        print("Erstelle PDF...")
        doc.build(story)
        
        print(f"Trivia-Karten PDF erstellt: {output_pdf}")
    
    except Exception as e:
        print(f"Fehler beim Erstellen des PDFs: {str(e)}")
        traceback.print_exc()


def create_answer_sheet(json_file, output_pdf):
    """Create an answer sheet PDF from the JSON data."""
    
    # Load the question data
    try:
        print(f"Lade JSON-Datei für Lösungsblatt: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        print(f"JSON erfolgreich geladen: {len(questions)} Fragen gefunden.")
    except Exception as e:
        print(f"Fehler beim Laden der JSON-Datei für Lösungsblatt: {str(e)}")
        traceback.print_exc()
        return
    
    # Set up the PDF document
    try:
        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=A4,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Create styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Custom style for answers
        answer_style = ParagraphStyle(
            'AnswerStyle',
            parent=normal_style,
            spaceBefore=6,
            spaceAfter=12,
            leftIndent=20
        )
        
        # Create the story (content)
        story = []
        
        # Add title
        story.append(Paragraph("Bitcoin Trivia - Answer Sheet", title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Group by difficulty
        difficulties = sorted(set(q.get('difficulty', 'unknown') for q in questions))
        
        for difficulty in difficulties:
            # Add difficulty heading
            story.append(Paragraph(f"Difficulty: {difficulty.title()}", heading_style))
            story.append(Spacer(1, 0.3*cm))
            
            # Filter questions by this difficulty
            diff_questions = [q for q in questions if q.get('difficulty') == difficulty]
            
            # Add each question and its answer
            for i, q in enumerate(diff_questions):
                try:
                    question_text = q.get("question", "Missing question")
                    options = q.get("options", [])
                    correct_idx = q.get("answer", 0)
                    
                    if options and correct_idx < len(options):
                        correct_answer = options[correct_idx]
                    else:
                        correct_answer = "Keine Antwort verfügbar"
                        print(f"Warnung: Ungültiger Antwortindex oder leere Optionen für Frage: {question_text}")
                    
                    question_num = i + 1
                    story.append(Paragraph(f"{question_num}. {question_text}", normal_style))
                    story.append(Paragraph(f"Answer: {correct_answer}", answer_style))
                except Exception as e:
                    print(f"Fehler bei Frage #{i+1}: {str(e)}")
                    print(f"Frage-Daten: {q}")
            
            story.append(Spacer(1, 0.5*cm))
        
        # Build the PDF
        doc.build(story)
        
        print(f"Lösungsblatt PDF erstellt: {output_pdf}")
    
    except Exception as e:
        print(f"Fehler beim Erstellen des Lösungsblatts: {str(e)}")
        traceback.print_exc()


# Define a PageBreak flowable
class PageBreak(Flowable):
    def __init__(self):
        Flowable.__init__(self)
        self.width = 0
        self.height = 0
        
    def draw(self):
        self.canv.showPage()


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Generate Bitcoin Trivia cards for print')
        parser.add_argument('--json', default='docs/lang/en.json', help='Path to the questions JSON file')
        parser.add_argument('--output', default='bitcoin_trivia_cards.pdf', help='Output PDF file name')
        parser.add_argument('--answers', action='store_true', help='Also generate an answer sheet')
        
        args = parser.parse_args()
        
        print(f"Startparameter: JSON-Datei: {args.json}, Ausgabedatei: {args.output}, Lösungsblatt: {args.answers}")
        
        # Prüfen, ob die JSON-Datei existiert und korrekten Pfad ermitteln
        json_file = args.json
        if not os.path.exists(json_file):
            # Alternative Pfade prüfen
            alt_paths = [
                os.path.join("tools", "lang", os.path.basename(json_file)),
                os.path.join("lang", os.path.basename(json_file)),
                os.path.join("tools", os.path.basename(json_file))
            ]
            
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    json_file = alt_path
                    print(f"JSON-Datei gefunden unter alternativen Pfad: {json_file}")
                    break
            else:
                print(f"Fehler: Die JSON-Datei '{args.json}' existiert nicht.")
                print(f"Aktuelles Verzeichnis: {os.getcwd()}")
                print(f"Verfügbare Dateien:")
                for root, dirs, files in os.walk("."):
                    for file in files:
                        if file.endswith(".json"):
                            print(os.path.join(root, file))
                sys.exit(1)
        
        # Create the cards PDF
        create_trivia_cards(json_file, args.output)
        
        # Create answer sheet if requested
        if args.answers:
            answer_output = args.output.replace('.pdf', '_answers.pdf')
            create_answer_sheet(json_file, answer_output)
    
    except Exception as e:
        print(f"Unerwarteter Fehler: {str(e)}")
        traceback.print_exc()
