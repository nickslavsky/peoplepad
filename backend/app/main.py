import logging
from fastapi import FastAPI
from fastapi.security import OAuth2AuthorizationCodeBearer
from app.database import engine, Base, SessionLocal
from app.routers import auth, records, search, tags
from app.config import settings

logging.basicConfig(level=logging.DEBUG, force=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="PeoplePad MVP")

# OAuth2 configuration for Google
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.google_auth_url,
    tokenUrl=settings.google_token_url,
    scopes={"openid": "OpenID", "email": "Email", "profile": "Profile"},
)

# Include routers
app.include_router(auth.router)
app.include_router(records.router)
app.include_router(search.router)
app.include_router(tags.router)

@app.get("/")
async def root():
    return {"message": "PeoplePad MVP API"}
