"""
test_qa.py

Tests the full QA pipeline (app/services/qa.py + POST /api/questions)
with the LLM provider mocked out — these tests need to be deterministic
and runnable without a real Anthropic API key, so app.services.qa's
get_llm_provider is monkeypatched to a FakeLLMProvider that returns a
scripted response and records exactly what prompt it was called with.

This still exercises everything that matters: Layer 1's relevance
threshold correctly skipping the LLM call entirely when nothing relevant
is found, the grounded context actually containing the relevant chunk's
text, ownership/auth checks, and the unconfigured-API-key path returning
a clear 503 rather than a raw error.
"""

import pytest


class FakeLLMProvider:
    """Records the last call's prompts and returns a scripted answer."""

    def __init__(self, response_text="Rahul's CGPA is 8.4."):
        self.response_text = response_text
        self.last_system_prompt = None
        self.last_user_message = None
        self.call_count = 0

    def generate(self, system_prompt, user_message):
        self.call_count += 1
        self.last_system_prompt = system_prompt
        self.last_user_message = user_message
        return self.response_text


@pytest.fixture
def fake_llm(monkeypatch):
    fake = FakeLLMProvider()
    monkeypatch.setattr("app.services.qa.get_llm_provider", lambda: fake)
    return fake


def test_question_with_relevant_data_returns_grounded_answer(auth_client, fake_llm):
    client, headers, _ = auth_client

    client.post(
        "/api/documents/upload",
        files={"file": ("student.txt", b"Rahul's CGPA is 8.4.", "text/plain")},
        headers=headers,
    )

    response = client.post(
        "/api/questions", json={"question": "What is Rahul's CGPA?"}, headers=headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Rahul's CGPA is 8.4."
    assert body["supported"] is True
    assert len(body["sources"]) >= 1
    assert body["sources"][0]["filename"] == "student.txt"
    assert fake_llm.call_count == 1


def test_question_with_no_relevant_data_skips_llm_entirely(auth_client, fake_llm):
    client, headers, _ = auth_client

    client.post(
        "/api/documents/upload",
        files={"file": ("company.txt", b"The company was founded in 2015 in Bengaluru.", "text/plain")},
        headers=headers,
    )

    response = client.post(
        "/api/questions",
        json={"question": "What is the airspeed velocity of an unladen swallow?"},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["supported"] is False
    assert body["sources"] == []
    assert "does not contain sufficient information" in body["answer"]
    # The whole point of Layer 1: no relevant chunks means we never even
    # ask the LLM.
    assert fake_llm.call_count == 0


def test_grounded_context_contains_relevant_chunk_text(auth_client, fake_llm):
    client, headers, _ = auth_client

    client.post(
        "/api/documents/upload",
        files={"file": ("student.txt", b"Rahul's CGPA is 8.4.", "text/plain")},
        headers=headers,
    )

    client.post("/api/questions", json={"question": "What is Rahul's CGPA?"}, headers=headers)

    assert "Rahul's CGPA is 8.4." in fake_llm.last_user_message
    assert "student.txt" in fake_llm.last_user_message
    assert "What is Rahul's CGPA?" in fake_llm.last_user_message
    # Layer 2's strict grounding instructions must actually be present.
    assert "ONLY" in fake_llm.last_system_prompt
    assert "does not contain sufficient information" in fake_llm.last_system_prompt


def test_model_declining_verbatim_marks_answer_unsupported(auth_client, monkeypatch):
    """
    If the LLM itself follows instructions and replies with the exact
    "not enough information" sentence (because the retrieved chunk was
    topically related but didn't actually answer the question), the API
    should report supported=False with no sources — not treat it as a
    normal supported answer just because retrieval found something.
    """
    client, headers, _ = auth_client

    fake = FakeLLMProvider(
        response_text="The provided data does not contain sufficient information to answer this question."
    )
    monkeypatch.setattr("app.services.qa.get_llm_provider", lambda: fake)

    client.post(
        "/api/documents/upload",
        files={"file": ("student.txt", b"Rahul's CGPA is 8.4.", "text/plain")},
        headers=headers,
    )

    response = client.post(
        "/api/questions", json={"question": "What is Rahul's father's name?"}, headers=headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["supported"] is False
    assert body["sources"] == []


def test_answer_style_short_adjusts_system_prompt(auth_client, fake_llm):
    client, headers, _ = auth_client

    client.post(
        "/api/documents/upload",
        files={"file": ("student.txt", b"Rahul's CGPA is 8.4.", "text/plain")},
        headers=headers,
    )

    client.post(
        "/api/questions",
        json={"question": "What is Rahul's CGPA?", "answer_style": "short"},
        headers=headers,
    )

    assert "one sentence" in fake_llm.last_system_prompt


def test_question_requires_authentication(client):
    response = client.post("/api/questions", json={"question": "anything"})
    assert response.status_code == 401


def test_question_rejects_empty_string(auth_client, fake_llm):
    client, headers, _ = auth_client
    response = client.post("/api/questions", json={"question": ""}, headers=headers)
    assert response.status_code == 422


def test_question_scoped_to_unowned_document_returns_404(auth_client, client, cleanup_users):
    import uuid

    owner_client, owner_headers, _ = auth_client
    upload_response = owner_client.post(
        "/api/documents/upload",
        files={"file": ("mine.txt", b"Some private content.", "text/plain")},
        headers=owner_headers,
    )
    document_id = upload_response.json()["id"]

    other_email = f"test-{uuid.uuid4().hex[:8]}-qa@example.com"
    cleanup_users.append(other_email)
    other_register = client.post(
        "/api/auth/register",
        json={"name": "Other QA User", "email": other_email, "password": "supersecret123"},
    )
    other_headers = {"Authorization": f"Bearer {other_register.json()['access_token']}"}

    response = client.post(
        "/api/questions",
        json={"question": "anything", "document_id": document_id},
        headers=other_headers,
    )
    assert response.status_code == 404


def test_question_without_llm_configured_returns_503(auth_client):
    """
    No monkeypatch here — exercises the real get_llm_provider(), which
    should raise LLMNotConfiguredError since the test environment has no
    LLM_API_KEY set, and the API should turn that into a 503, not a crash.
    """
    client, headers, _ = auth_client

    client.post(
        "/api/documents/upload",
        files={"file": ("student.txt", b"Rahul's CGPA is 8.4.", "text/plain")},
        headers=headers,
    )

    response = client.post(
        "/api/questions", json={"question": "What is Rahul's CGPA?"}, headers=headers
    )

    assert response.status_code == 503
