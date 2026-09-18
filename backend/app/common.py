from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Tag


def resolve_tags(db: Session, names: list[str]) -> list[Tag]:
    resolved: list[Tag] = []
    seen: set[str] = set()
    for raw in names:
        name = raw.strip()
        if not name or name in seen:
            continue
        seen.add(name)
        tag = db.scalar(select(Tag).where(Tag.name == name))
        if tag is None:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        resolved.append(tag)
    return resolved
