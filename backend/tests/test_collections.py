"""
test_collections.py

Covers collection CRUD plus the two behaviors most likely to be gotten
wrong: user isolation (can't see/delete someone else's collection) and
the "delete unassigns documents rather than deleting them" behavior.
"""


def test_create_and_list_collection(auth_client):
    client, headers, _ = auth_client

    create_response = client.post(
        "/api/collections", json={"name": "College", "description": "DSA, DBMS, OS"}, headers=headers
    )
    assert create_response.status_code == 201
    body = create_response.json()
    assert body["name"] == "College"
    assert body["document_count"] == 0

    list_response = client.get("/api/collections", headers=headers)
    assert list_response.status_code == 200
    names = [c["name"] for c in list_response.json()]
    assert "College" in names


def test_collections_require_authentication(client):
    response = client.get("/api/collections")
    assert response.status_code == 401


def test_cannot_delete_another_users_collection(auth_client, client, cleanup_users):
    import uuid

    owner_client, owner_headers, _ = auth_client
    create_response = owner_client.post(
        "/api/collections", json={"name": "Private"}, headers=owner_headers
    )
    collection_id = create_response.json()["id"]

    other_email = f"test-{uuid.uuid4().hex[:8]}-other@example.com"
    cleanup_users.append(other_email)
    other_register = client.post(
        "/api/auth/register",
        json={"name": "Other User", "email": other_email, "password": "supersecret123"},
    )
    other_headers = {"Authorization": f"Bearer {other_register.json()['access_token']}"}

    delete_response = client.delete(f"/api/collections/{collection_id}", headers=other_headers)
    assert delete_response.status_code == 404


def test_delete_collection_unassigns_documents_without_deleting_them(auth_client):
    client, headers, _ = auth_client

    collection_id = client.post(
        "/api/collections", json={"name": "Temp Folder"}, headers=headers
    ).json()["id"]

    upload_response = client.post(
        "/api/documents/upload",
        params={"collection_id": collection_id},
        files={"file": ("notes.txt", b"Rahul's CGPA is 8.4.", "text/plain")},
        headers=headers,
    )
    document_id = upload_response.json()["id"]
    assert upload_response.json()["collection_id"] == collection_id

    delete_response = client.delete(f"/api/collections/{collection_id}", headers=headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/documents/{document_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["collection_id"] is None
