from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

from app.models.product import Product

import os
_default_db = Path(__file__).parent.parent.parent / "scraper.db"
DB_PATH = Path(os.getenv("DB_PATH", str(_default_db)))

_DDL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS jobs (
    id         TEXT PRIMARY KEY,
    status     TEXT NOT NULL,
    error      TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id       TEXT    NOT NULL REFERENCES jobs(id),
    nome         TEXT,
    image        TEXT,
    link         TEXT,
    tags         TEXT,
    preco_atual  REAL,
    preco_antigo REAL,
    desconto_pct INTEGER,
    no_pix       INTEGER,
    parcelamento TEXT
);
"""


@contextmanager
def _conn() -> Generator[sqlite3.Connection, None, None]:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def init_db() -> None:
    with _conn() as con:
        con.executescript(_DDL)


# ── Jobs ──────────────────────────────────────────────────────────────────────

def create_job(job_id: str) -> None:
    with _conn() as con:
        con.execute(
            "INSERT INTO jobs (id, status, created_at) VALUES (?, 'pending', ?)",
            (job_id, datetime.now(timezone.utc).isoformat()),
        )


def update_job_status(job_id: str, status: str, error: str | None = None) -> None:
    with _conn() as con:
        con.execute(
            "UPDATE jobs SET status = ?, error = ? WHERE id = ?",
            (status, error, job_id),
        )


def get_job(job_id: str) -> dict | None:
    with _conn() as con:
        row = con.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None


# ── Products ──────────────────────────────────────────────────────────────────

def save_products(job_id: str, products: list[Product]) -> None:
    rows = [
        (
            job_id,
            p.nome, p.image, p.link, p.tags,
            p.preco_atual, p.preco_antigo, p.desconto_pct,
            int(p.no_pix) if p.no_pix is not None else None,
            p.parcelamento,
        )
        for p in products
    ]
    with _conn() as con:
        con.executemany(
            """INSERT INTO products
               (job_id, nome, image, link, tags, preco_atual, preco_antigo, desconto_pct, no_pix, parcelamento)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )


def get_products(job_id: str) -> list[Product]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM products WHERE job_id = ?", (job_id,)
        ).fetchall()
    return [
        Product(
            nome=r["nome"], image=r["image"], link=r["link"], tags=r["tags"],
            preco_atual=r["preco_atual"], preco_antigo=r["preco_antigo"],
            desconto_pct=r["desconto_pct"],
            no_pix=bool(r["no_pix"]) if r["no_pix"] is not None else None,
            parcelamento=r["parcelamento"],
        )
        for r in rows
    ]
