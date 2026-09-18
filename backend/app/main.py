from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import image_store
from .auth import ensure_default_admin
from .database import Base, SessionLocal, backup_database, engine, run_migrations
from .routers import auth, banners, categories, images, sets, site_config

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        try:
            response = await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404 and not path.startswith("api/"):
                return await super().get_response("index.html", scope)
            raise
        if response.status_code == 404 and not path.startswith("api/"):
            return await super().get_response("index.html", scope)
        return response


@asynccontextmanager
async def lifespan(_: FastAPI):
    backup_database()
    Base.metadata.create_all(bind=engine)
    run_migrations()
    image_store.ensure_dirs()
    with SessionLocal() as db:
        ensure_default_admin(db)
    yield


app = FastAPI(title="ImageVault API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(site_config.router)
app.include_router(images.router)
app.include_router(sets.router)
app.include_router(categories.router)
app.include_router(banners.router)

if FRONTEND_DIST.exists():
    app.mount("/", SPAStaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")
