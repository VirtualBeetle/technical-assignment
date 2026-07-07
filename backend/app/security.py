"""
Demo-grade authentication.

This is deliberately simple (single hardcoded CEO account, JWT in a bearer
token) because the assignment brief asks for "a platform a CEO would log in
to and use" as a demonstration surface, not a production auth system. A real
deployment would add refresh tokens, httpOnly cookies, SSO, and per-user
roles/permissions - noted in the README under Assumptions.
"""
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expires_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def ensure_demo_user(db: Session) -> None:
    existing = db.query(User).filter(User.email == settings.demo_ceo_email).first()
    if existing:
        return
    user = User(
        email=settings.demo_ceo_email,
        hashed_password=hash_password(settings.demo_ceo_password),
        full_name="Brendan Allen",
        role="ceo",
    )
    db.add(user)
    db.commit()
