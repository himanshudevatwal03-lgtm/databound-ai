"""
document_processing.py

Two jobs, kept in one file since they're both "figure out if/how we can
use this uploaded file":

1. validate_upload() — checks the file before we try to do anything
   expensive with it: right extension, not empty, not oversized, and (for
   PDFs) actually starts with a real PDF header rather than trusting the
   filename alone.

2. extract_content() — turns raw file bytes into the structured
   `extracted_content` shape stored on the Document model (see
   app/models/document.py for the exact shape per file type). This is
   also where "unreadable PDF" / "malformed CSV" turn into clear errors
   rather than a silent empty result or an unhandled exception.
"""

import csv
import io

from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.config import settings


class DocumentProcessingError(Exception):
    """Raised when a file passes upload validation but fails during
    extraction (e.g. a .pdf that isn't actually readable as one)."""


def _extension_of(filename: str) -> str:
    if "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[-1].lower()


def validate_upload(file: UploadFile, file_bytes: bytes) -> str:
    """
    Validates an uploaded file and returns its normalized file_type
    ("txt" | "pdf" | "csv"). Raises HTTPException(400) with a specific,
    actionable message for every failure case called out in the spec:
    unsupported extension, empty file, oversized file, and (for PDFs) a
    file that doesn't even start with a valid PDF header.
    """
    if not file.filename:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Uploaded file has no filename.")

    ext = _extension_of(file.filename)
    if ext not in settings.allowed_file_extensions_list:
        allowed = ", ".join(settings.allowed_file_extensions_list)
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Unsupported file type '{ext or 'unknown'}'. Allowed types: {allowed}.",
        )

    if len(file_bytes) == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Uploaded file is empty.")

    if len(file_bytes) > settings.MAX_FILE_SIZE:
        max_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"File is too large. Maximum allowed size is {max_mb:.0f} MB.",
        )

    file_type = ext.lstrip(".")

    # A cheap, dependency-free sanity check: real PDFs start with "%PDF-".
    # This catches the common case of a renamed/mislabeled file before we
    # waste time trying to parse it as one.
    if file_type == "pdf" and not file_bytes.lstrip()[:5].startswith(b"%PDF-"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "This file doesn't look like a valid PDF (missing PDF header).",
        )

    return file_type


def extract_content(file_bytes: bytes, file_type: str) -> dict:
    """
    Extracts structured content from validated file bytes. Raises
    DocumentProcessingError (not HTTPException) on failure — the caller
    catches this and marks the document's status as "failed" with the
    message stored, rather than rejecting the upload outright, since by
    this point the file has already been accepted and the user should be
    able to see *why* processing failed.
    """
    if file_type == "txt":
        return _extract_txt(file_bytes)
    if file_type == "csv":
        return _extract_csv(file_bytes)
    if file_type == "pdf":
        return _extract_pdf(file_bytes)
    raise DocumentProcessingError(f"No extractor available for file type '{file_type}'.")


def _extract_txt(file_bytes: bytes) -> dict:
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        raise DocumentProcessingError(
            "Could not read this text file — it doesn't appear to be UTF-8 encoded."
        ) from e

    if not text.strip():
        raise DocumentProcessingError("This text file has no readable content.")

    return {"type": "txt", "text": text}


def _extract_csv(file_bytes: bytes) -> dict:
    try:
        text = file_bytes.decode("utf-8-sig")  # handles a leading BOM from Excel exports
    except UnicodeDecodeError as e:
        raise DocumentProcessingError(
            "Could not read this CSV file — it doesn't appear to be UTF-8 encoded."
        ) from e

    reader = csv.reader(io.StringIO(text))
    try:
        rows = list(reader)
    except csv.Error as e:
        raise DocumentProcessingError(f"This CSV file is malformed: {e}") from e

    if not rows:
        raise DocumentProcessingError("This CSV file is empty.")

    columns = [c.strip() for c in rows[0]]
    if not any(columns):
        raise DocumentProcessingError("This CSV file has no header row.")

    data_rows = []
    for row_number, row in enumerate(rows[1:], start=1):
        if not any(cell.strip() for cell in row):
            continue  # skip fully blank rows rather than erroring
        # Preserve column->value mapping even if a row is short/long
        # relative to the header, instead of silently misaligning data.
        row_data = {columns[i]: (row[i] if i < len(row) else "") for i in range(len(columns))}
        data_rows.append({"row_number": row_number, "data": row_data})

    if not data_rows:
        raise DocumentProcessingError("This CSV file has a header row but no data rows.")

    return {"type": "csv", "columns": columns, "rows": data_rows}


def _extract_pdf(file_bytes: bytes) -> dict:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        if reader.is_encrypted:
            # Try an empty password (some "encrypted" PDFs are just
            # permission-restricted, not actually password-protected).
            if reader.decrypt("") == 0:
                raise DocumentProcessingError(
                    "This PDF is password-protected and can't be read."
                )

        pages = []
        for i, page in enumerate(reader.pages, start=1):
            page_text = (page.extract_text() or "").strip()
            if page_text:
                pages.append({"page_number": i, "text": page_text})
    except PdfReadError as e:
        raise DocumentProcessingError(f"This PDF could not be read — it may be corrupted: {e}") from e

    if not pages:
        raise DocumentProcessingError(
            "No extractable text was found in this PDF (it may be scanned images without OCR)."
        )

    return {"type": "pdf", "pages": pages}
