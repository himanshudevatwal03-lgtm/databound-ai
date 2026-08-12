# DataBound AI

> A data-grounded question-answering platform that answers ONLY from user-provided information with verifiable sources.

## 🎯 Problem Statement

Users have documents and want to ask questions about them. Traditional search is keyword-based and limited. General AI assistants hallucinate and make up information.

**DataBound AI** solves this by:
- Extracting and indexing user data
- Retrieving relevant information using semantic search
- Generating answers ONLY from retrieved data
- Validating answers against sources
- Showing exact sources and evidence
- Providing knowledge-gap detection

## ✨ Core Features

### Phase 1 - Foundation ✅
- [x] Project structure
- [x] FastAPI backend
- [x] React frontend
- [x] PostgreSQL + pgvector
- [x] Docker setup
- [x] Health checks

### Phase 2 - Authentication
- [ ] User registration
- [ ] Login/logout
- [ ] JWT authentication
- [ ] User isolation

### Phase 3 - Document Management
- [ ] TXT/PDF/CSV upload
- [ ] Document processing
- [ ] Collections/folders
- [ ] Document deletion

### Phase 4 - Retrieval System
- [ ] Text chunking
- [ ] Embedding generation
- [ ] Vector search
- [ ] Relevance ranking

### Phase 5 - Core QA
- [ ] Question answering API
- [ ] Source citations
- [ ] Grounded context

### Phase 6 - Anti-Hallucination
- [ ] Relevance threshold
- [ ] Answer validation
- [ ] Hallucination tests

### Phase 7 - Chat Interface
- [ ] Conversations
- [ ] Chat history
- [ ] Follow-up questions

### Phase 8 - Knowledge Features
- [ ] Save answers
- [ ] Personal notes
- [ ] Bookmarks
- [ ] Tags
- [ ] Note search
- [ ] Export

### Phase 9+ - Advanced Features
- [ ] Document summaries
- [ ] Multi-document comparison
- [ ] Study mode
- [ ] Flashcards
- [ ] Knowledge gap detection
- [ ] Unanswered question analytics

## 🏗️ Architecture

```
User
  ↓
React Frontend (Vite)
  ↓
FastAPI Backend
  ↓
┌─────────────────────────────────┐
│ Document Service                │
│  • Upload TXT/PDF/CSV           │
│  • Extract text                 │
│  • Chunk text                   │
│  • Generate embeddings          │
└─────────────────────────────────┘
  ↓
PostgreSQL + pgvector
  ↓
┌─────────────────────────────────┐
│ QA Service                      │
│  • Retrieve relevant chunks     │
│  • Check relevance threshold    │
│  • Generate grounded answer     │
│  • Validate against context     │
│  • Return sources               │
└─────────────────────────────────┘
  ↓
User sees answer + sources
```

## 🛡️ Anti-Hallucination Strategy

### Layer 1: Retrieval Threshold
If no relevant data found → "Information not found"

### Layer 2: Strict Prompting
LLM receives only relevant context with clear instructions not to hallucinate

### Layer 3: Answer Validation
Generated answer validated against retrieved context

### Layer 4: Source Requirement
Every factual claim must have a source

## 🚀 Tech Stack

**Frontend:**
- React 18
- Vite
- Axios
- React Router

**Backend:**
- Python 3.11
- FastAPI
- Pydantic
- SQLAlchemy

**Database:**
- PostgreSQL 16
- pgvector

**AI:**
- OpenAI (LLM + embeddings)
- Pluggable providers

**Deployment:**
- Docker
- Docker Compose

## 📁 Project Structure

```
databound-ai/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── context/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   ├── services/
│   │   ├── core/
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- (Or: Python 3.11, Node.js 18+, PostgreSQL 16)

### Using Docker

1. **Clone the repository:**
```bash
git clone https://github.com/himanshudevatwal03-lgtm/databound-ai.git
cd databound-ai
```

2. **Create `.env` from example:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Build and run:**
```bash
docker compose up --build
```

4. **Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Database:**
```bash
# Using Docker
docker run --name postgres -e POSTGRES_PASSWORD=databound -e POSTGRES_USER=databound -e POSTGRES_DB=databound_db -p 5432:5432 pgvector/pgvector:pg16-latest

# Or install PostgreSQL locally with pgvector extension
```

## 📚 Database Schema

Key tables:
- `users` - User accounts
- `collections` - Document folders
- `documents` - Uploaded files
- `document_chunks` - Text chunks with embeddings
- `conversations` - Chat sessions
- `questions` - User questions
- `answers` - AI answers
- `sources` - Answer sources
- `notes` - User's personal notes
- `bookmarks` - Bookmarked questions
- `tags` - User tags

## 🔌 API Endpoints

```
AUTH:
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout

DOCUMENTS:
POST   /api/documents/upload
GET    /api/documents
GET    /api/documents/{id}
DELETE /api/documents/{id}

QUESTIONS:
POST   /api/questions
GET    /api/conversations/{id}

ANSWERS:
POST   /api/answers/{id}/save
GET    /api/answers

NOTES:
POST   /api/notes
GET    /api/notes
PUT    /api/notes/{id}
DELETE /api/notes/{id}

BOOKMARKS:
POST   /api/bookmarks
GET    /api/bookmarks
DELETE /api/bookmarks/{id}
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🔐 Security

- ✅ Passwords hashed with bcrypt
- ✅ JWT authentication
- ✅ User data isolation
- ✅ File validation
- ✅ API key in environment variables
- ✅ CORS configured
- ✅ Input validation with Pydantic

## 📖 Key Concepts Explained

### Embeddings
Embeddings convert text into numerical vectors that capture semantic meaning. Similar texts have similar embeddings, enabling semantic search.

### pgvector
PostgreSQL extension that stores and searches vectors efficiently using similarity operations.

### RAG (Retrieval-Augmented Generation)
1. Retrieve relevant documents
2. Augment prompt with retrieved content
3. Generate answer using augmented context

This prevents hallucination because LLM only sees relevant data.

### Anti-Hallucination
Multiple safeguards prevent AI from making up information:
- Relevance threshold (don't answer if data not found)
- Strict system prompt (don't use general knowledge)
- Answer validation (verify answer against context)
- Source requirement (cite everything)

## 🔮 Future Improvements

- [ ] Support DOCX, XLSX, images with OCR
- [ ] Multi-language support
- [ ] Real-time collaboration
- [ ] Document versioning
- [ ] Advanced analytics
- [ ] Custom LLM fine-tuning
- [ ] Graph-based knowledge representation
- [ ] Advanced privacy modes

## 📝 License

MIT

## 👤 Author

Himanshu Devatwal

---

**Last Updated:** Phase 1 - Foundation
