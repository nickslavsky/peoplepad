from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt, ExpiredSignatureError
from app.config import settings
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.token import RefreshToken
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import logging
import hashlib

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)) -> UUID:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"require_exp": True}
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token missing 'sub' claim")
            raise credentials_exception
        user = db.query(User).filter(User.id == UUID(user_id)).first()
        if user is None:
            logger.warning(f"No user found for ID: {user_id}")
            raise credentials_exception
        return user.id
    except ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.error(f"JWT validation failed: {str(e)}")
        raise credentials_exception

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=1)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def hash_token(token: str, salt: str) -> str:
    """Hash the token with a provided salt using SHA-256."""
    return hashlib.sha256((token + salt).encode('utf-8')).hexdigest()

def verify_token(token: str, hashed_token: str, salt: str) -> bool:
    """Verify a token against its stored hash using the provided salt."""
    try:
        computed_hash = hash_token(token, salt)
        return computed_hash == hashed_token
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return False

async def validate_refresh_token(token: str, db: Session) -> UUID:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"require_exp": True}
        )
        if payload.get("type") != "refresh":
            logger.warning("Token is not a refresh token")
            raise credentials_exception
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Refresh token missing 'sub' claim")
            raise credentials_exception
        token_record = db.query(RefreshToken).filter(
            RefreshToken.user_id == UUID(user_id),
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        if token_record is None or not verify_token(token, token_record.hashed_token, token_record.salt):
            logger.warning(f"No valid refresh token found for user ID: {user_id}")
            raise credentials_exception
        return UUID(user_id)
    except (JWTError, ExpiredSignatureError) as e:
        logger.error(f"Refresh token validation failed: {str(e)}")
        raise credentials_exception