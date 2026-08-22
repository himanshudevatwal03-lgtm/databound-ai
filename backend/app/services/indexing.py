"""
indexing.py

Ties chunking (app/services/chunking.py) and embedding
(app/services/embeddings.py) together into the one operation the rest of
the app calls: "make this document's content searchable." Kept as its
own service, separate from both, so re-indexing (e.g. after a future
"reprocess this document" feature, or a provider change) is a single
function call rather than duplicated logic.

Deliberately synchronous, same tradeoff as Phase 3's upload processing —
fine for the local embedding provider (no network call) and typical
document sizes; a background job queue is the right upgrade once large
documents or the OpenAI provider make this slow. Noted in the README.
"""

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.chunking import chunk_extracted_content
from app.services.embeddings import get_embedding_provider


def index_document(db: Session, document: Document) -> int:
    """
    Chunks and embeds `document.extracted_content`, storing the results
    as DocumentChunk rows. Returns the number of chunks created. Any
    existing chunks for this document are cleared first, so this is safe
    to call again (e.g. for re-indexing) without creating duplicates.
    """
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()

    chunks = chunk_extracted_content(document.extracted_content or {})
    if not chunks:
        db.commit()
        return 0

    provider = get_embedding_provider()
    texts = [c["text"] for c in chunks]
    embeddings = provider.embed_texts(texts)

    for chunk, embedding in zip(chunks, embeddings):
        db.add(
            DocumentChunk(
                document_id=document.id,
                user_id=document.user_id,
                chunk_index=chunk["chunk_index"],
                text=chunk["text"],
                page_number=chunk["page_number"],
                row_number=chunk["row_number"],
                embedding=embedding,
            )
        )

    db.commit()
    return len(chunks)
