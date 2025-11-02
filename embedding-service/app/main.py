import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sentence_transformers import SentenceTransformer, __version__
from .settings import Settings
from .schemas import EmbedRequest, BatchRequest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

settings = Settings()

try:
    model = SentenceTransformer(settings.embedding_model_name, cache_folder=settings.embedding_model_path)
    # Pre-warm the model
    model.encode("This is a warmup sentence.", normalize_embeddings=True)
except Exception as e:
    logging.error(f"Failed to load model: {e}")
    raise e

dimension = model.get_sentence_embedding_dimension()

app = FastAPI()

security = HTTPBearer()

async def authenticate(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != settings.peoplepad_client_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

@app.post("/embed")
async def embed(request: EmbedRequest, auth: bool = Depends(authenticate)):
    if request.model != settings.embedding_model_name:
        raise HTTPException(400, detail="Unsupported model")
    if request.encoding_format != "float":
        raise HTTPException(400, detail="Unsupported encoding format")
    if len(request.input) > settings.max_input_length:
        raise HTTPException(400, detail=f"Input too long, max {settings.max_input_length}")
    embedding = model.encode(request.input, normalize_embeddings=True).tolist()
    data = [{"object": "embedding", "embedding": embedding, "index": 0}]
    return {"object": "list", "model": settings.embedding_model_name, "data": data}

@app.post("/embed/batch")
async def embed_batch(request: BatchRequest, auth: bool = Depends(authenticate)):
    if request.model != settings.embedding_model_name:
        raise HTTPException(400, detail="Unsupported model")
    if request.encoding_format != "float":
        raise HTTPException(400, detail="Unsupported encoding format")
    if len(request.inputs) > 100:  # Arbitrary limit to prevent potential OOM; adjust as needed
        raise HTTPException(413, detail="Batch too large, please split into smaller batches")
    texts = []
    ids = []
    for inp in request.inputs:
        if len(inp.text) > settings.max_input_length:
            raise HTTPException(400, detail=f"Input too long for id {inp.id}, max {settings.max_input_length}")
        texts.append(inp.text)
        ids.append(inp.id)
    embeddings = model.encode(texts, normalize_embeddings=True, batch_size=8)
    data = []
    for i, emb in enumerate(embeddings):
        data.append({"id": ids[i], "object": "embedding", "embedding": emb.tolist()})
    return {"object": "list", "model": settings.embedding_model_name, "data": data}

@app.get("/health")
def health():
    return {"status": "ok", "model": settings.embedding_model_name, "ready": True}

@app.get("/metadata")
def metadata():
    return {
        "model": settings.embedding_model_name,
        "dimension": dimension,
        "version": __version__
    }