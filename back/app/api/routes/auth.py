from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.db.session import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


class AuthPayload(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    nickname: str | None = None


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


def user_response(user: User) -> dict[str, object]:
    return {"id": user.id, "email": user.email, "nickname": user.nickname}


@router.post("/register")
def register(payload: AuthPayload, db: Session = Depends(get_db)) -> dict[str, object]:
    email = payload.email.lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=email, nickname=payload.nickname, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"access_token": create_access_token(user.id), "token_type": "bearer", "user": user_response(user)}


@router.post("/login")
def login(payload: LoginPayload, db: Session = Depends(get_db)) -> dict[str, object]:
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token(user.id), "token_type": "bearer", "user": user_response(user)}

