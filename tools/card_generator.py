# card_generator.py
import json
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet

CARD_WIDTH = 70 * mm
CARD_HEIGHT = 100 * mm
MARGIN_X = 15 * mm
MARGIN_Y = 20 * mm
CARDS_PER_ROW = 3
CARDS_PER_COLUMN = 3


def load_questions(json_path):
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def draw_card(c, x, y, question, options):
    c.rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    text = c.beginText(x + 5 * mm, y + CARD_HEIGHT - 10 * mm)
    text.setFont("Helvetica", 8)
    text.textLines(question[:200])
    for i, option in enumerate(options):
        text.textLine(f"{chr(65 + i)}. {option[:100]}")
    c.drawText(text)


def generate_pdf(questions, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    count = 0

    for idx, q in enumerate(questions):
        row = count // CARDS_PER_ROW
        col = count % CARDS_PER_ROW

        x = MARGIN_X + col * (CARD_WIDTH + 10 * mm)
        y = A4[1] - MARGIN_Y - (row + 1) * (CARD_HEIGHT + 10 * mm)

        draw_card(c, x, y, q['question'], q['options'])
        count += 1

        if count >= CARDS_PER_ROW * CARDS_PER_COLUMN:
            c.showPage()
            count = 0

    c.save()


if __name__ == "__main__":
    input_path = Path("../doc/lang/de.json")
    output_path = Path("cards_de.pdf")
    questions = load_questions(input_path)
    generate_pdf(questions[:27], output_path)
    print(f"PDF saved to: {output_path}")

