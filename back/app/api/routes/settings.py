from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import Setting
from app.db.models import User
from app.db.session import get_db

router = APIRouter(prefix="/api/settings", tags=["settings"])


class ApiKeyPayload(BaseModel):
    api_key: str


@router.get("")
def get_settings_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    weread_key = (
        db.query(Setting).filter(Setting.user_id == current_user.id, Setting.key == "weread_api_key").first()
    )
    ai_key = db.query(Setting).filter(Setting.user_id == current_user.id, Setting.key == "ai_api_key").first()
    return {"weread_key_configured": bool(weread_key), "ai_key_configured": bool(ai_key)}


@router.get("/weread-key")
def get_weread_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    setting = db.query(Setting).filter(Setting.user_id == current_user.id, Setting.key == "weread_api_key").first()
    value = setting.value if setting and setting.value else ""
    return {"api_key": value, "configured": bool(value)}


@router.put("/weread-key")
def save_weread_key(
    payload: ApiKeyPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    value = payload.api_key.strip()
    setting = db.query(Setting).filter(Setting.user_id == current_user.id, Setting.key == "weread_api_key").first()
    if setting is None:
        setting = Setting(user_id=current_user.id, key="weread_api_key", value=value, is_secret=1)
        db.add(setting)
    else:
        setting.value = value
    db.commit()
    return {"configured": bool(value)}
