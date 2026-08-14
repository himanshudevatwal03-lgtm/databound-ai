# DataBound AI

**A personal data-grounded AI assistant that answers only from user-provided
information, provides verifiable sources, saves useful answers/notes,
identifies knowledge gaps, and provides study/knowledge-management
features.**

This is not "chat with a PDF." The core guarantee of the product is:

> If the answer isn't in your data, the system tells you so — it never
> guesses, infers, or fills in gaps with outside knowledge.

---

## Status: Phase 1 — Project Foundation ✅

This repository is being built in phases (see [Development Roadmap](#development-roadmap)
below). Phase 1 sets up the skeleton: FastAPI backend, React frontend,
PostgreSQL, Docker Compose, and a working health check proving the whole
stack talks to itself correctly. No auth, uploads, or AI features exist
yet — those arrive in Phases 2 onward.

## Problem Statement

General-purpose AI chat tools answer confidently even when they don't
actually know something, because they're drawing on broad training data
instead of a specific, verifiable source. That's a serious problem for
anyone using AI answers to make decisions, study, or reference facts:
there's no way to tell a correct answer from a plausible-sounding
fabrication.

## Motivation

DataBound AI flips the default: instead of "answer from everything I was
trained on," it's "answer only from what you gave me, and show your
work." That makes it trustworthy for exactly the situations where
hallucination is most costly — studying from your own notes, reviewing a
contract, or querying a dataset — because every claim can be traced back
to a specific document, page, or row.

## Core Features (target — see roadmap for what's built so far)

- Upload TXT / PDF / CSV documents, organized into collections
- Ask natural-language questions, answered only from retrieved chunks of
  your own documents
- Every answer ships with source citations (filename, page/row, quoted
  text) or an explicit "not enough information" response
- Save answers, attach personal notes, bookmark and tag questions
- Search your own saved notes
- Document summaries, multi-document questions, and document comparison
- Knowledge-gap detection and unanswered-question analytics
- Study mode: generated questions, flashcards, and answer evaluation —
  all grounded in your uploaded material
- Document versioning and version comparison
- Privacy controls and clean document deletion

## Architecture

```text
                     USER
                       |
                       v
                 React Frontend
                       |
                       v
                  FastAPI API
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
 Document Service   QA Service     Notes Service
        |              |              |
        v              v              v
 Data Processing   Retrieval      PostgreSQL
        |
        v
 Chunking -> Embeddings -> PostgreSQL + pgvector
        |
        v
 Relevant Context -> LLM -> Answer Validator -> Grounded Answer + Sources
```

## Anti-Hallucination Strategy

Three layers protect against fabricated answers:

1. **Retrieval threshold** — if nothing relevant enough is found in your
   documents, the system returns "not enough information" without ever
   asking the LLM to answer.
2. **Strict system prompt** — the LLM is explicitly instructed to use only
   the provided context, never general knowledge, and to say so when the
   context is insufficient.
3. **Answer validation** — after generation, the answer is checked against
   the retrieved context. If it isn't actually supported, it's replaced
   with the standard "not enough information" response before it ever
   reaches the user.

These layers are implemented starting in Phase 5/6 — see the roadmap.

## Technology Stack

| Layer        | Choice                                   |
|--------------|-------------------------------------------|
| Frontend     | React + Vite (JavaScript)                |
| Backend      | Python + FastAPI                          |
| Database     | PostgreSQL                                |
| Vector search| PostgreSQL + pgvector                     |
| AI / LLM     | Provider-agnostic service interface       |
| Embeddings   | Configurable embedding service            |
| Deployment   | Docker + Docker Compose                   |

The AI and embedding layers are built behind an abstraction so the actual
provider/model can change without touching the rest of the app.

## Database Design

See the full schema plan in [`docs/architecture.md`](docs/architecture.md).
Tables are added incrementally as each phase needs them (e.g. `users` in
Phase 2, `documents`/`document_chunks` in Phases 3–4, `notes`/`bookmarks`/
`tags` in Phase 8).

## Folder Structure

```text
databound-ai/
├── frontend/
│   ├── src/
│   │   ├── components/   # Navbar, LoadingSpinner, ErrorMessage, ...
│   │   ├── pages/         # Dashboard, ...
│   │   ├── services/      # api.js — all backend calls live here
│   │   ├── hooks/
│   │   ├── context/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI app + router registration
│   │   ├── config.py       # environment-driven settings
│   │   ├── database/       # SQLAlchemy engine/session
│   │   ├── models/         # ORM models (added from Phase 2 onward)
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── api/            # route modules (health.py so far)
│   │   ├── services/       # business logic (added per phase)
│   │   ├── core/           # security, auth helpers (Phase 2+)
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── sample_data/            # TXT samples now; CSV/PDF added in Phase 3
├── docs/
│   └── architecture.md
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Installation & Running Locally

### Option A — Docker Compose (recommended)

```bash
git clone <your-repo-url>
cd databound-ai
cp .env.example .env
docker compose up --build
```

Then open:

- Frontend: http://localhost:5173
- Backend docs (Swagger UI): http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

The Dashboard page calls the health endpoint on load and shows whether the
API and database are reachable.

### Option B — Running services individually

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env   # then edit DATABASE_URL if not using Docker's Postgres
uvicorn app.main:app --reload
```

You'll need a running PostgreSQL instance reachable at whatever
`DATABASE_URL` you set. The easiest way is still:

```bash
docker compose up postgres
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## Deployment (Render)

The repo includes [`render.yaml`](render.yaml), a Blueprint that provisions
all three pieces together: managed Postgres, the FastAPI backend (as a
Docker web service), and the React frontend (as a static site).

**1. Push this repo to GitHub** (if you haven't already):

```bash
cd databound-ai
git init
git add .
git commit -m "Phase 1: project foundation"
git branch -M main
git remote add origin https://github.com/<your-username>/databound-ai.git
git push -u origin main
```

**2. Create the Blueprint on Render:**

- Go to the Render dashboard → **New** → **Blueprint**
- Connect your GitHub account and select the `databound-ai` repo
- Render reads `render.yaml` and shows you three resources to create:
  `databound-postgres`, `databound-backend`, `databound-frontend`
- Click **Apply**

**3. Fix up the two URLs that only exist after the first deploy:**

Render assigns each service a URL like `https://databound-backend-xxxx.onrender.com`
(the `xxxx` suffix is only known after creation, so `render.yaml` can't
predict it exactly). Once both services have deployed once:

- Open **databound-backend → Environment**, set `CORS_ORIGINS` to your
  actual frontend URL (e.g. `https://databound-frontend-xxxx.onrender.com`)
- Open **databound-frontend → Environment**, set `VITE_API_BASE_URL` to
  your actual backend URL (e.g. `https://databound-backend-xxxx.onrender.com`)
- Because `VITE_API_BASE_URL` is baked in at build time, trigger a
  **Manual Deploy → Clear build cache & deploy** on the frontend after
  changing it — a plain redeploy without clearing cache won't pick it up.

**4. Verify:**

- Backend health check: `https://<your-backend-url>/api/health` → should
  show `"database": "connected"`
- Frontend: open the frontend URL → the dashboard's status card should
  show API running / Database connected

**Notes on Render's free tier:** free web services spin down after 15
minutes of inactivity and take ~30–60s to wake back up on the next
request — the first `/api/health` call after idle time will be slow, not
broken. Free Postgres databases also expire after 90 days unless upgraded.

**Secrets:** `LLM_API_KEY` is marked `sync: false` in `render.yaml`, so
Render will prompt you to enter it manually in the dashboard rather than
storing it in the repo — you won't need this until Phase 5, but it's wired
up now so the env var name is stable.

## Environment Variables

See [`.env.example`](.env.example) for the full list with descriptions.
Key ones for Phase 1:

| Variable        | Purpose                                      |
|-----------------|-----------------------------------------------|
| `DATABASE_URL`  | PostgreSQL connection string                  |
| `JWT_SECRET`    | Signing secret for auth tokens (Phase 2+)     |
| `LLM_API_KEY`   | Provider API key for the LLM (Phase 5+)       |
| `VITE_API_BASE_URL` | Backend URL the frontend calls          |

## API Documentation (Phase 1)

| Method | Path          | Description                                  |
|--------|---------------|-----------------------------------------------|
| GET    | `/`           | API root — confirms the service is up         |
| GET    | `/api/health` | Health check; also confirms DB connectivity   |

Full interactive docs are always available at `/docs` (Swagger) while the
backend is running. Later phases add auth, document, question, note,
bookmark, summary, comparison, and study endpoints — the full target list
is in [`docs/architecture.md`](docs/architecture.md).

## Testing

```bash
cd backend
pytest
```

Phase 1 includes a smoke test for `/` and `/api/health`. Every later phase
adds tests under `backend/tests/`, including — critically — explicit
hallucination tests once question-answering exists (Phase 6).

## Development Roadmap

- [x] **Phase 1 — Project Foundation** (this state): structure, FastAPI,
      React, PostgreSQL, Docker, health check, basic frontend
- [ ] Phase 2 — Authentication
- [ ] Phase 3 — Document Management (upload, TXT/PDF/CSV, collections)
- [ ] Phase 4 — Retrieval (chunking, embeddings, pgvector)
- [ ] Phase 5 — Core Question Answering
- [ ] Phase 6 — Anti-Hallucination (validation + hallucination tests)
- [ ] Phase 7 — Chat (conversations, follow-ups)
- [ ] Phase 8 — Personal Knowledge Features (notes, bookmarks, tags, export)
- [ ] Phase 9 — Advanced Data Features (summaries, comparison)
- [ ] Phase 10 — Knowledge Features (knowledge gaps, study mode, flashcards)
- [ ] Phase 11 — UI Polish
- [ ] Phase 12 — Testing
- [ ] Phase 13 — Docker & Deployment hardening
- [ ] Phase 14 — Documentation

## Limitations (current, Phase 1)

- No authentication yet — there is no concept of a "user" in the database.
- No document upload or AI features yet — this phase only proves the
  frontend, backend, and database can talk to each other.
- `pgvector` extension is available in the Postgres image but not yet used
  by any table (arrives in Phase 4).

## Future Improvements

Tracked implicitly by the roadmap above — every unchecked phase is a
planned improvement, not a maybe.
