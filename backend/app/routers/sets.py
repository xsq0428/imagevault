from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import image_store
from ..common import resolve_tags
from ..database import get_db
from ..models import Category, Image, ImageSet, Tag
from ..schemas import SetDetail, SetOut, SetUpdate

router = APIRouter(prefix="/api/sets", tags=["sets"])


def serialize(db: Session, image_set: ImageSet) -> SetOut:
    count = db.scalar(
        select(func.count(Image.id)).where(
            Image.set_id == image_set.id, Image.deleted_at.is_(None)
        )
    )
    return SetOut(
        id=image_set.id,
        title=image_set.title,
        description=image_set.description or "",
        cover_image_id=image_set.cover_image_id,
        category_id=image_set.category_id,
        category_name=image_set.category.name if image_set.category else None,
        tags=sorted(tag.name for tag in image_set.tags),
        image_count=count or 0,
        deleted_at=image_set.deleted_at,
        created_at=image_set.created_at,
    )


def active_members(db: Session, set_id: int) -> list[Image]:
    return db.scalars(
        select(Image)
        .where(Image.set_id == set_id, Image.deleted_at.is_(None))
        .order_by(Image.id)
    ).all()


def serialize_detail(db: Session, image_set: ImageSet) -> SetDetail:
    from .images import serialize as serialize_image

    base = serialize(db, image_set)
    return SetDetail(
        **base.model_dump(),
        images=[serialize_image(image) for image in active_members(db, image_set.id)],
    )


@router.get("", response_model=list[SetOut])
def list_sets(db: Session = Depends(get_db)) -> list[SetOut]:
    sets = db.scalars(
        select(ImageSet)
        .where(ImageSet.deleted_at.is_(None))
        .order_by(ImageSet.created_at.desc())
    ).all()
    return [serialize(db, image_set) for image_set in sets]


@router.post("", response_model=SetDetail, status_code=status.HTTP_201_CREATED)
def create_set(
    files: list[UploadFile] = File(...),
    title: str = Form(""),
    description: str = Form(""),
    category_id: int | None = Form(None),
    tags: str = Form(""),
    db: Session = Depends(get_db),
) -> SetDetail:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="请至少上传一张图片"
        )
    if category_id is not None and db.get(Category, category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="分类不存在"
        )

    image_set = ImageSet(
        title=title.strip() or "未命名套图",
        description=description.strip(),
        category_id=category_id,
    )
    db.add(image_set)
    db.flush()

    created: list[Image] = []
    for upload in files:
        meta = image_store.save_upload(upload)
        image = Image(**meta, set_id=image_set.id, category_id=category_id)
        db.add(image)
        db.flush()
        created.append(image)

    image_set.cover_image_id = created[0].id
    image_set.tags = resolve_tags(
        db, [part for part in tags.split(",") if part.strip()]
    )

    db.commit()
    db.refresh(image_set)
    return serialize_detail(db, image_set)


@router.get("/trash", response_model=list[SetOut])
def list_trash_sets(db: Session = Depends(get_db)) -> list[SetOut]:
    sets = db.scalars(
        select(ImageSet)
        .where(ImageSet.deleted_at.is_not(None))
        .order_by(ImageSet.deleted_at.desc())
    ).all()
    return [serialize(db, image_set) for image_set in sets]


@router.get("/{set_id}", response_model=SetDetail)
def get_set(set_id: int, db: Session = Depends(get_db)) -> SetDetail:
    image_set = db.get(ImageSet, set_id)
    if image_set is None or image_set.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="套图不存在")
    return serialize_detail(db, image_set)


@router.patch("/{set_id}", response_model=SetDetail)
def update_set(
    set_id: int, payload: SetUpdate, db: Session = Depends(get_db)
) -> SetDetail:
    image_set = db.get(ImageSet, set_id)
    if image_set is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="套图不存在")

    if payload.title is not None:
        image_set.title = payload.title.strip()
    if payload.description is not None:
        image_set.description = payload.description.strip()
    if "category_id" in payload.model_fields_set:
        if payload.category_id is not None and db.get(Category, payload.category_id) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="分类不存在"
            )
        image_set.category_id = payload.category_id
    if payload.tags is not None:
        image_set.tags = resolve_tags(db, payload.tags)
    if payload.cover_image_id is not None:
        members = {image.id for image in active_members(db, set_id)}
        if payload.cover_image_id not in members:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="封面必须属于该套图"
            )
        image_set.cover_image_id = payload.cover_image_id

    db.commit()
    db.refresh(image_set)
    return serialize_detail(db, image_set)


@router.delete("/{set_id}")
def delete_set(set_id: int, db: Session = Depends(get_db)) -> dict:
    image_set = db.get(ImageSet, set_id)
    if image_set is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="套图不存在")

    image_set.deleted_at = func.now()
    for image in db.scalars(select(Image).where(Image.set_id == set_id)).all():
        image.deleted_at = func.now()
    db.commit()
    return {"deleted": 1}


@router.post("/{set_id}/restore", response_model=SetOut)
def restore_set(set_id: int, db: Session = Depends(get_db)) -> SetOut:
    image_set = db.get(ImageSet, set_id)
    if image_set is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="套图不存在")

    for image in db.scalars(select(Image).where(Image.set_id == set_id)).all():
        image.deleted_at = None
    image_set.deleted_at = None
    db.commit()
    db.refresh(image_set)
    return serialize(db, image_set)


@router.delete("/{set_id}/purge")
def purge_set(set_id: int, db: Session = Depends(get_db)) -> dict:
    image_set = db.get(ImageSet, set_id)
    if image_set is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="套图不存在")

    members = db.scalars(select(Image).where(Image.set_id == set_id)).all()
    for image in members:
        image_store.remove_files(image.stored_name)
        db.delete(image)
    image_set.cover_image_id = None
    db.flush()
    db.delete(image_set)
    db.commit()
    return {"deleted": len(members)}
