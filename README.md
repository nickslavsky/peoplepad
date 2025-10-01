# PeoplePad MVP — Product & Engineering Spec

## Overview
PeoplePad is a lightweight personal knowledge app for remembering people you meet.  
The MVP is designed for private use (local deployment, a few users).

### Core Flows
- **Login** with Google OAuth  
- **Add Record** → enter *Name, Notes, and Tags*   
- **Search Records** → query with text + optional date range + tag filter  
- **View Record** → view the full record from search 
- **Edit Record** → overwrite Notes or Tags, update modified timestamp 

---

## 🎯 Finalized MVP Scope

### Users
- Google OAuth login (any Google account can log in).  
- Each user only sees their own records.  
- No roles, no social/sharing features.  

### Records 
- name, notes, tags, dates: created and modified
- edits overwrite records (no revision history)

### Search
- **Hybrid**:  
  - Vector similarity search (pgvector)  
  - Date range filter (created/updated)  
  - Tag filter (exact or prefix match)  
- Results ranked by semantic similarity.  

### Embeddings
- Computed in backend using an external service. First text-embedding-3-small then local small model. 
- Handled asynchronously with caching in front, retries + exponential backoff.  
- DB write is **not blocked** if embedding call fails (retry later).
---
## Tech & Deployment
- **Frontend**: React + TypeScript  
- **Backend**: Python, FastAPI, SQLAlchemy, Alembic
- **Database**: Postgres 17 + pgvector  
- **Infra**: docker-compose with frontend and backend, db is a separate connection string
- **Access**: local machine only (ngrok if needed)  
- **Tooling**: CI/CD + tests for both frontend and backend
---
## Backend Directory structure
- backend/
  - Dockerfile
  - requirements.txt
  - alembic.ini
  - migrations/
    - env.py
    - script.py.mako
    - versions/
      - 20250923_init.py
  - .env.example
  - app/
    - __init__.py
    - main.py
    - config.py
    - database.py
    - models/
      - __init__.py
      - user.py
      - record.py
      - tag.py
    - schemas/
      - __init__.py
      - auth.py
      - record.py
      - search.py
    - routers/
      - __init__.py
      - auth.py
      - records.py
      - search.py
      - tags.py
    - services/
      - __init__.py
      - auth.py
      - search.py
      - embedding.py
    - tasks/
      - __init__.py
      - embeddings.py
    - utils/
      - __init__.py
      - security.py
  - tests/
    - __init__.py
    - test_auth.py
    - test_records.py
    - test_search.py
    - test_embedding.py
--- 
## Data Model
### Tables
- **users**  
  - id (UUID PK)  
  - email (text, unique)  
  - created_at (timestamp with time zone, default now)  

- **records**  
  - id (UUID PK)  
  - user_id (FK → users)  
  - name (text)  
  - notes (text)  
  - embedding (vector)  
  - created_at (timestamp with time zone, default now)  
  - updated_at (timestamp with time zone, auto updated)  

- **tags**  
  - id (UUID PK)  
  - user_id (FK → users)  
  - name (text, unique per user)  

- **record_tags** (many-to-many)  
  - record_id (FK → records)  
  - tag_id (FK → tags)  
  - composite PK (record_id, tag_id)  

### Rules
- Each user only sees their own records and tags.  
- Timestamps auto-maintained.  
- pgvector extension enabled for embeddings. 
### Additional
- Enable **prefix search on tags** (GIN index with pg_trgm).  
- Enable vector similarity search (HNSW index on embeddings).  
- All database changes should be saved as versioned Alembic migrations.   
---
## API Endpoints
### Requirements
- Auth
  - /auth/login (redirects to Google OAuth)  
  - /auth/callback (handles OAuth, issues JWT/session)  
  - middleware to enforce authenticated user context  

- Records
  - POST /records → create record (name, notes, tags)  
    - Save immediately with created_at/updated_at.  
    - Launch async background task to compute embedding and update DB later.  
  - GET /records/{id} → fetch a single record  
  - PUT /records/{id} → update name/notes/tags, overwrite notes, update modified date  
  - DELETE /records/{id} → delete record  

- Search
  - POST /search → input: query string + date range + tags  
    - Backend computes query embedding  
    - Executes vector similarity search with filters (date range, tags)  
    - Returns ranked list of matching records  

### Notes
- Embedding service call must be **non-blocking**: use background worker (Celery, RQ, or FastAPI’s BackgroundTasks).  
- Retries with exponential backoff on embedding failure.  
- Include example request/response payloads for each route.  
- Keep API surface minimal but production-quality for MVP.  

---
## Embedding Workflow
Embeddings are generated via an external REST service.

### Requirements
- When a record is created or updated:  
  - Store the record immediately in Postgres (without waiting for embedding).  
  - Launch an async background job to compute embedding.  
  - Job fetches latest text (name + notes + tags) and sends HTTP POST to external embedding API.  

- Embedding service call:
  - REST endpoint: POST /embed  
  - Input: JSON { "text": "<combined content>" }  
  - Output: JSON { "embedding": [float, float, ...] }  
  - Model may have latency or transient errors.  

- Reliability:
  - Jobs should retry with exponential backoff on failures (network errors, 5xx, timeouts).  
  - Max retries configurable.  
  - Errors logged with record ID for debugging.  
  - Job queue should not block FastAPI main threads.  

- DB Update:
  - Once embedding is retrieved, update the `embedding` column in the records table.  
  - Ensure idempotency (if multiple jobs race, latest one wins).  
  - Embeddings stored as Postgres vector type.  

### Implementation guidance:
- Use FastAPI’s BackgroundTasks for very lean MVP OR integrate Celery/RQ for more robust job handling.  
- Show example code for:  
  1. Launching a background embedding job after record save.  
  2. Worker function that calls external API, retries, and updates DB.  
- Include async HTTP request (httpx or aiohttp).  
- Demonstrate retry logic (exponential backoff).

