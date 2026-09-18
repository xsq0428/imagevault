from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import image_store
from ..auth import require_admin
from ..database import get_db
from ..models import AdminUser, SiteConfig
from ..schemas import SiteConfigOut, SiteConfigUpdate

router = APIRouter(prefix="/api", tags=["site-config"])


def get_or_create_config(db: Session) -> SiteConfig:
    config = db.scalar(select(SiteConfig).order_by(SiteConfig.id))
    if config is None:
        config = SiteConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def serialize(config: SiteConfig) -> SiteConfigOut:
    return SiteConfigOut(
        site_name=config.site_name,
        site_tagline=config.site_tagline,
        site_description=config.site_description,
        site_keywords=config.site_keywords,
        footer_text=config.footer_text,
        icp_number=config.icp_number,
        logo_placeholder=config.logo_placeholder or "",
        has_logo=bool(config.logo_stored_name),
        page_size=config.page_size,
        announcement_enabled=config.announcement_enabled,
        announcement_mode=config.announcement_mode or "topbar",
        announcement_text=config.announcement_text,
        updated_at=config.updated_at,
    )


@router.get("/site-config", response_model=SiteConfigOut)
def public_site_config(db: Session = Depends(get_db)) -> SiteConfigOut:
    return serialize(get_or_create_config(db))


@router.get("/admin/site-config", response_model=SiteConfigOut)
def admin_site_config(
    _: AdminUser = Depends(require_admin), db: Session = Depends(get_db)
) -> SiteConfigOut:
    return serialize(get_or_create_config(db))


@router.patch("/admin/site-config", response_model=SiteConfigOut)
def update_site_config(
    payload: SiteConfigUpdate,
    _: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SiteConfigOut:
    config = get_or_create_config(db)
    for field in payload.model_fields_set:
        value = getattr(payload, field)
        if value is None:
            continue
        setattr(config, field, value.strip() if isinstance(value, str) else value)
    db.commit()
    db.refresh(config)
    return serialize(config)


@router.post("/admin/site-config/logo", response_model=SiteConfigOut)
def upload_logo(
    file: UploadFile = File(...),
    _: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SiteConfigOut:
    config = get_or_create_config(db)
    meta = image_store.save_upload(file)
    if config.logo_stored_name:
        image_store.remove_files(config.logo_stored_name)
    config.logo_stored_name = meta["stored_name"]
    config.logo_content_type = meta["content_type"]
    config.logo_placeholder = meta["placeholder"]
    db.commit()
    db.refresh(config)
    return serialize(config)


@router.delete("/admin/site-config/logo", response_model=SiteConfigOut)
def delete_logo(
    _: AdminUser = Depends(require_admin), db: Session = Depends(get_db)
) -> SiteConfigOut:
    config = get_or_create_config(db)
    if config.logo_stored_name:
        image_store.remove_files(config.logo_stored_name)
        config.logo_stored_name = ""
        config.logo_content_type = ""
        config.logo_placeholder = ""
        db.commit()
        db.refresh(config)
    return serialize(config)


@router.get("/media/logo")
def logo_image(db: Session = Depends(get_db)) -> FileResponse:
    config = get_or_create_config(db)
    if not config.logo_stored_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Logo 不存在")
    path = image_store.ORIGINALS_DIR / config.logo_stored_name
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Logo 文件缺失")
    return FileResponse(path, media_type=config.logo_content_type or "image/png")


@router.get("/media/logo-thumb")
def logo_thumbnail(db: Session = Depends(get_db)) -> FileResponse:
    config = get_or_create_config(db)
    if not config.logo_stored_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Logo 不存在")
    path = image_store.THUMBS_DIR / f"{config.logo_stored_name}.jpg"
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Logo 缩略图缺失")
    return FileResponse(path, media_type="image/jpeg")
