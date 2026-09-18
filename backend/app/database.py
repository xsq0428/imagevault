import shutil
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'gallery.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def backup_database(keep: int = 20) -> Path | None:
    db_path = DATA_DIR / "gallery.db"
    if not db_path.exists():
        return None
    backup_dir = DATA_DIR / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / f"gallery-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db"
    shutil.copy2(db_path, target)
    backups = sorted(backup_dir.glob("gallery-*.db"))
    for stale in backups[:-keep]:
        stale.unlink(missing_ok=True)
    return target


def run_migrations() -> None:
    inspector = inspect(engine)
    if "images" not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns("images")}
    statements = {
        "description": "ALTER TABLE images ADD COLUMN description VARCHAR(500) DEFAULT ''",
        "category_id": "ALTER TABLE images ADD COLUMN category_id INTEGER REFERENCES categories(id)",
        "deleted_at": "ALTER TABLE images ADD COLUMN deleted_at DATETIME",
        "set_id": "ALTER TABLE images ADD COLUMN set_id INTEGER REFERENCES image_sets(id)",
        "placeholder": "ALTER TABLE images ADD COLUMN placeholder TEXT DEFAULT ''",
    }
    with engine.begin() as connection:
        for column, statement in statements.items():
            if column not in existing:
                connection.execute(text(statement))

    if "banners" in inspector.get_table_names():
        banner_columns = {column["name"] for column in inspector.get_columns("banners")}
        if "placeholder" not in banner_columns:
            with engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE banners ADD COLUMN placeholder TEXT DEFAULT ''")
                )

    if "categories" in inspector.get_table_names():
        category_columns = {column["name"] for column in inspector.get_columns("categories")}
        category_statements = {
            "cover_stored_name": "ALTER TABLE categories ADD COLUMN cover_stored_name VARCHAR(128) DEFAULT ''",
            "cover_content_type": "ALTER TABLE categories ADD COLUMN cover_content_type VARCHAR(64) DEFAULT ''",
            "cover_placeholder": "ALTER TABLE categories ADD COLUMN cover_placeholder TEXT DEFAULT ''",
        }
        with engine.begin() as connection:
            for column, statement in category_statements.items():
                if column not in category_columns:
                    connection.execute(text(statement))

    if "site_config" in inspector.get_table_names():
        config_columns = {column["name"] for column in inspector.get_columns("site_config")}
        if "announcement_mode" not in config_columns:
            with engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE site_config ADD COLUMN announcement_mode VARCHAR(16) DEFAULT 'topbar'")
                )
