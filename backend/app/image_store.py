import base64
import io
import secrets
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image as PILImage
from PIL import UnidentifiedImageError

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ORIGINALS_DIR = DATA_DIR / "originals"
THUMBS_DIR = DATA_DIR / "thumbs"

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/bmp": ".bmp",
}
MAX_BYTES = 20 * 1024 * 1024
THUMB_MAX_SIDE = 480
PLACEHOLDER_MAX_SIDE = 20


def build_placeholder(source: PILImage.Image) -> str:
    tiny = source.convert("RGB")
    tiny.thumbnail((PLACEHOLDER_MAX_SIDE, PLACEHOLDER_MAX_SIDE))
    buffer = io.BytesIO()
    tiny.save(buffer, "JPEG", quality=35)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def ensure_dirs() -> None:
    for directory in (DATA_DIR, ORIGINALS_DIR, THUMBS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def save_upload(file: UploadFile) -> dict:
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: {content_type or 'unknown'}",
        )

    raw = file.file.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image exceeds the 20MB limit",
        )

    extension = ALLOWED_TYPES[content_type]
    stored_name = f"{secrets.token_hex(16)}{extension}"
    original_path = ORIGINALS_DIR / stored_name

    try:
        with PILImage.open(io.BytesIO(raw)) as probe:
            probe.verify()
        with PILImage.open(io.BytesIO(raw)) as source:
            width, height = source.size
            thumb = source.convert("RGB")
            thumb.thumbnail((THUMB_MAX_SIDE, THUMB_MAX_SIDE))
            thumb.save(THUMBS_DIR / f"{stored_name}.jpg", "JPEG", quality=85)
            placeholder = build_placeholder(source)
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not a readable image",
        ) from None

    original_path.write_bytes(raw)

    return {
        "filename": file.filename or stored_name,
        "stored_name": stored_name,
        "content_type": content_type,
        "width": width,
        "height": height,
        "size": len(raw),
        "placeholder": placeholder,
    }


def remove_files(stored_name: str) -> None:
    (ORIGINALS_DIR / stored_name).unlink(missing_ok=True)
    (THUMBS_DIR / f"{stored_name}.jpg").unlink(missing_ok=True)
