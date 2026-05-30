from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import hash_password, verify_password
from app.db.models import User
from app.db.session import get_db

router = APIRouter(prefix="/api/profile", tags=["profile"])


class ProfileUpdate(BaseModel):
    nickname: str | None = Field(default=None, max_length=128)


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


def serialize_user(user: User) -> dict[str, object]:
    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "created_at": user.created_at.isoformat(sep=" ") if user.created_at else None,
    }


@router.get("")
def get_profile(current_user: User = Depends(get_current_user)) -> dict[str, object]:
    return serialize_user(current_user)


@router.patch("")
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    current_user.nickname = payload.nickname.strip() if payload.nickname else None
    db.commit()
    db.refresh(current_user)
    return serialize_user(current_user)


@router.patch("/password")
def update_password(
    payload: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"password_changed": True}

