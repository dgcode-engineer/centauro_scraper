from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class Product(BaseModel):
    nome: str | None = None
    image: str | None = None
    link: str | None = None
    tags: str | None = None
    preco_atual: float | None = None
    preco_antigo: float | None = None
    desconto_pct: int | None = None
    no_pix: bool | None = None
    parcelamento: str | None = None


class ScrapeRequest(BaseModel):
    query: str
    pages: int = 1


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    done = "done"
    error = "error"


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: list[Product] | None = None
    error: str | None = None
