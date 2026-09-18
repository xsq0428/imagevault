from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import image_store
from .database import Base, engine, run_migrations
from .routers import banners, categories, images, sets


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    run_migrations()
    image_store.ensure_dirs()
    yield


app = FastAPI(title="ImageVault API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(images.router)
app.include_router(sets.router)
app.include_router(categories.router)
app.include_router(banners.router)
