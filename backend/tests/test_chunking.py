"""
test_chunking.py

Pure unit tests for chunk_extracted_content — no database needed, since
chunking operates entirely on the in-memory extracted_content dict shape.
Covers all three file-type chunking strategies plus the edge cases most
likely to break them (empty content, content shorter than one chunk).
"""

from app.config import settings
from app.services.chunking import chunk_extracted_content


def test_chunk_short_txt_produces_single_chunk():
    content = {"type": "txt", "text": "Rahul's CGPA is 8.4."}
    chunks = chunk_extracted_content(content)

    assert len(chunks) == 1
    assert chunks[0]["text"] == "Rahul's CGPA is 8.4."
    assert chunks[0]["page_number"] is None
    assert chunks[0]["row_number"] is None
    assert chunks[0]["chunk_index"] == 0


def test_chunk_long_txt_produces_multiple_overlapping_chunks():
    # Build text well beyond CHUNK_SIZE so it must split into 3+ chunks.
    paragraph = "The quick brown fox jumps over the lazy dog. " * 60
    content = {"type": "txt", "text": paragraph}

    chunks = chunk_extracted_content(content)

    assert len(chunks) > 1
    for c in chunks:
        # Each chunk should be roughly chunk-sized, not wildly over.
        assert len(c["text"]) <= settings.CHUNK_SIZE + 50
    # Indices are sequential starting at 0.
    assert [c["chunk_index"] for c in chunks] == list(range(len(chunks)))


def test_chunk_empty_txt_produces_no_chunks():
    assert chunk_extracted_content({"type": "txt", "text": "   "}) == []


def test_chunk_pdf_keeps_page_numbers():
    content = {
        "type": "pdf",
        "pages": [
            {"page_number": 1, "text": "Project deadline: 25 August 2026."},
            {"page_number": 2, "text": "Arjun Verma is responsible for testing."},
        ],
    }

    chunks = chunk_extracted_content(content)

    assert len(chunks) == 2
    assert chunks[0]["page_number"] == 1
    assert "deadline" in chunks[0]["text"]
    assert chunks[1]["page_number"] == 2
    assert "Arjun" in chunks[1]["text"]
    assert all(c["row_number"] is None for c in chunks)


def test_chunk_csv_produces_one_chunk_per_row_with_row_number():
    content = {
        "type": "csv",
        "columns": ["name", "department", "salary"],
        "rows": [
            {"row_number": 1, "data": {"name": "Rahul", "department": "Engineering", "salary": "55000"}},
            {"row_number": 2, "data": {"name": "Priya", "department": "Finance", "salary": "60000"}},
        ],
    }

    chunks = chunk_extracted_content(content)

    assert len(chunks) == 2
    assert chunks[0]["row_number"] == 1
    assert "Rahul" in chunks[0]["text"]
    assert "Engineering" in chunks[0]["text"]
    assert chunks[1]["row_number"] == 2
    assert "Priya" in chunks[1]["text"]
    assert all(c["page_number"] is None for c in chunks)


def test_chunk_unknown_type_returns_empty_list():
    assert chunk_extracted_content({"type": "mystery"}) == []
