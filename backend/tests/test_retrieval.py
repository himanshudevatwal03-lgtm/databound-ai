"""
test_retrieval.py

End-to-end retrieval tests through the real API: upload a document (which
triggers chunking + embedding per Phase 4's indexing step), then search
for it and check the right chunk comes back with the right source
metadata. Also covers the properties that matter for safety and
correctness: user isolation, document/collection scoping, and that
deleting a document actually removes its chunks (cascade).
"""


def test_search_finds_relevant_chunk_from_uploaded_txt(auth_client):
    client, headers, _ = auth_client

    client.post(
        "/api/documents/upload",
        files={"file": ("student.txt", b"Rahul's CGPA is 8.4. He studies Data Structures.", "text/plain")},
        headers=headers,
    )

    response = client.get("/api/retrieval/search", params={"q": "What is Rahul's CGPA?"}, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "What is Rahul's CGPA?"
    assert len(body["results"]) >= 1
    top_result = body["results"][0]
    assert "CGPA" in top_result["text"]
    assert top_result["filename"] == "student.txt"
    assert top_result["file_type"] == "txt"
    assert 0.0 <= top_result["similarity"] <= 1.0


def test_search_pdf_result_includes_page_number(auth_client):
    client, headers, _ = auth_client

    import io

    def make_minimal_pdf(text: bytes) -> bytes:
        content_stream = b"BT /F1 24 Tf 72 712 Td (%s) Tj ET" % text
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

    client.post(
        "/api/documents/upload",
        files={"file": ("deadline.pdf", make_minimal_pdf(b"Project deadline 25 August"), "application/pdf")},
        headers=headers,
    )

    response = client.get("/api/retrieval/search", params={"q": "project deadline"}, headers=headers)

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) >= 1
    assert results[0]["page_number"] == 1
    assert results[0]["row_number"] is None


def test_search_csv_result_includes_row_number(auth_client):
    client, headers, _ = auth_client

    csv_bytes = b"name,department,salary\nRahul,Engineering,55000\nPriya,Finance,60000\n"
    client.post(
        "/api/documents/upload",
        files={"file": ("employees.csv", csv_bytes, "text/csv")},
        headers=headers,
    )

    response = client.get("/api/retrieval/search", params={"q": "Priya Finance salary"}, headers=headers)

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) >= 1
    assert results[0]["row_number"] is not None
    assert results[0]["page_number"] is None


def test_search_requires_authentication(client):
    response = client.get("/api/retrieval/search", params={"q": "anything"})
    assert response.status_code == 401


def test_search_rejects_blank_query(auth_client):
    client, headers, _ = auth_client
    response = client.get("/api/retrieval/search", params={"q": "   "}, headers=headers)
    assert response.status_code == 400


def test_search_only_returns_own_documents(auth_client, client, cleanup_users):
    import uuid

    owner_client, owner_headers, _ = auth_client
    owner_client.post(
        "/api/documents/upload",
        files={"file": ("secret.txt", b"The launch codes are hidden in this sentence.", "text/plain")},
        headers=owner_headers,
    )

    other_email = f"test-{uuid.uuid4().hex[:8]}-retrieval@example.com"
    cleanup_users.append(other_email)
    other_register = client.post(
        "/api/auth/register",
        json={"name": "Other Retrieval User", "email": other_email, "password": "supersecret123"},
    )
    other_headers = {"Authorization": f"Bearer {other_register.json()['access_token']}"}

    response = client.get(
        "/api/retrieval/search", params={"q": "launch codes"}, headers=other_headers
    )
    assert response.status_code == 200
    assert response.json()["results"] == []


def test_search_scoped_to_specific_document(auth_client):
    client, headers, _ = auth_client

    doc_a = client.post(
        "/api/documents/upload",
        files={"file": ("a.txt", b"Document A discusses quarterly revenue figures.", "text/plain")},
        headers=headers,
    ).json()
    client.post(
        "/api/documents/upload",
        files={"file": ("b.txt", b"Document B discusses quarterly revenue figures too.", "text/plain")},
        headers=headers,
    )

    response = client.get(
        "/api/retrieval/search",
        params={"q": "quarterly revenue", "document_id": doc_a["id"]},
        headers=headers,
    )

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) >= 1
    assert all(r["document_id"] == doc_a["id"] for r in results)


def test_deleting_document_removes_its_chunks_from_search(auth_client):
    client, headers, _ = auth_client

    upload_response = client.post(
        "/api/documents/upload",
        files={"file": ("temp.txt", b"This unique phrase should vanish after deletion.", "text/plain")},
        headers=headers,
    )
    document_id = upload_response.json()["id"]

    before = client.get(
        "/api/retrieval/search", params={"q": "unique phrase vanish"}, headers=headers
    ).json()
    assert len(before["results"]) >= 1

    client.delete(f"/api/documents/{document_id}", headers=headers)

    after = client.get(
        "/api/retrieval/search", params={"q": "unique phrase vanish"}, headers=headers
    ).json()
    assert after["results"] == []
