"""
test_documents.py

Covers upload + extraction for all three supported file types, plus every
validation/error case called out in the spec: unsupported extension,
empty file, oversized file, malformed CSV, and an unreadable/corrupted
PDF. Also covers listing, retrieval, deletion, and user isolation.
"""

import io

import pytest


def _make_minimal_pdf() -> bytes:
    """
    Builds the smallest valid single-page PDF containing the text
    "Hello DataBound" — by hand, rather than depending on a PDF-writing
    library, so this test file has no extra runtime dependencies. The
    structure is deliberately minimal but spec-valid: a catalog, one page,
    and a content stream that draws one line of text.
    """
    content_stream = b"BT /F1 24 Tf 72 712 Td (Hello DataBound) Tj ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> "
        b"/MediaBox [0 0 612 792] /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content_stream), content_stream),
    ]

    buf = io.BytesIO()
    buf.write(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(buf.tell())
        buf.write(b"%d 0 obj\n%s\nendobj\n" % (i, obj))

    xref_offset = buf.tell()
    buf.write(b"xref\n0 %d\n" % (len(objects) + 1))
    buf.write(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        buf.write(b"%010d 00000 n \n" % off)
    buf.write(b"trailer\n<< /Size %d /Root 1 0 R >>\n" % (len(objects) + 1))
    buf.write(b"startxref\n%d\n%%%%EOF" % xref_offset)
    return buf.getvalue()


def test_upload_txt_extracts_and_stores_text(auth_client):
    client, headers, _ = auth_client

    response = client.post(
        "/api/documents/upload",
        files={"file": ("student.txt", b"Rahul's CGPA is 8.4.", "text/plain")},
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ready"
    assert body["file_type"] == "txt"
    assert "CGPA" in body["preview"]


def test_upload_csv_extracts_rows(auth_client):
    client, headers, _ = auth_client

    csv_bytes = b"name,department,salary\nRahul,Engineering,55000\nPriya,Finance,60000\n"
    response = client.post(
        "/api/documents/upload",
        files={"file": ("employees.csv", csv_bytes, "text/csv")},
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ready"
    assert body["file_type"] == "csv"
    assert "row(s)" in body["preview"]


def test_upload_malformed_csv_marks_document_failed(auth_client):
    client, headers, _ = auth_client

    # Header row only, no data rows at all — should fail extraction
    # cleanly rather than silently succeeding with zero usable rows.
    response = client.post(
        "/api/documents/upload",
        files={"file": ("empty_data.csv", b"name,department,salary\n", "text/csv")},
        headers=headers,
    )

    assert response.status_code == 201  # upload itself is accepted
    body = response.json()
    assert body["status"] == "failed"
    assert "no data rows" in body["processing_error"]


def test_upload_valid_pdf_extracts_page_text(auth_client):
    client, headers, _ = auth_client

    response = client.post(
        "/api/documents/upload",
        files={"file": ("hello.pdf", _make_minimal_pdf(), "application/pdf")},
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ready"
    assert body["file_type"] == "pdf"
    assert "Hello DataBound" in body["preview"]


def test_upload_fake_pdf_rejected(auth_client):
    """A .pdf file that doesn't actually start with a PDF header."""
    client, headers, _ = auth_client

    response = client.post(
        "/api/documents/upload",
        files={"file": ("fake.pdf", b"this is not a real pdf", "application/pdf")},
        headers=headers,
    )

    assert response.status_code == 400
    assert "PDF header" in response.json()["detail"]


def test_upload_unsupported_extension_rejected(auth_client):
    client, headers, _ = auth_client

    response = client.post(
        "/api/documents/upload",
        files={"file": ("resume.docx", b"some bytes", "application/octet-stream")},
        headers=headers,
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_empty_file_rejected(auth_client):
    client, headers, _ = auth_client

    response = client.post(
        "/api/documents/upload",
        files={"file": ("empty.txt", b"", "text/plain")},
        headers=headers,
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_oversized_file_rejected(auth_client, monkeypatch):
    client, headers, _ = auth_client

    from app.config import settings

    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 10)  # 10 bytes, for this test only

    response = client.post(
        "/api/documents/upload",
        files={"file": ("big.txt", b"this file is definitely more than ten bytes", "text/plain")},
        headers=headers,
    )

    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()


def test_upload_requires_authentication(client):
    response = client.post(
        "/api/documents/upload",
        files={"file": ("student.txt", b"some content", "text/plain")},
    )
    assert response.status_code == 401


def test_list_documents_only_shows_own_documents(auth_client, client, cleanup_users):
    import uuid

    owner_client, owner_headers, _ = auth_client
    owner_client.post(
        "/api/documents/upload",
        files={"file": ("mine.txt", b"my private notes", "text/plain")},
        headers=owner_headers,
    )

    other_email = f"test-{uuid.uuid4().hex[:8]}-otherdocs@example.com"
    cleanup_users.append(other_email)
    other_register = client.post(
        "/api/auth/register",
        json={"name": "Other Docs User", "email": other_email, "password": "supersecret123"},
    )
    other_headers = {"Authorization": f"Bearer {other_register.json()['access_token']}"}

    other_list = client.get("/api/documents", headers=other_headers)
    assert other_list.status_code == 200
    assert other_list.json() == []  # sees none of owner's documents


def test_cannot_get_or_delete_another_users_document(auth_client, client, cleanup_users):
    import uuid

    owner_client, owner_headers, _ = auth_client
    upload_response = owner_client.post(
        "/api/documents/upload",
        files={"file": ("mine.txt", b"my private notes", "text/plain")},
        headers=owner_headers,
    )
    document_id = upload_response.json()["id"]

    other_email = f"test-{uuid.uuid4().hex[:8]}-otherdelete@example.com"
    cleanup_users.append(other_email)
    other_register = client.post(
        "/api/auth/register",
        json={"name": "Other Delete User", "email": other_email, "password": "supersecret123"},
    )
    other_headers = {"Authorization": f"Bearer {other_register.json()['access_token']}"}

    assert client.get(f"/api/documents/{document_id}", headers=other_headers).status_code == 404
    assert client.delete(f"/api/documents/{document_id}", headers=other_headers).status_code == 404


def test_delete_document(auth_client):
    client, headers, _ = auth_client

    upload_response = client.post(
        "/api/documents/upload",
        files={"file": ("temp.txt", b"delete me", "text/plain")},
        headers=headers,
    )
    document_id = upload_response.json()["id"]

    delete_response = client.delete(f"/api/documents/{document_id}", headers=headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/documents/{document_id}", headers=headers)
    assert get_response.status_code == 404


def test_upload_to_nonexistent_collection_rejected(auth_client):
    import uuid

    client, headers, _ = auth_client
    fake_collection_id = str(uuid.uuid4())

    response = client.post(
        "/api/documents/upload",
        params={"collection_id": fake_collection_id},
        files={"file": ("orphan.txt", b"content", "text/plain")},
        headers=headers,
    )
    assert response.status_code == 404
