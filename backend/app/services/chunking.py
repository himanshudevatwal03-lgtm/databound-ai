"""
chunking.py

Turns a document's `extracted_content` (see app/models/document.py for the
per-type shape) into a flat list of chunks ready for embedding and
storage. Each chunk is a dict:

    {"text": ..., "chunk_index": ..., "page_number": ... | None, "row_number": ... | None}

Chunking strategy differs deliberately by file type, per spec section 10:

  TXT — split into ~CHUNK_SIZE-character windows with CHUNK_OVERLAP
    characters of overlap, breaking on whitespace rather than mid-word so
    chunks stay readable. The overlap means a fact split across a chunk
    boundary still has a decent chance of appearing whole in at least one
    chunk.

  PDF — chunked the same way, but per page, so every chunk keeps its
    page_number. This is what lets Phase 5 cite "page 7" instead of just
    "somewhere in this PDF" (spec section 12).

  CSV — NOT run through the text splitter at all (spec section 11 is
    explicit: don't just flatten a CSV into one blob). Each row becomes
    exactly one chunk, formatted as "column: value, column: value, ...",
    keeping row_number for citation. Rows are usually short enough that
    splitting would only hurt retrieval by breaking a single record apart.
"""

from app.config import settings


def chunk_extracted_content(extracted_content: dict) -> list[dict]:
    content_type = extracted_content.get("type")

    if content_type == "txt":
        return _chunk_plain_text(extracted_content["text"])
    if content_type == "pdf":
        return _chunk_pdf_pages(extracted_content["pages"])
    if content_type == "csv":
        return _chunk_csv_rows(extracted_content["columns"], extracted_content["rows"])

    return []


def _split_text(text: str, size: int, overlap: int) -> list[str]:
    """
    Splits `text` into chunks of roughly `size` characters, overlapping by
    `overlap` characters, breaking at the nearest earlier whitespace
    rather than mid-word wherever possible.
    """
    text = text.strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + size, text_len)
        if end < text_len:
            last_space = text.rfind(" ", start, end)
            if last_space > start:
                end = last_space

        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)

        if end >= text_len:
            break
        # Step forward by (chunk length - overlap), but always make
        # progress even if overlap >= chunk length, to avoid an infinite
        # loop on pathological config values.
        start = max(end - overlap, start + 1)

    return chunks


def _chunk_plain_text(text: str) -> list[dict]:
    pieces = _split_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    return [
        {"text": piece, "chunk_index": i, "page_number": None, "row_number": None}
        for i, piece in enumerate(pieces)
    ]


def _chunk_pdf_pages(pages: list[dict]) -> list[dict]:
    chunks = []
    chunk_index = 0
    for page in pages:
        pieces = _split_text(page["text"], settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        for piece in pieces:
            chunks.append(
                {
                    "text": piece,
                    "chunk_index": chunk_index,
                    "page_number": page["page_number"],
                    "row_number": None,
                }
            )
            chunk_index += 1
    return chunks


def _chunk_csv_rows(columns: list[str], rows: list[dict]) -> list[dict]:
    chunks = []
    for i, row in enumerate(rows):
        row_data = row["data"]
        text = ", ".join(f"{col}: {row_data.get(col, '')}" for col in columns)
        chunks.append(
            {
                "text": text,
                "chunk_index": i,
                "page_number": None,
                "row_number": row["row_number"],
            }
        )
    return chunks
