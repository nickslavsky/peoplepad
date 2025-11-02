Goal: build a small stateless FastAPI-based HTTP wrapper around the sentence-transformers/all-mpnet-base-v2 model running through sentence-transformers. The service must be backward-compatible with existing peoplepad calls and return the exact JSON shape peoplepad expects so the backend can continue to response.json().get("data", [{}])[0].get("embedding").
Tech stack / runtime

- Python 3.12-slim
- FastAPI + Uvicorn (ASGI)
- pydantic for settings and endpoint schemas
- settings from .env file
EMBEDDING_API_KEY
MAX_WORKERS
TIMEOUT_SECONDS
MAX_INPUT_LENGTH
PEOPLEPAD_CLIENT_KEY 
MODEL_PATH
- configure for local mode / allow auto-download to mounted volume
- httpx (for client examples / tests)
- Running in Docker on Ubuntu 24.04 via docker-compose (single container, no multi-model per container)
- assume a clean machine without pre-installed model
- no commands in Dockerfile, only commands in the docker-compose snippet
- Persist downloaded model files to mounted volume (default /var/lib/<...>), fallback to auto-download mapped to same path.

Non-functional constraints

- Runs on consumer hardware (no GPU assumed). Be scrappy, simple concurrency.
- return full normalized embeddings
- no further chunking of each input/text field!
- Standard logging (timestamps to ms). No Prometheus/telemetry.
- Overnight batch processing expected; low concurrency ok.
- Each model gets its own column in Postgres on the caller; the backend will manage storage.
- Service port: Accept default 8080 
- API key comparison: use PEOPLEPAD_CLIENT_KEY. I'll refactor peoplepad code myself
- Max input length: MAX_INPUT_LENGTH from .env
- Batch memory strategy: return 413 on too-large batch and let backend retry smaller batches. 
- Model download policy: attempt auto-download to mounted MODEL_PATH
- Model dimension exposure. yes, if SDK provides it
- On batch: echo any input id. IDs should be required.
- Rate-limiting: none; small-scale prototype
- logging `logging.basicConfig(level=logging.INFO, format="%(asctime)s.%(msecs)03d %(levelname)s %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")`
## API specification (backward-compatible)
### Authentication
Use the API key via Authorization: Bearer <API_KEY> header (same header my code already sends, but on the peoplepad side will be EMBEDDING_SERVICE_KEY).
#### Single-record endpoint (primary)
POST /embed
```
{
  "input": "<text string>",
  "model": "all-mpnet-base-v2",        // must accept model param
  "encoding_format": "float"              // only "float" supported
}
```
response example
```
{
  "object": "list",
  "model": "all-mpnet-base-v2",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.0123, -0.0042, ...],  // array of floats
      "index": 0
    }
  ]
}
```
#### Batch endpoint (for population & re-embedding)
POST /embed/batch
Example Request JSON:
```
{
  "inputs": [
    {"id": "<required record UUID1>", "text": "<text>"},
    {"id": "<required record UUID2>", "text": "<text2>"}
  ],
  "model": "all-mpnet-base-v2",
  "encoding_format": "float"
}
```
Example response:
```
{
  "object": "list",
  "model": "all-mpnet-base-v2",
  "data": [
    {"id": "<same required record id1>", "object":"embedding", "embedding":[...]},
    {"id": "<same required record id2>", "object":"embedding", "embedding":[...]}
  ]
}
```
Notes:
- record ids (UUID) are used to map records and embeddings
- mapping is the client's responsibility, don't care about the order
- Batch endpoint should process sequentially or with limited concurrency (configurable) to avoid OOM on consumer hardware

#### Health & metadata
GET /health -> {"status":"ok","model":"all-mpnet-base-v2","ready": true}
GET /metadata -> returns a JSON with model name, embedding dimension (if known) and version string

### Security & request handling

- Require Authorization: Bearer <API_KEY> header. If header missing/invalid -> 401.
- Validate input length; if text is more than max from .env file (1024), return 400 with guidance. 
- Per-request timeout default 10s (match your current client code) and expose timeout in config.
- Limit request body size (e.g., 1MB) to avoid abuse.
- Logging: basic, human-readable with timestamps to ms.

### Runtime / model handling

- Use the nomic embedding SDK in local mode. Model should go to the /var/lib/models (or a better name, mounted through docker compose).
- Only all-mpnet-base-v2 for this container.
- pre-warm the model at container startup to reduce first-request latency.

### Docker + docker-compose

- Provide a small Dockerfile using python:3.12-slim
- set it up for hot reload
- copy everything you need
- in docker compose snippet Require volume mount for /var/lib/<good folder nema>
- in docker compose, specify the .env file

### Acceptance criteria:
```
# existing peoplepad client (no changes needed except key)
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8080/embed",
        headers={
            "Authorization": f"Bearer {settings.openai_key}",
            "Content-Type": "application/json"
        },
        json={
            "input": text,
            "model": settings.embedding_model,
            "encoding_format": "float"
        },
        timeout=10.0
    )
    response.raise_for_status()
    embedding = response.json().get("data", [{}])[0].get("embedding")
```
### Deliverables
fully working and runnable FastAPI project with app/ folder + Dockerfile + docker-compose.yml snippet.
Provide each file as a separate, copy-paste code block or download