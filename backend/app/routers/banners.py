from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import image_store
from ..database import get_db
from ..models import Banner
from ..schemas import BannerOut, BannerUpdate

router = APIRouter(prefix="/api", tags=["banners"])


def serialize(banner: Banner) -> BannerOut:
    return BannerOut(
        id=banner.id,
        title=banner.title or "",
        link=banner.link or "",
        filename=banner.filename,
        width=banner.width,
        height=banner.height,
        size=banner.size,
        placeholder=banner.placeholder or "",
        sort_order=banner.sort_order,
        is_active=banner.is_active,
        created_at=banner.created_at,
    )


@router.get("/banners", response_model=list[BannerOut])
def list_banners(
    include_inactive: bool = False, db: Session = Depends(get_db)
) -> list[BannerOut]:
    stmt = select(Banner)
    if not include_inactive:
        stmt = stmt.where(Banner.is_active.is_(True))
    banners = db.scalars(stmt.order_by(Banner.sort_order, Banner.id)).all()
    return [serialize(banner) for banner in banners]


@router.post("/banners", response_model=list[BannerOut], status_code=status.HTTP_201_CREATED)
def upload_banners(
    files: list[UploadFile] = File(...),
    title: str = Form(""),
    link: str = Form(""),
    db: Session = Depends(get_db),
) -> list[BannerOut]:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="请至少上传一张广告图"
        )

    start = db.scalar(select(func.coalesce(func.max(Banner.sort_order), 0))) or 0
    created: list[Banner] = []
    for offset, upload in enumerate(files, start=1):
        meta = image_store.save_upload(upload)
        banner = Banner(
            **meta,
            title=title.strip() or (upload.filename or "广告图"),
            link=link.strip(),
            sort_order=start + offset,
        )
        db.add(banner)
        created.append(banner)

    db.commit()
    for banner in created:
        db.refresh(banner)
    return [serialize(banner) for banner in created]


@router.patch("/banners/{banner_id}", response_model=BannerOut)
def update_banner(
    banner_id: int, payload: BannerUpdate, db: Session = Depends(get_db)
) -> BannerOut:
    banner = db.get(Banner, banner_id)
    if banner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="广告图不存在")

    if payload.title is not None:
        banner.title = payload.title.strip()
    if payload.link is not None:
        banner.link = payload.link.strip()
    if payload.sort_order is not None:
        banner.sort_order = payload.sort_order
    if payload.is_active is not None:
        banner.is_active = payload.is_active

    db.commit()
    db.refresh(banner)
    return serialize(banner)


@router.delete("/banners/{banner_id}")
def delete_banner(banner_id: int, db: Session = Depends(get_db)) -> dict:
    banner = db.get(Banner, banner_id)
    if banner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="广告图不存在")

    image_store.remove_files(banner.stored_name)
    db.delete(banner)
    db.commit()
    return {"deleted": 1}


@router.get("/media/banner/{banner_id}")
def banner_image(banner_id: int, db: Session = Depends(get_db)) -> FileResponse:
    banner = db.get(Banner, banner_id)
    if banner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="广告图不存在")
    path = image_store.ORIGINALS_DIR / banner.stored_name
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件缺失")
    return FileResponse(path, media_type=banner.content_type, filename=banner.filename)


@router.get("/media/banner-thumb/{banner_id}")
def banner_thumbnail(banner_id: int, db: Session = Depends(get_db)) -> FileResponse:
    banner = db.get(Banner, banner_id)
    if banner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="广告图不存在")
    path = image_store.THUMBS_DIR / f"{banner.stored_name}.jpg"
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="缩略图缺失")
    return FileResponse(path, media_type="image/jpeg")
