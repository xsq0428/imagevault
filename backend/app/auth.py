import hashlib
import hmac
import io
import secrets
import threading
import time
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request, Response, status
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import AdminSession, AdminUser

SESSION_COOKIE = "iv_session"
CAPTCHA_COOKIE = "iv_captcha"
SESSION_MAX_AGE = 7 * 24 * 3600
CAPTCHA_MAX_AGE = 300
PBKDF2_ITERATIONS = 240_000

_captcha_lock = threading.Lock()
_captcha_store: dict[str, tuple[str, float]] = {}


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return (
        f"pbkdf2_sha256${PBKDF2_ITERATIONS}$"
        f"{salt.hex()}${digest.hex()}"
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded.split("$")
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    expected = bytes.fromhex(digest_hex)
    actual = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
    )
    return hmac.compare_digest(actual, expected)


def ensure_default_admin(db: Session) -> None:
    if db.scalar(select(AdminUser).limit(1)) is not None:
        return
    db.add(AdminUser(username="admin", password_hash=hash_password("admin123")))
    db.commit()


def create_session(db: Session, user: AdminUser) -> str:
    token = secrets.token_urlsafe(48)
    session = AdminSession(
        token=token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(seconds=SESSION_MAX_AGE),
    )
    db.add(session)
    db.commit()
    return token


def get_session_user(db: Session, token: str | None) -> AdminUser | None:
    if not token:
        return None
    session = db.scalar(select(AdminSession).where(AdminSession.token == token))
    if session is None:
        return None
    if session.expires_at < datetime.utcnow():
        db.delete(session)
        db.commit()
        return None
    return session.user


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/")


def require_admin(
    request: Request, db: Session = Depends(get_db)
) -> AdminUser:
    token = request.cookies.get(SESSION_COOKIE)
    user = get_session_user(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录"
        )
    return user


def optional_admin(
    request: Request, db: Session = Depends(get_db)
) -> AdminUser | None:
    return get_session_user(db, request.cookies.get(SESSION_COOKIE))


def generate_captcha() -> tuple[str, bytes]:
    width, height = 120, 44
    background = PILImage.new("RGB", (width, height), (247, 250, 249))
    draw = ImageDraw.Draw(background)

    answer = "".join(secrets.choice("0123456789") for _ in range(4))

    for _ in range(6):
        start = (secrets.randbelow(width), secrets.randbelow(height))
        end = (secrets.randbelow(width), secrets.randbelow(height))
        draw.line([start, end], fill=(200, 225, 217), width=1)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
    except OSError:
        font = ImageFont.load_default()

    for index, char in enumerate(answer):
        x = 14 + index * 25 + secrets.randbelow(5)
        y = secrets.randbelow(8) + 4
        color = (
            secrets.randbelow(60) + 40,
            secrets.randbelow(60) + 90,
            secrets.randbelow(60) + 70,
        )
        draw.text((x, y), char, fill=color, font=font)

    buffer = io.BytesIO()
    background.save(buffer, "PNG")
    return answer, buffer.getvalue()


def store_captcha(answer: str) -> str:
    captcha_id = secrets.token_urlsafe(24)
    now = time.time()
    with _captcha_lock:
        expired = [key for key, (_, expiry) in _captcha_store.items() if expiry < now]
        for key in expired:
            _captcha_store.pop(key, None)
        _captcha_store[captcha_id] = (answer, now + CAPTCHA_MAX_AGE)
    return captcha_id


def consume_captcha(captcha_id: str | None, answer: str) -> bool:
    if not captcha_id:
        return False
    now = time.time()
    with _captcha_lock:
        stored = _captcha_store.pop(captcha_id, None)
    if stored is None:
        return False
    expected, expiry = stored
    if expiry < now:
        return False
    return hmac.compare_digest(expected, answer.strip())
