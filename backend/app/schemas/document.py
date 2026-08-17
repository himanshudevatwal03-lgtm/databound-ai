"""
document.py (schemas)

DocumentResponse deliberately omits `extracted_content` — it can be large
(a whole PDF's worth of text) and isn't needed by the document list/detail
views in this phase. It'll be used internally by Phase 4's chunking step
and Phase 5's retrieval, not returned wholesale over the API. `preview` is
a short excerpt instead, just enough to recognize the document at a glance.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: uuid.UUID
    collection_id: uuid.UUID | None
    filename: str
    file_type: str
    file_size: int
    version: int
    status: str
    processing_error: str | None
    preview: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


def build_preview(extracted_content: dict | None, max_chars: int = 240) -> str | None:
    """
    Produces a short, human-readable excerpt from a document's extracted
    content, regardless of file type, for use in list/card views.
    """
    if not extracted_content:
        return None

    content_type = extracted_content.get("type")

    if content_type == "txt":
        text = extracted_content.get("text", "")
    elif content_type == "pdf":
        pages = extracted_content.get("pages", [])
        text = pages[0]["text"] if pages else ""
    elif content_type == "csv":
        columns = extracted_content.get("columns", [])
        row_count = len(extracted_content.get("rows", []))
        text = f"Columns: {', '.join(columns)} — {row_count} row(s)"
    else:
        text = ""

    text = " ".join(text.split())  # collapse whitespace/newlines
    if len(text) > max_chars:
        return text[:max_chars].rstrip() + "..."
    return text or None
