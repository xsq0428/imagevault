from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class TagCount(BaseModel):
    name: str
    count: int


class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    description: str = Field(default="", max_length=255)
    sort_order: int = 0


class CategoryOut(BaseModel):
    id: int
    name: str
    description: str
    sort_order: int
    image_count: int
    cover_source: str = "none"
    cover_image_id: int | None = None
    cover_placeholder: str = ""


class BannerOut(BaseModel):
    id: int
    title: str
    link: str
    filename: str
    width: int
    height: int
    size: int
    placeholder: str = ""
    sort_order: int
    is_active: bool
    created_at: datetime


class BannerUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=128)
    link: str | None = Field(default=None, max_length=255)
    sort_order: int | None = None
    is_active: bool | None = None


class ImageOut(BaseModel):
    id: int
    filename: str
    stored_name: str
    content_type: str
    width: int
    height: int
    size: int
    description: str
    placeholder: str = ""
    category_id: int | None
    category_name: str | None
    set_id: int | None
    tags: list[str] = Field(default_factory=list)
    deleted_at: datetime | None
    created_at: datetime


class ImagePage(BaseModel):
    items: list[ImageOut]
    total: int
    page: int
    limit: int


class ImageUpdate(BaseModel):
    filename: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    category_id: int | None = None
    tags: list[str] | None = None


class SetUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=500)
    category_id: int | None = None
    tags: list[str] | None = None
    cover_image_id: int | None = None


class SetOut(BaseModel):
    id: int
    title: str
    description: str
    cover_image_id: int | None
    category_id: int | None
    category_name: str | None
    tags: list[str] = Field(default_factory=list)
    image_count: int
    deleted_at: datetime | None
    created_at: datetime


class SetDetail(SetOut):
    images: list[ImageOut] = Field(default_factory=list)


class FeedItem(BaseModel):
    item_type: str
    id: int
    title: str
    description: str
    cover_image_id: int | None
    placeholder: str = ""
    category_id: int | None
    category_name: str | None
    tags: list[str] = Field(default_factory=list)
    image_count: int
    width: int
    height: int
    created_at: datetime
    image: ImageOut | None = None


class FeedPage(BaseModel):
    items: list[FeedItem]
    total: int
    page: int
    limit: int


class BatchDelete(BaseModel):
    ids: list[int] = Field(default_factory=list)


class BatchMove(BaseModel):
    ids: list[int] = Field(default_factory=list)
    category_id: int | None = None


class StatsOut(BaseModel):
    total_images: int
    total_sets: int
    total_categories: int
    total_tags: int
    total_bytes: int
    trash_count: int
    recent: list[ImageOut]
    category_usage: list[CategoryOut]


class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)
    captcha: str = Field(min_length=1, max_length=8)


class AdminOut(BaseModel):
    id: int
    username: str


class CaptchaOut(BaseModel):
    image: str


class AccountUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=64)
    current_password: str | None = Field(default=None, max_length=128)
    new_password: str | None = Field(default=None, min_length=6, max_length=128)


class SiteConfigOut(BaseModel):
    site_name: str
    site_tagline: str
    site_description: str
    site_keywords: str
    footer_text: str
    icp_number: str
    logo_placeholder: str = ""
    has_logo: bool = False
    page_size: int
    announcement_enabled: bool
    announcement_mode: str
    announcement_text: str
    updated_at: datetime


class SiteConfigUpdate(BaseModel):
    site_name: str | None = Field(default=None, min_length=1, max_length=64)
    site_tagline: str | None = Field(default=None, max_length=128)
    site_description: str | None = Field(default=None, max_length=255)
    site_keywords: str | None = Field(default=None, max_length=255)
    footer_text: str | None = Field(default=None, max_length=255)
    icp_number: str | None = Field(default=None, max_length=128)
    page_size: int | None = Field(default=None, ge=1, le=60)
    announcement_enabled: bool | None = None
    announcement_mode: str | None = None
    announcement_text: str | None = Field(default=None, max_length=500)

