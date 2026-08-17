"""
collections.py (api)

CRUD for collections (spec section 17). Every route requires
authentication and every query is scoped to `current_user.id` — this is
the pattern every future user-owned resource in this project follows for
the "a user must never access another user's data" requirement (spec
section 14).
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.collection import Collection
from app.models.document import Document
from app.models.user import User
from app.schemas.collection import CollectionCreate, CollectionResponse

router = APIRouter(prefix="/collections", tags=["collections"])


def _get_owned_collection_or_404(db: Session, collection_id: uuid.UUID, user: User) -> Collection:
    collection = (
        db.query(Collection)
        .filter(Collection.id == collection_id, Collection.user_id == user.id)
        .first()
    )
    if collection is None:
        # 404, not 403 — we don't want to confirm to a user that a
        # collection with this id exists but belongs to someone else.
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Collection not found.")
    return collection


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(
    payload: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    collection = Collection(user_id=current_user.id, name=payload.name, description=payload.description)
    db.add(collection)
    db.commit()
    db.refresh(collection)

    response = CollectionResponse.model_validate(collection)
    response.document_count = 0
    return response


@router.get("", response_model=list[CollectionResponse])
def list_collections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Collection, func.count(Document.id))
        .outerjoin(Document, Document.collection_id == Collection.id)
        .filter(Collection.user_id == current_user.id)
        .group_by(Collection.id)
        .order_by(Collection.created_at.desc())
        .all()
    )

    results = []
    for collection, doc_count in rows:
        response = CollectionResponse.model_validate(collection)
        response.document_count = doc_count
        results.append(response)
    return results


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    collection = _get_owned_collection_or_404(db, collection_id, current_user)

    # Unassign (not delete) any documents in this collection — losing a
    # folder shouldn't destroy the files that were organized under it.
    db.query(Document).filter(Document.collection_id == collection.id).update(
        {Document.collection_id: None}
    )
    db.delete(collection)
    db.commit()
