import base64
import hashlib
import hmac
import json
import secrets
from datetime import timedelta

from app.core.config import get_settings
from app.core.time import utc_now


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, salt, expected = password_hash.split("$", 2)
    except ValueError:
        return False
    if scheme != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return hmac.compare_digest(digest.hex(), expected)


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expires_at = utc_now() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": user_id, "exp": int(expires_at.timestamp())}
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_part = base64.urlsafe_b64encode(payload_bytes).decode("ascii").rstrip("=")
    signature = _sign(payload_part, settings.auth_secret_key)
    return f"{payload_part}.{signature}"


def decode_access_token(token: str) -> int | None:
    settings = get_settings()
    try:
        payload_part, signature = token.split(".", 1)
    except ValueError:
        return None
    if not hmac.compare_digest(_sign(payload_part, settings.auth_secret_key), signature):
        return None
    padded = payload_part + "=" * (-len(payload_part) % 4)
    payload = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
    if int(payload.get("exp", 0)) < int(utc_now().timestamp()):
        return None
    return int(payload["sub"])


def _sign(payload_part: str, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), payload_part.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

