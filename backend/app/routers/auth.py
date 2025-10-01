from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database import get_db
from app.models.user import User
from app.config import settings
from app.utils.security import create_jwt_token,get_current_user
from google.oauth2 import id_token
from google.auth.transport.requests import Request
import httpx
import logging
from uuid import UUID

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
async def login():
    logger.debug("login")
    return {
        "url": f"{settings.google_auth_url}?client_id={settings.google_client_id}&redirect_uri={settings.google_redirect_uri}&response_type=code&scope=openid%20email%20profile"
    }

@router.post("/logout")  # New: Logout endpoint
async def logout(current_user: UUID = Depends(get_current_user)):
    logger.debug(f"User {current_user} logged out")
    return {"message": "Logout successful"}

@router.get("/callback")
async def callback(code: str, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.google_token_url,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Google OAuth failed")

        try:
            token_data = response.json()
        except ValueError:
            logger.error("Invalid JSON in Google token response")
            raise HTTPException(status_code=400, detail="Invalid Google response")
        id_token_str = token_data.get("id_token")
        if not id_token_str:
            raise HTTPException(status_code=400, detail="ID token not found")

        try:
            user_info = id_token.verify_oauth2_token(
                id_token_str,
                Request(),
                settings.google_client_id,
                clock_skew_in_seconds=30
            )
            if not user_info.get("email_verified", False):
                logger.warning(f"Unverified email: {user_info.get('email')}")
                raise HTTPException(status_code=400, detail="Email not verified")
        except ValueError as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid Google token")

        email = user_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email not found")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email)
            db.add(user)
        else:
            user.last_login = func.now()  # New: Update last_login for existing users
        db.commit()
        db.refresh(user)

        token = create_jwt_token({"sub": str(user.id), "email": email})
        return {"access_token": token, "token_type": "bearer"}