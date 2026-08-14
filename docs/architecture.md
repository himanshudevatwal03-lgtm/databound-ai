# Architecture

## Request flow (target, once all phases are complete)

```text
User
 |
 v
Frontend (React)
 |
 v
FastAPI
 |
 v
Document processing (validate -> extract -> normalize -> chunk)
 |
 v
Embeddings (chunk text -> vector)
 |
 v
PostgreSQL + pgvector (store + similarity search)
 |
 v
Retrieval (top-K relevant chunks for a question)
 |
 v
LLM (answers using ONLY the retrieved chunks)
 |
 v
Validation (is the answer actually supported by the context?)
 |
 v
Answer + source citations shown to the user
```

## Why retrieval and validation are both necessary

Retrieval alone isn't enough: an LLM given *some* context will often still
try to be "helpful" by filling gaps with general knowledge if the context
is thin. Validation alone isn't enough either: by the time you're
validating, the LLM has already generated an answer, and a validator can
miss subtle fabrications if it isn't checking specific claims against
specific source text.

Together, they form two independent checkpoints:

- **Retrieval threshold (before generation)** stops the LLM from even
  attempting an answer when there's no relevant data at all — the
  cheapest and most reliable way to avoid hallucination.
- **Answer validation (after generation)** catches the harder case: there
  *was* some relevant context, but the LLM still asserted something the
  context doesn't actually support (e.g. combining two unrelated facts
  into a false inference).

## Target database schema

Implemented incrementally — `users` arrives in Phase 2, `documents` /
`document_chunks` in Phases 3–4, and so on. Full target design:

```text
users(id, name, email, password_hash, created_at)

collections(id, user_id, name, description, created_at)

documents(id, user_id, collection_id, filename, file_type, file_size,
          version, status, created_at, updated_at)

document_chunks(id, document_id, chunk_index, text, page_number,
                 row_number, embedding, created_at)

conversations(id, user_id, document_id, collection_id, title,
              created_at, updated_at)

questions(id, conversation_id, question, created_at)

answers(id, question_id, answer, supported, created_at)

sources(id, answer_id, document_id, chunk_id, source_text, page_number,
        row_number)

notes(id, user_id, answer_id, title, content, created_at, updated_at)

bookmarks(id, user_id, question_id, answer_id, created_at)

tags(id, user_id, name)

note_tags(note_id, tag_id)

unanswered_questions(id, user_id, question, checked_at)

flashcards(id, user_id, document_id, question, answer, source, created_at)

document_versions(id, document_id, version, created_at)
```

## Target API surface

Beyond Phase 1's `/` and `/api/health`, later phases add:

```text
POST   /api/auth/register
POST   /api/auth/login

POST   /api/documents/upload
GET    /api/documents
GET    /api/documents/{id}
DELETE /api/documents/{id}

POST   /api/questions
GET    /api/conversations
GET    /api/conversations/{id}

POST   /api/answers/{id}/save
DELETE /api/answers/{id}/save

POST   /api/notes
GET    /api/notes
PUT    /api/notes/{id}
DELETE /api/notes/{id}

POST   /api/bookmarks
GET    /api/bookmarks
DELETE /api/bookmarks/{id}

POST   /api/documents/{id}/summary
POST   /api/documents/compare
POST   /api/questions/generate
GET    /api/knowledge-gaps
POST   /api/study/generate
POST   /api/flashcards
GET    /api/flashcards
POST   /api/study/evaluate
```

## Key concepts, explained

**FastAPI** — a Python web framework for building APIs. We use it because
it generates interactive docs (`/docs`) automatically from our Python type
hints and Pydantic models, and it's async-friendly, which matters once
we're calling an LLM API and waiting on network I/O.

**REST API** — a convention for structuring web APIs around resources
(`/documents`, `/notes`) and standard HTTP verbs (GET to read, POST to
create, DELETE to remove). It keeps the API predictable as it grows.

**PostgreSQL** — a relational database. We chose it over a NoSQL store
because DataBound AI's data is inherently relational (a user has many
documents, a document has many chunks, an answer has many sources) — the
foreign-key relationships are the point, not a complication to route
around.

**pgvector** — a PostgreSQL extension that adds a `vector` column type and
similarity-search operators. Instead of running a separate vector
database, we store embeddings directly alongside the relational data they
belong to, which keeps a chunk's text, metadata, and embedding in one row.

**Embeddings** — a numerical representation of text such that similar
meanings produce similar vectors. This is what makes "semantic" search
possible: a question about "pay" can match a chunk that says "salary"
even though the words differ.

**Semantic search** — searching by meaning (via embedding similarity)
instead of exact keyword matches. It's what powers retrieval: given a
question's embedding, find the document chunks whose embeddings are
closest to it.

**RAG (Retrieval-Augmented Generation)** — the overall pattern this app
implements: instead of asking an LLM to answer from its training data,
you *retrieve* relevant material first and feed only that to the LLM as
context. It's what makes grounding possible.

**Retrieval** — the step where a question is turned into an embedding,
compared against stored chunk embeddings, and the top-K most similar
chunks are returned.

**Grounding** — ensuring an answer is actually anchored in retrieved
source material, not the model's general knowledge. Every claim should be
traceable back to specific text.

**Answer validation** — a post-generation check: does the retrieved
context actually support what the model just said? If not, the answer is
discarded in favor of "not enough information."

**Authentication** — verifying who a user is (login) and what they're
allowed to access (authorization), so User A can never see User B's
documents or notes.

**Docker** — packages the app (code + dependencies + runtime) into
portable containers, so "works on my machine" becomes "works anywhere
Docker runs." Docker Compose lets us define and run the frontend,
backend, and database together with one command.
