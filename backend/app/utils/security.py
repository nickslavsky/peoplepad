from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt, ExpiredSignatureError
from app.config import settings
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from uuid import UUID
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UUID:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"require_exp": True}  # New: Require exp claim
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
    except ExpiredSignatureError:  # New: Handle expired tokens specifically
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.error(f"JWT validation failed: {str(e)}")
        raise credentials_exception

def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()  # New: Copy to avoid mutating input
    expire = datetime.utcnow() + timedelta(minutes=30)  # New: 30-min expiration (configurable via settings if needed)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)