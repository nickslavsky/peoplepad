from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database import get_db
from app.models.user import User
from app.models.token import RefreshToken
from app.schemas.auth import RefreshRequest, AccessTokenResponse, LogoutResponse
from app.config import settings
from app.utils.security import create_access_token, create_refresh_token, get_current_user, validate_refresh_token, hash_token
from google.oauth2 import id_token
from google.auth.transport.requests import Request
import httpx
import logging
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
async def login():
    logger.debug("Initiating Google OAuth login")
    return {
        "url": f"{settings.google_auth_url}?client_id={settings.google_client_id}&redirect_uri={settings.google_redirect_uri}&response_type=code&scope=openid%20email%20profile"
    }

@router.post("/logout", response_model=LogoutResponse)
async def logout(current_user: UUID = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(RefreshToken).filter(RefreshToken.user_id == current_user).delete()
    db.commit()
    return LogoutResponse(message="Logout successful")



@router.get("/callback", response_class=HTMLResponse)
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
            logger.error(f"Google OAuth failed: {response.text}")
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
            user.last_login = func.now()
        db.commit()
        db.refresh(user)

        access_token = create_access_token({"sub": str(user.id), "email": email})
        refresh_token = create_refresh_token({"sub": str(user.id), "email": email})
        salt = os.urandom(32).hex()
        hashed_token = hash_token(refresh_token, salt)

        db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
        db.add(RefreshToken(
            id=uuid4(),
            user_id=user.id,
            hashed_token=hashed_token,
            salt=salt,
            expires_at=datetime.utcnow() + timedelta(days=30)
        ))
        db.commit()

        # Get frontend URL from settings - add this to your config!
        frontend_url = getattr(settings, 'frontend_url', 'http://localhost:5173')

        # HTML response to send tokens to parent window via postMessage
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Successful</title>
        </head>
        <body>
            <p>Authentication successful! Closing window...</p>
            <script>
                // Send tokens to the opener window
                if (window.opener) {{
                    window.opener.postMessage({{
                        access_token: '{access_token}',
                        refresh_token: '{refresh_token}'
                    }}, '{frontend_url}');
                    window.close();
                }} else {{
                    document.body.innerHTML = '<p>Error: Could not communicate with parent window. Please close this window and try again.</p>';
                }}
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(data: RefreshRequest, db: Session = Depends(get_db)):
    user_id = await validate_refresh_token(data.refresh_token, db)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    return AccessTokenResponse(access_token=access_token)