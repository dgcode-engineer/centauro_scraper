from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.products import router as scrape_router
from app.db.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Centauro Scraper API", version="0.1.0", lifespan=lifespan)

app.include_router(scrape_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
