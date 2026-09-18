from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import image_store
from ..common import resolve_tags
from ..database import get_db
from ..models import Category, Image, ImageSet, Tag
from ..schemas import (
    BatchDelete,
    BatchMove,
    CategoryOut,
    FeedItem,
    FeedPage,
    ImageOut,
    ImagePage,
    ImageUpdate,
    SetOut,
    StatsOut,
    TagCount,
)
from .sets import serialize as serialize_set

router = APIRouter(prefix="/api", tags=["images"])


def serialize(image: Image) -> ImageOut:
    return ImageOut(
        id=image.id,
        filename=image.filename,
        stored_name=image.stored_name,
        content_type=image.content_type,
        width=image.width,
        height=image.height,
        size=image.size,
        description=image.description or "",
        placeholder=image.placeholder or "",
        category_id=image.category_id,
        category_name=image.category.name if image.category else None,
        set_id=image.set_id,
        tags=sorted(tag.name for tag in image.tags),
        deleted_at=image.deleted_at,
        created_at=image.created_at,
    )


def active_filter():
    return Image.deleted_at.is_(None)


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)) -> StatsOut:
    total_images = db.scalar(
        select(func.count(Image.id)).where(active_filter(), Image.set_id.is_(None))
    ) or 0
    total_sets = db.scalar(
        select(func.count(ImageSet.id)).where(ImageSet.deleted_at.is_(None))
    ) or 0
    trash_count = db.scalar(
        select(func.count(Image.id)).where(Image.deleted_at.is_not(None))
    ) or 0
    trash_count += db.scalar(
        select(func.count(ImageSet.id)).where(ImageSet.deleted_at.is_not(None))
    ) or 0
    total_bytes = db.scalar(
        select(func.coalesce(func.sum(Image.size), 0)).where(active_filter())
    ) or 0
    total_categories = db.scalar(select(func.count(Category.id))) or 0
    total_tags = db.scalar(select(func.count(Tag.id))) or 0

    recent_rows = db.scalars(
        select(Image).where(active_filter()).order_by(Image.created_at.desc()).limit(8)
    ).all()

    categories = db.scalars(
        select(Category).order_by(Category.sort_order, Category.id)
    ).all()
    usage = []
    for category in categories:
        count = db.scalar(
            select(func.count(Image.id)).where(
                Image.category_id == category.id, active_filter()
            )
        )
        usage.append(
            CategoryOut(
                id=category.id,
                name=category.name,
                description=category.description,
                sort_order=category.sort_order,
                image_count=count or 0,
            )
        )

    return StatsOut(
        total_images=total_images,
        total_sets=total_sets,
        total_categories=total_categories,
        total_tags=total_tags,
        total_bytes=total_bytes,
        trash_count=trash_count,
        recent=[serialize(image) for image in recent_rows],
        category_usage=usage,
    )


@router.get("/images", response_model=ImagePage)
def list_images(
    q: str | None = None,
    tag: str | None = None,
    category_id: int | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ImagePage:
    stmt = select(Image).where(active_filter())
    if q:
        stmt = stmt.where(Image.filename.ilike(f"%{q.strip()}%"))
    if tag:
        stmt = stmt.where(Image.tags.any(Tag.name == tag))
    if category_id is not None:
        stmt = stmt.where(Image.category_id == category_id)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(
        stmt.order_by(Image.created_at.desc(), Image.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    return ImagePage(
        items=[serialize(row) for row in rows],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/feed", response_model=FeedPage)
def feed(
    q: str | None = None,
    category_id: int | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> FeedPage:
    keyword = q.strip() if q else None

    image_stmt = select(Image.id, Image.created_at).where(
        active_filter(), Image.set_id.is_(None)
    )
    if keyword:
        image_stmt = image_stmt.where(Image.filename.ilike(f"%{keyword}%"))
    if category_id is not None:
        image_stmt = image_stmt.where(Image.category_id == category_id)

    set_stmt = select(ImageSet.id, ImageSet.created_at).where(
        ImageSet.deleted_at.is_(None)
    )
    if keyword:
        set_stmt = set_stmt.where(ImageSet.title.ilike(f"%{keyword}%"))
    if category_id is not None:
        set_stmt = set_stmt.where(ImageSet.category_id == category_id)

    entries = [("image", row.id, row.created_at) for row in db.execute(image_stmt).all()]
    entries += [("set", row.id, row.created_at) for row in db.execute(set_stmt).all()]
    entries.sort(key=lambda entry: (entry[2], entry[1]), reverse=True)

    total = len(entries)
    window = entries[(page - 1) * limit : page * limit]

    feed_items: list[FeedItem] = []
    for item_type, item_id, _ in window:
        if item_type == "image":
            image = db.get(Image, item_id)
            if image is None:
                continue
            feed_items.append(
                FeedItem(
                    item_type="image",
                    id=image.id,
                    title=image.filename,
                    description=image.description or "",
                    cover_image_id=image.id,
                    placeholder=image.placeholder or "",
                    category_id=image.category_id,
                    category_name=image.category.name if image.category else None,
                    tags=sorted(tag.name for tag in image.tags),
                    image_count=1,
                    width=image.width,
                    height=image.height,
                    created_at=image.created_at,
                    image=serialize(image),
                )
            )
        else:
            image_set = db.get(ImageSet, item_id)
            if image_set is None:
                continue
            base = serialize_set(db, image_set)
            cover = (
                db.get(Image, image_set.cover_image_id)
                if image_set.cover_image_id
                else None
            )
            feed_items.append(
                FeedItem(
                    item_type="set",
                    id=image_set.id,
                    title=base.title,
                    description=base.description,
                    cover_image_id=base.cover_image_id,
                    placeholder=cover.placeholder if cover else "",
                    category_id=base.category_id,
                    category_name=base.category_name,
                    tags=base.tags,
                    image_count=base.image_count,
                    width=cover.width if cover else 0,
                    height=cover.height if cover else 0,
                    created_at=image_set.created_at,
                )
            )

    return FeedPage(items=feed_items, total=total, page=page, limit=limit)


@router.get("/images/trash", response_model=ImagePage)
def list_trash(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ImagePage:
    stmt = select(Image).where(Image.deleted_at.is_not(None), Image.set_id.is_(None))
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(
        stmt.order_by(Image.deleted_at.desc()).offset((page - 1) * limit).limit(limit)
    ).all()
    return ImagePage(
        items=[serialize(row) for row in rows], total=total, page=page, limit=limit
    )


@router.post("/images", response_model=list[ImageOut], status_code=status.HTTP_201_CREATED)
def upload_images(
    files: list[UploadFile] = File(...),
    tags: str = Form(""),
    category_id: int | None = Form(None),
    description: str = Form(""),
    db: Session = Depends(get_db),
) -> list[ImageOut]:
    if category_id is not None and db.get(Category, category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="分类不存在"
        )

    tag_names = [part for part in tags.split(",") if part.strip()]
    tag_models = resolve_tags(db, tag_names)

    created: list[Image] = []
    for upload in files:
        meta = image_store.save_upload(upload)
        image = Image(
            **meta,
            tags=list(tag_models),
            category_id=category_id,
            description=description.strip(),
        )
        db.add(image)
        created.append(image)

    db.commit()
    for image in created:
        db.refresh(image)
    return [serialize(image) for image in created]


@router.post("/images/batch-delete")
def batch_delete(payload: BatchDelete, db: Session = Depends(get_db)) -> dict:
    if not payload.ids:
        return {"deleted": 0}
    images = db.scalars(
        select(Image).where(Image.id.in_(payload.ids), active_filter())
    ).all()
    for image in images:
        image.deleted_at = func.now()
    db.commit()
    return {"deleted": len(images)}


@router.post("/images/batch-move")
def batch_move(payload: BatchMove, db: Session = Depends(get_db)) -> dict:
    if not payload.ids:
        return {"moved": 0}
    if payload.category_id is not None and db.get(Category, payload.category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="分类不存在"
        )
    images = db.scalars(
        select(Image).where(Image.id.in_(payload.ids), active_filter())
    ).all()
    for image in images:
        image.category_id = payload.category_id
    db.commit()
    return {"moved": len(images)}


@router.post("/images/{image_id}/restore", response_model=ImageOut)
def restore_image(image_id: int, db: Session = Depends(get_db)) -> ImageOut:
    image = db.get(Image, image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")
    image.deleted_at = None
    db.commit()
    db.refresh(image)
    return serialize(image)


@router.delete("/images/{image_id}/purge")
def purge_image(image_id: int, db: Session = Depends(get_db)) -> dict:
    image = db.get(Image, image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")
    image_store.remove_files(image.stored_name)
    db.delete(image)
    db.commit()
    return {"deleted": 1}


@router.post("/trash/empty")
def empty_trash(db: Session = Depends(get_db)) -> dict:
    images = db.scalars(select(Image).where(Image.deleted_at.is_not(None))).all()
    for image in images:
        image_store.remove_files(image.stored_name)
        db.delete(image)

    sets = db.scalars(select(ImageSet).where(ImageSet.deleted_at.is_not(None))).all()
    for image_set in sets:
        image_set.cover_image_id = None
    db.flush()
    for image_set in sets:
        db.delete(image_set)

    db.commit()
    return {"deleted": len(images), "sets": len(sets)}


@router.get("/images/{image_id}", response_model=ImageOut)
def get_image(image_id: int, db: Session = Depends(get_db)) -> ImageOut:
    image = db.get(Image, image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")
    return serialize(image)


@router.patch("/images/{image_id}", response_model=ImageOut)
def update_image(
    image_id: int, payload: ImageUpdate, db: Session = Depends(get_db)
) -> ImageOut:
    image = db.get(Image, image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")

    if payload.filename is not None:
        image.filename = payload.filename.strip()
    if payload.description is not None:
        image.description = payload.description.strip()
    if "category_id" in payload.model_fields_set:
        if payload.category_id is not None and db.get(Category, payload.category_id) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="分类不存在"
            )
        image.category_id = payload.category_id
    if payload.tags is not None:
        image.tags = resolve_tags(db, payload.tags)

    db.commit()
    db.refresh(image)
    return serialize(image)


@router.delete("/images/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db)) -> dict:
    image = db.get(Image, image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")
    image.deleted_at = func.now()
    db.commit()
    return {"deleted": 1}


@router.get("/tags", response_model=list[TagCount])
def list_tags(db: Session = Depends(get_db)) -> list[TagCount]:
    rows = db.execute(
        select(Tag.name, func.count(Image.id))
        .join(Tag.images)
        .where(Image.deleted_at.is_(None))
        .group_by(Tag.name)
        .order_by(func.count(Image.id).desc(), Tag.name)
    ).all()
    return [TagCount(name=name, count=count) for name, count in rows]


@router.get("/media/original/{image_id}")
def original(image_id: int, db: Session = Depends(get_db)) -> FileResponse:
    image = db.get(Image, image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")
    path = image_store.ORIGINALS_DIR / image.stored_name
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="原图文件缺失")
    return FileResponse(path, media_type=image.content_type, filename=image.filename)


@router.get("/media/thumb/{image_id}")
def thumbnail(image_id: int, db: Session = Depends(get_db)) -> FileResponse:
    image = db.get(Image, image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")
    path = image_store.THUMBS_DIR / f"{image.stored_name}.jpg"
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="缩略图缺失")
    return FileResponse(path, media_type="image/jpeg")
