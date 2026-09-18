from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

image_tags = Table(
    "image_tags",
    Base.metadata,
    Column("image_id", ForeignKey("images.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

set_tags = Table(
    "set_tags",
    Base.metadata,
    Column("set_id", ForeignKey("image_sets.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    images: Mapped[list["Image"]] = relationship(
        secondary=image_tags, back_populates="tags"
    )
    sets: Mapped[list["ImageSet"]] = relationship(
        secondary=set_tags, back_populates="tags"
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255), default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    cover_stored_name: Mapped[str] = mapped_column(String(128), default="")
    cover_content_type: Mapped[str] = mapped_column(String(64), default="")
    cover_placeholder: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    images: Mapped[list["Image"]] = relationship(back_populates="category")


class ImageSet(Base):
    __tablename__ = "image_sets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(String(500), default="")
    cover_image_id: Mapped[int | None] = mapped_column(
        ForeignKey("images.id", ondelete="SET NULL"), nullable=True
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    category: Mapped[Category | None] = relationship(lazy="joined")
    tags: Mapped[list[Tag]] = relationship(
        secondary=set_tags, back_populates="sets", lazy="selectin"
    )
    images: Mapped[list["Image"]] = relationship(
        back_populates="image_set",
        foreign_keys="Image.set_id",
        lazy="selectin",
    )


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    content_type: Mapped[str] = mapped_column(String(64))
    width: Mapped[int] = mapped_column(Integer, default=0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    size: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str] = mapped_column(String(500), default="")
    placeholder: Mapped[str] = mapped_column(Text, default="")
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    set_id: Mapped[int | None] = mapped_column(
        ForeignKey("image_sets.id", ondelete="CASCADE"), nullable=True, index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tags: Mapped[list[Tag]] = relationship(
        secondary=image_tags, back_populates="images", lazy="selectin"
    )
    category: Mapped[Category | None] = relationship(
        back_populates="images", lazy="joined"
    )
    image_set: Mapped[ImageSet | None] = relationship(
        back_populates="images", foreign_keys=[set_id]
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class AdminSession(Base):
    __tablename__ = "admin_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("admin_users.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)

    user: Mapped[AdminUser] = relationship(lazy="joined")


class SiteConfig(Base):
    __tablename__ = "site_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    site_name: Mapped[str] = mapped_column(String(64), default="ImageVault")
    site_tagline: Mapped[str] = mapped_column(String(128), default="图片素材库")
    site_description: Mapped[str] = mapped_column(String(255), default="")
    site_keywords: Mapped[str] = mapped_column(String(255), default="")
    footer_text: Mapped[str] = mapped_column(String(255), default="")
    icp_number: Mapped[str] = mapped_column(String(128), default="")
    logo_stored_name: Mapped[str] = mapped_column(String(128), default="")
    logo_content_type: Mapped[str] = mapped_column(String(64), default="")
    logo_placeholder: Mapped[str] = mapped_column(Text, default="")
    page_size: Mapped[int] = mapped_column(Integer, default=8)
    announcement_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    announcement_mode: Mapped[str] = mapped_column(String(16), default="topbar")
    announcement_text: Mapped[str] = mapped_column(String(500), default="")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Banner(Base):
    __tablename__ = "banners"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(128), default="")
    link: Mapped[str] = mapped_column(String(255), default="")
    filename: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    content_type: Mapped[str] = mapped_column(String(64))
    width: Mapped[int] = mapped_column(Integer, default=0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    size: Mapped[int] = mapped_column(Integer, default=0)
    placeholder: Mapped[str] = mapped_column(Text, default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
