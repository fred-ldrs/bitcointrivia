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
import glob
import datetime
import re
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
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Define card dimensions for 3x3 grid on A4 paper
A4_WIDTH, A4_HEIGHT = A4
MARGIN = 10 * mm
CARD_WIDTH = (A4_WIDTH - 2 * MARGIN) / 3
CARD_HEIGHT = (A4_HEIGHT - 2 * MARGIN) / 3
SPACING = 2 * mm

# Define mapping for difficulty levels (to rename them)
DIFFICULTY_MAPPING = {
    "curious": "BITCOINER",
    "bitcoiner": "CYPHERPUNK",
    "satoshi": "SATOSHI"
}

# Define colors based on difficulty levels
DIFFICULTY_COLORS = {
    "BITCOINER": colors.Color(0.5, 0.8, 1),   # Light blue (was "curious")
    "CYPHERPUNK": colors.Color(1, 0.8, 0.3),  # Gold (was "bitcoiner")
    "SATOSHI": colors.Color(1, 0.5, 0.5)      # Light red (kept as "satoshi")
}

# Define English category colors
CATEGORY_COLORS = {
    "Bitcoin History and Adoption": colors.Color(0.2, 0.7, 0.4),  # Green
    "Technology and Security": colors.Color(0.3, 0.3, 0.9),      # Blue
    "Proof of Work and Mining": colors.Color(0.9, 0.6, 0.2)      # Orange
}

# Define German to English category mapping
# This ensures that German categories use the same colors as their English counterparts
CATEGORY_MAPPING = {
    # German categories mapped to English equivalent
    "Bitcoin Geschichte und Adoption": "Bitcoin History and Adoption",
    "Technologie und Sicherheit": "Technology and Security",
    "Proof of Work und Mining": "Proof of Work and Mining"
}

# Logo path
LOGO_PATH = os.path.join("tools", "BitcoinTriviaV3_copy.png")

# Process tracking to avoid duplicates
PROCESSED_FILES = set()

def get_timestamp():
    """Return a timestamp string for filenames."""
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d_%H%M%S")

def replace_bitcoin_symbol(text):
    """Replace Bitcoin symbol with safe alternative."""
    # Replace both Unicode Bitcoin symbol and text representation
    return text.replace("₿", "BTC").replace("Bitcoin", "Bitcoin")

def wrap_text(text, max_chars, canvas, font_name, font_size):
    """Wrap text to fit within max_chars per line with better space usage."""
    # First replace any Bitcoin symbol to avoid display issues
    text = replace_bitcoin_symbol(text)
    
    # For better text wrapping, consider word length
    canvas.setFont(font_name, font_size)
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if len(test_line) <= max_chars:
            current_line = test_line
        else:
            # If the current word is very long, we might need to break it
            if len(word) > max_chars - 2 and not current_line:
                # Break long words if necessary
                while len(word) > max_chars:
                    lines.append(word[:max_chars-1] + "-")
                    word = word[max_chars-1:]
                current_line = word
            else:
                lines.append(current_line)
                current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

def calculate_option_height(option, max_chars, font_size):
    """Calculate the height needed for an option based on text length."""
    # Estimate number of lines
    words = option.split()
    current_line = ""
    line_count = 1
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if len(test_line) <= max_chars:
            current_line = test_line
        else:
            # If the word is very long, we might need to count additional lines
            if len(word) > max_chars:
                line_count += (len(word) + max_chars - 1) // max_chars
            else:
                line_count += 1
            current_line = word
    
    # Calculate total height (line_count * font_size * 1.2 for line spacing)
    return line_count * font_size * 1.2

def get_category_color(category):
    """Get the correct color for a category, with language mapping."""
    # If the category is in the mapping (e.g., German), map it to English first
    mapped_category = CATEGORY_MAPPING.get(category, category)
    
    # Then get the color based on the mapped (or original) category
    return CATEGORY_COLORS.get(mapped_category, colors.gray)

def draw_card(canvas, x, y, question_data, width, height):
    """Draw a card directly on the canvas at the specified position."""
    # Save the canvas state
    canvas.saveState()
    
    try:
        # Translate to card position
        canvas.translate(x, y)
        
        # Draw card background/border
        original_difficulty = question_data.get("difficulty", "curious")
        difficulty = DIFFICULTY_MAPPING.get(original_difficulty, original_difficulty).upper()
        difficulty_color = DIFFICULTY_COLORS.get(difficulty, colors.white)
        
        # Get category and apply language mapping for color selection
        category = question_data.get("category", "Unknown")
        category_color = get_category_color(category)
        
        # Draw main card background
        canvas.setFillColor(colors.white)
        
        # Draw difficulty header
        header_height = height / 10
        canvas.setFillColor(difficulty_color)
        canvas.rect(0, height - header_height, width, header_height, fill=1, stroke=0)
        
        # Draw category footer
        footer_height = height / 10
        canvas.setFillColor(category_color)
        canvas.rect(0, 0, width, footer_height, fill=1, stroke=0)
        
        # Draw the card border on top of the colored areas
        canvas.setFillColor(colors.white)
        canvas.setStrokeColor(colors.black)
        canvas.roundRect(0, 0, width, height, 5, fill=0, stroke=1)
        
        # Add logo if available
        logo_path = LOGO_PATH
        if os.path.exists(logo_path):
            try:
                # Erhält die Proportionen
                logo_width = 15
                logo_height = 15
                canvas.drawImage(logo_path, width - logo_width - 5, height - logo_height - 5, 
                                width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                print(f"Fehler beim Laden des Logos: {str(e)}")
                # Fallback to Bitcoin symbol if logo can't be loaded
                canvas.setFillColor(colors.black)
                canvas.setFont("Helvetica-Bold", 14)
                canvas.drawString(width - 15, height - 15, "BTC")
        else:
            # Fallback to Bitcoin symbol
            print(f"Logo nicht gefunden unter: {logo_path}")
            canvas.setFillColor(colors.black)
            canvas.setFont("Helvetica-Bold", 14)
            canvas.drawString(width - 15, height - 15, "BTC")
        
        # Add difficulty label with more padding
        canvas.setFillColor(colors.black)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(width / 2, height - header_height / 2 - 4, difficulty)
        
        # Add category label
        canvas.setFont("Helvetica", 7)
        canvas.drawCentredString(width / 2, footer_height / 2 - 3, category)
        
        # Add question with more padding from the sides
        canvas.setFillColor(colors.black)
        question_text = question_data.get("question", "Missing question")
        
        # Replace Bitcoin symbol to avoid display problems
        question_text = replace_bitcoin_symbol(question_text)
        
        # Better text wrapping for question with reduced max width for more padding
        max_chars = 30  # Increased from 28 to allow more text per line
        question_lines = wrap_text(question_text, max_chars, canvas, "Helvetica-Bold", 11)
        question_area_height = min(height / 3, len(question_lines) * 12 + 10)  # Limit question area height
        
        for i, line in enumerate(question_lines):
            y_pos = height - header_height - 15 - (i * 12)
            canvas.drawCentredString(width / 2, y_pos, line)
        
        # Draw a line to separate question from answer options
        canvas.setStrokeColor(colors.lightgrey)
        separator_y = height - header_height - question_area_height - 10
        canvas.line(15, separator_y, width - 15, separator_y)  # Increased side padding here too
        
        # Add answer options with better formatting and spacing
        options = question_data.get("options", [])
        if options:  # Only process if options exist and are not empty
            answer_idx = question_data.get("answer", 0)
            
            # Calculate space needed for each option
            option_font_size = 9
            option_max_chars = 30  # Increased from 26 to use more space
            option_heights = []
            
            for option in options:
                # Replace Bitcoin symbol in options too
                option = replace_bitcoin_symbol(option)
                option_heights.append(calculate_option_height(option, option_max_chars, option_font_size))
            
            # Calculate total height needed and adjust spacing
            total_options_height = sum(option_heights)
            available_height = separator_y - footer_height - 10
            
            # Add minimum spacing between options
            min_spacing = 5  # minimum 5 points between options
            total_min_spacing = min_spacing * (len(options) - 1)
            
            # Check if we need to reduce font size
            if total_options_height + total_min_spacing > available_height:
                option_font_size = 8  # Reduce font size if needed
                # Recalculate heights with smaller font
                option_heights = []
                for option in options:
                    option = replace_bitcoin_symbol(option)
                    option_heights.append(calculate_option_height(option, option_max_chars, option_font_size))
                total_options_height = sum(option_heights)
            
            # Calculate positions for each option
            option_letters = ["A", "B", "C", "D"]
            current_y = separator_y - 15  # Start below separator
            
            for i, option in enumerate(options):
                if i < len(option_letters):
                    # Replace Bitcoin symbol
                    option = replace_bitcoin_symbol(option)
                    
                    # Mark the correct answer with a bold letter in brackets
                    letter = option_letters[i]
                    if i == answer_idx:
                        canvas.setFont("Helvetica-Bold", option_font_size)
                        letter_prefix = f"[{letter}]"
                    else:
                        canvas.setFont("Helvetica", option_font_size)
                        letter_prefix = f"{letter}."
                    
                    # Draw option letter with more padding from left edge
                    canvas.drawString(10, current_y, letter_prefix)  # Decreased left padding to 10
                    
                    # Switch back to regular font for the option text
                    canvas.setFont("Helvetica", option_font_size)
                    
                    # Draw the option text with wrapping
                    option_lines = wrap_text(option, option_max_chars - 2, canvas, "Helvetica", option_font_size)
                    for j, line in enumerate(option_lines):
                        if j == 0:
                            # First line comes after the letter
                            canvas.drawString(25, current_y, line)  # Decreased indent to 25
                        else:
                            # Subsequent lines are indented
                            canvas.drawString(25, current_y - (j * (option_font_size + 2)), line)  # Decreased indent to 25
                    
                    # Move to the next option position with more spacing for multi-line options
                    line_count = len(option_lines)
                    line_spacing = option_font_size + 2
                    option_total_height = line_count * line_spacing
                    current_y -= max(option_total_height, option_font_size + 5) + min_spacing + 2  # Reduced extra padding to 2
    
    except Exception as e:
        print(f"Fehler beim Zeichnen der Karte: {str(e)}")
        print(f"Frage-Daten: {question_data}")
        traceback.print_exc()
    
    finally:
        # Restore the canvas state
        canvas.restoreState()


def create_trivia_cards(json_file, output_pdf):
    """Create a PDF with trivia cards from the JSON data."""
    
    # Normalisiere die Pfade für konsistente Speicherung im Set
    json_file = os.path.normpath(json_file)
    
    # Check if we already processed this file to avoid duplicates
    file_key = f"{json_file}"  # Use just the JSON file path as key
    if file_key in PROCESSED_FILES:
        print(f"Überspringe bereits verarbeitete Datei: {json_file}")
        return True, output_pdf
    
    PROCESSED_FILES.add(file_key)
    
    # Add timestamp to filename
    timestamp = get_timestamp()
    base_name, extension = os.path.splitext(output_pdf)
    output_pdf_with_timestamp = f"{base_name}_{timestamp}{extension}"
    
    # Load the question data
    try:
        print(f"Versuche JSON-Datei zu lesen: {json_file}")
        
        # Überprüfen, ob die Datei existiert
        if not os.path.exists(json_file):
            print(f"FEHLER: JSON-Datei nicht gefunden: {json_file}")
            print(f"Aktuelles Verzeichnis: {os.getcwd()}")
            print(f"Verfügbare Dateien im Ordner: {os.listdir(os.path.dirname(json_file) if os.path.dirname(json_file) else '.')}")
            return False, None
            
        with open(json_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        print(f"JSON erfolgreich geladen: {len(questions)} Fragen gefunden.")
    except Exception as e:
        print(f"Fehler beim Laden der JSON-Datei: {str(e)}")
        traceback.print_exc()
        return False, None
    
    if not questions:
        print("Fehler: Keine Fragen in der JSON-Datei gefunden.")
        return False, None
    
    # Set up the PDF document
    try:
        print(f"Erstelle PDF-Dokument: {output_pdf_with_timestamp}")
        
        # Wir verwenden einen direkten Canvas-Ansatz
        c = canvas.Canvas(output_pdf_with_timestamp, pagesize=A4)
        
        # Group cards into pages (9 cards per page) - 3x3 grid
        cards_per_page = 9
        cards_per_row = 3
        
        total_pages = (len(questions) + cards_per_page - 1) // cards_per_page
        
        for page in range(total_pages):
            print(f"Erstelle Seite {page+1} von {total_pages}")
            
            start_idx = page * cards_per_page
            end_idx = min(start_idx + cards_per_page, len(questions))
            
            for i in range(start_idx, end_idx):
                # Calculate card position in the grid
                rel_idx = i - start_idx
                row = rel_idx // cards_per_row
                col = rel_idx % cards_per_row
                
                # Calculate card position on page
                x = MARGIN + col * CARD_WIDTH
                y = A4_HEIGHT - MARGIN - (row + 1) * CARD_HEIGHT + SPACING / 2
                
                # Draw the card
                draw_card(
                    c, 
                    x, 
                    y, 
                    questions[i], 
                    CARD_WIDTH - SPACING, 
                    CARD_HEIGHT - SPACING
                )
            
            # Add a new page if needed
            if page < total_pages - 1:
                c.showPage()
        
        # Save the PDF
        c.save()
        
        print(f"Trivia-Karten PDF erstellt: {output_pdf_with_timestamp}")
        return True, output_pdf_with_timestamp
    
    except Exception as e:
        print(f"Fehler beim Erstellen des PDFs: {str(e)}")
        traceback.print_exc()
        return False, None


def find_json_files():
    """Find all available JSON files in various locations."""
    search_paths = [
        os.path.join("docs", "lang", "*.json"),
        #os.path.join("tools", "lang", "*.json"),
        #os.path.join("lang", "*.json"),
        #os.path.join("tools", "*.json"),
        #os.path.join("docs", "lang_copy", "*.json"),
        #os.path.join("tools", "lang_copy", "*.json"),
        #os.path.join("lang_copy", "*.json")
    ]
    
    json_files = []
    found_paths = set()  # Verwenden eines Sets zur Vermeidung von Duplikaten
    
    for pattern in search_paths:
        for file_path in glob.glob(pattern):
            # Normalisiere den Pfad und überprüfe auf Duplikate
            norm_path = os.path.normpath(file_path)
            basename = os.path.basename(norm_path)
            
            # Prüfe, ob wir bereits eine Datei mit diesem Namen haben
            # Wenn ja, überspringen wir die Datei
            if basename not in found_paths:
                found_paths.add(basename)
                json_files.append(norm_path)
    
    return json_files


def process_all_languages(create_answers=False):  # Default to no answer sheets
    """Process all available language files."""
    json_files = find_json_files()
    if not json_files:
        print("Keine JSON-Dateien gefunden!")
        print("Aktuelles Verzeichnis:", os.getcwd())
        print("Verfügbare Dateien:")
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.json'):
                    print(os.path.join(root, file))
        return False
    
    print(f"Gefundene JSON-Dateien: {len(json_files)}")
    
    successful = 0
    total = len(json_files)
    
    # Vermeide doppelte Verarbeitung
    processed_basenames = set()
    
    for json_file in json_files:
        # Extrahiere Sprachcode aus Dateinamen (z.B. "en.json" -> "en")
        basename = os.path.basename(json_file)
        if basename in processed_basenames:
            print(f"Überspringe doppelte Datei: {json_file}")
            continue
            
        processed_basenames.add(basename)
        lang_code = os.path.splitext(basename)[0]
        output_pdf = f"bitcoin_trivia_cards_{lang_code}.pdf"
        
        print(f"\n=== Verarbeite Sprache: {lang_code} ===")
        print(f"JSON-Datei: {json_file}")
        print(f"Ausgabe-PDF: {output_pdf}")
        
        # Create the cards PDF
        success, _ = create_trivia_cards(json_file, output_pdf)
        
        if success:
            successful += 1
    
    print(f"\n=== Zusammenfassung ===")
    print(f"{successful} von {total} Sprachdateien erfolgreich verarbeitet.")
    return successful > 0


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Generate Bitcoin Trivia cards for print')
        parser.add_argument('--json', help='Path to a specific questions JSON file')
        parser.add_argument('--output', default='bitcoin_trivia_cards.pdf', help='Output PDF file name when processing a single JSON file')
        parser.add_argument('--answers', action='store_true', help='Also generate an answer sheet', default=False)  # Default to no answer sheets
        
        args = parser.parse_args()
        
        # Überprüfe, ob das Logo existiert
        if not os.path.exists(LOGO_PATH):
            print(f"Warnung: Logo-Datei nicht gefunden unter: {LOGO_PATH}")
            print("Aktuelles Verzeichnis:", os.getcwd())
            print("Suche nach Bilddateien in tools-Ordner:")
            if os.path.exists("tools"):
                for file in os.listdir("tools"):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        print(f"Gefundene Bilddatei: {file}")
        else:
            print(f"Logo gefunden: {LOGO_PATH}")
        
        # Standardmodus oder Einzelne JSON-Datei
        if args.json:
            # Einzelne JSON-Datei verarbeiten
            print(f"Verarbeite einzelne JSON-Datei: {args.json}")
            json_file = args.json
            if not os.path.exists(json_file):
                # Alternative Pfade prüfen
                alt_paths = [
                    os.path.join("tools", "lang", os.path.basename(json_file)),
                    os.path.join("lang", os.path.basename(json_file)),
                    os.path.join("tools", os.path.basename(json_file)),
                    os.path.join("docs", "lang", os.path.basename(json_file)),
                    os.path.join("tools", "lang_copy", os.path.basename(json_file)),
                    os.path.join("lang_copy", os.path.basename(json_file)),
                    os.path.join("docs", "lang_copy", os.path.basename(json_file))
                ]
                
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        json_file = alt_path
                        print(f"JSON-Datei gefunden unter alternativen Pfad: {json_file}")
                        break
                else:
                    print(f"Fehler: Die JSON-Datei '{args.json}' existiert nicht.")
                    print(f"Aktuelles Verzeichnis: {os.getcwd()}")
                    print(f"Verfügbare JSON-Dateien:")
                    for json_file in find_json_files():
                        print(f"  {json_file}")
                    # Statt zu beenden, verarbeiten wir automatisch alle verfügbaren Dateien
                    print("\nVerarbeite stattdessen alle verfügbaren Sprachdateien...")
                    process_all_languages(args.answers)
                    sys.exit(0)
            
            # Create the cards PDF for the specified file
            success, _ = create_trivia_cards(json_file, args.output)
            
            # KEINE weitere Verarbeitung anderer Dateien wenn eine Datei explizit angegeben wurde
            # So vermeiden wir doppelte Verarbeitung der en.json
            if not success:
                print("\nFehler bei der Verarbeitung der angegebenen JSON-Datei. Verarbeite stattdessen alle verfügbaren Dateien...")
                process_all_languages(args.answers)
        else:
            # Standardmodus: Alle Sprachdateien verarbeiten
            print("Verarbeite alle verfügbaren Sprachdateien...")
            process_all_languages(args.answers)
    
    except Exception as e:
        print(f"Unerwarteter Fehler: {str(e)}")
        traceback.print_exc()
