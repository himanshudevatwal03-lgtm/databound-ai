"""
documents.py (api)

Upload, list, retrieve, and delete documents (spec sections 9, 10, 16).

The upload flow is deliberately synchronous for this phase: validate ->
extract -> store, all within the request. That's simple and fine for
TXT/CSV/reasonably-sized PDFs; a truly async job queue (upload returns
immediately with status="processing", extraction happens in the
background) is a reasonable future improvement once large files or a
production user base make synchronous processing too slow — noted in the
README's Future Improvements.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.collection import Collection
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse, build_preview
from app.services.document_processing import (
    DocumentProcessingError,
    extract_content,
    validate_upload,
)
from app.services.indexing import index_document

router = APIRouter(prefix="/documents", tags=["documents"])


def _to_response(document: Document) -> DocumentResponse:
    response = DocumentResponse.model_validate(document)
    response.preview = build_preview(document.extracted_content)
    return response


def _get_owned_document_or_404(db: Session, document_id: uuid.UUID, user: User) -> Document:
    document = (
        db.query(Document).filter(Document.id == document_id, Document.user_id == user.id).first()
    )
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found.")
    return document


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    collection_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if collection_id is not None:
        owned = (
            db.query(Collection)
            .filter(Collection.id == collection_id, Collection.user_id == current_user.id)
            .first()
        )
        if owned is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Collection not found.")

    file_bytes = await file.read()

    # Raises HTTPException(400) directly for anything wrong enough that
    # the upload itself should be rejected (bad extension, empty, too
    # large, obviously-not-a-PDF).
    file_type = validate_upload(file, file_bytes)

    document = Document(
        user_id=current_user.id,
        collection_id=collection_id,
        filename=file.filename,
        file_type=file_type,
        file_size=len(file_bytes),
        status="processing",
    )

    # Extraction failures are more nuanced than validation failures: the
    # upload itself was reasonable (right type, right size), but the
    # *content* couldn't be parsed (corrupted PDF, malformed CSV, wrong
    # encoding). We store the document as "failed" with a reason rather
    # than rejecting the request outright, so the user can see why and
    # decide whether to fix the file and retry.
    try:
        document.extracted_content = extract_content(file_bytes, file_type)
        document.status = "ready"
    except DocumentProcessingError as e:
        document.status = "failed"
        document.processing_error = str(e)

    db.add(document)
    db.commit()
    db.refresh(document)

    # Chunking + embedding (Phase 4): only runs when extraction actually
    # produced usable content. Deliberately NOT allowed to fail the
    # upload response — if indexing has trouble, the document still
    # exists as "ready" with its extracted content intact; it's simply
    # not searchable yet. Retrieval finding nothing for it is a safe
    # failure mode (leads to "not enough information" in Phase 5+, not a
    # wrong answer), so we surface the problem via processing_error
    # rather than discarding the whole upload.
    if document.status == "ready":
        try:
            index_document(db, document)
        except Exception as e:
            document.processing_error = f"Document was saved but indexing failed: {e}"
            db.commit()
            db.refresh(document)

    return _to_response(document)


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    collection_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Document).filter(Document.user_id == current_user.id)
    if collection_id is not None:
        query = query.filter(Document.collection_id == collection_id)
    documents = query.order_by(Document.created_at.desc()).all()
    return [_to_response(d) for d in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = _get_owned_document_or_404(db, document_id, current_user)
    return _to_response(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = _get_owned_document_or_404(db, document_id, current_user)
    # DocumentChunk rows are removed automatically by the database via
    # ON DELETE CASCADE on document_chunks.document_id (see
    # app/models/document_chunk.py) — no manual cleanup needed here.
    # Conversations/sources will need the same treatment once those
    # tables exist in Phases 5/7.
    db.delete(document)
    db.commit()
