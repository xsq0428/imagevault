from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import image_store
from ..database import get_db
from ..models import Category, Image, ImageSet
from ..schemas import CategoryIn, CategoryOut

router = APIRouter(prefix="/api/categories", tags=["categories"])


def serialize(db: Session, category: Category) -> CategoryOut:
    count = db.scalar(
        select(func.count(Image.id)).where(
            Image.category_id == category.id, Image.deleted_at.is_(None)
        )
    )

    if category.cover_stored_name:
        return CategoryOut(
            id=category.id,
            name=category.name,
            description=category.description,
            sort_order=category.sort_order,
            image_count=count or 0,
            cover_source="upload",
            cover_image_id=None,
            cover_placeholder=category.cover_placeholder or "",
        )

    cover = db.scalar(
        select(Image)
        .where(Image.category_id == category.id, Image.deleted_at.is_(None))
        .order_by(Image.created_at.desc(), Image.id.desc())
        .limit(1)
    )
    if cover is None:
        cover_id = db.scalar(
            select(ImageSet.cover_image_id)
            .where(
                ImageSet.category_id == category.id,
                ImageSet.deleted_at.is_(None),
                ImageSet.cover_image_id.is_not(None),
            )
            .order_by(ImageSet.created_at.desc())
            .limit(1)
        )
        if cover_id is not None:
            cover = db.get(Image, cover_id)

    return CategoryOut(
        id=category.id,
        name=category.name,
        description=category.description,
        sort_order=category.sort_order,
        image_count=count or 0,
        cover_source="image" if cover else "none",
        cover_image_id=cover.id if cover else None,
        cover_placeholder=cover.placeholder if cover else "",
    )


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryOut]:
    categories = db.scalars(
        select(Category).order_by(Category.sort_order, Category.id)
    ).all()
    return [serialize(db, category) for category in categories]


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryIn, db: Session = Depends(get_db)) -> CategoryOut:
    name = payload.name.strip()
    if db.scalar(select(Category).where(Category.name == name)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类名称已存在",
        )
    category = Category(
        name=name, description=payload.description.strip(), sort_order=payload.sort_order
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return serialize(db, category)


@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int, payload: CategoryIn, db: Session = Depends(get_db)
) -> CategoryOut:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在"
        )

    name = payload.name.strip()
    duplicate = db.scalar(
        select(Category).where(Category.name == name, Category.id != category_id)
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="分类名称已存在"
        )

    category.name = name
    category.description = payload.description.strip()
    category.sort_order = payload.sort_order
    db.commit()
    db.refresh(category)
    return serialize(db, category)


@router.post("/{category_id}/cover", response_model=CategoryOut)
def upload_cover(
    category_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
) -> CategoryOut:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在"
        )

    meta = image_store.save_upload(file)
    if category.cover_stored_name:
        image_store.remove_files(category.cover_stored_name)

    category.cover_stored_name = meta["stored_name"]
    category.cover_content_type = meta["content_type"]
    category.cover_placeholder = meta["placeholder"]
    db.commit()
    db.refresh(category)
    return serialize(db, category)


@router.delete("/{category_id}/cover", response_model=CategoryOut)
def delete_cover(category_id: int, db: Session = Depends(get_db)) -> CategoryOut:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在"
        )

    if category.cover_stored_name:
        image_store.remove_files(category.cover_stored_name)
        category.cover_stored_name = ""
        category.cover_content_type = ""
        category.cover_placeholder = ""
        db.commit()
        db.refresh(category)
    return serialize(db, category)


@router.get("/{category_id}/cover")
def category_cover(category_id: int, db: Session = Depends(get_db)) -> FileResponse:
    category = db.get(Category, category_id)
    if category is None or not category.cover_stored_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="封面不存在")
    path = image_store.ORIGINALS_DIR / category.cover_stored_name
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="封面文件缺失")
    return FileResponse(path, media_type=category.cover_content_type or "image/jpeg")


@router.get("/{category_id}/cover-thumb")
def category_cover_thumb(category_id: int, db: Session = Depends(get_db)) -> FileResponse:
    category = db.get(Category, category_id)
    if category is None or not category.cover_stored_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="封面不存在")
    path = image_store.THUMBS_DIR / f"{category.cover_stored_name}.jpg"
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="封面缩略图缺失")
    return FileResponse(path, media_type="image/jpeg")


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)) -> dict:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在"
        )

    db.execute(
        Image.__table__.update()
        .where(Image.category_id == category_id)
        .values(category_id=None)
    )
    db.execute(
        ImageSet.__table__.update()
        .where(ImageSet.category_id == category_id)
        .values(category_id=None)
    )
    if category.cover_stored_name:
        image_store.remove_files(category.cover_stored_name)
    db.delete(category)
    db.commit()
    return {"deleted": 1}
