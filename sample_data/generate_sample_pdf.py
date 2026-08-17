"""
generate_sample_pdf.py

Generates sample_data/project_requirements.pdf — a small multi-page PDF
used to manually test PDF upload/extraction and, from Phase 5 onward,
question answering with page-numbered citations.

This is a one-off dev script, not a runtime dependency of the app, so its
only requirement (reportlab) is intentionally NOT in backend/requirements.txt.
Run it once, locally:

    pip install reportlab
    python sample_data/generate_sample_pdf.py

The resulting PDF is already checked into sample_data/, so most people
won't need to run this at all — it's here for transparency and in case
the sample content ever needs to change.
"""

import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "project_requirements.pdf")


def build_pdf():
    c = canvas.Canvas(OUTPUT_PATH, pagesize=letter)
    width, height = letter

    def draw_page(title, lines):
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, title)
        c.setFont("Helvetica", 11)
        y = height - 1.4 * inch
        for line in lines:
            c.drawString(1 * inch, y, line)
            y -= 0.28 * inch
        c.showPage()

    draw_page(
        "Project Requirements — DataBound AI Sample",
        [
            "Project name: Internal Knowledge Assistant Pilot",
            "Project deadline: 25 August 2026",
            "Project owner: Priya Menon",
            "",
            "Objective: Build a small internal tool so the support team can",
            "ask questions about our own product documentation and get",
            "answers with citations, instead of searching manually.",
        ],
    )

    draw_page(
        "Scope and Technology",
        [
            "In scope for this pilot:",
            "  - Upload PDF and TXT documentation",
            "  - Ask natural-language questions about uploaded docs",
            "  - Show source citations for every answer",
            "",
            "Technologies being used: FastAPI, React, PostgreSQL.",
            "Out of scope for this pilot: multi-language support.",
        ],
    )

    draw_page(
        "Testing Strategy",
        [
            "Testing responsibilities:",
            "  - Arjun Verma is responsible for testing.",
            "  - Sneha Iyer is responsible for QA sign-off before launch.",
            "",
            "Test coverage should include upload validation, retrieval",
            "accuracy, and — critically — hallucination tests: the system",
            "must say when it doesn't have enough information, rather",
            "than guessing.",
        ],
    )

    c.save()


if __name__ == "__main__":
    build_pdf()
    print(f"Wrote {OUTPUT_PATH}")
