from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.logger import logger
from app.db.database import create_job, get_job, get_products, save_products, update_job_status
from app.models.product import JobResponse, JobStatus, ScrapeRequest
from app.scraper.centauro import run_scrape
from app.scraper.driver import create_driver

router = APIRouter(prefix="/scrape", tags=["scrape"])


# ── Background task ───────────────────────────────────────────────────────────

def _run_job(job_id: str, query: str, pages: int) -> None:
    update_job_status(job_id, JobStatus.running)
    driver = None
    try:
        driver = create_driver()
        products = run_scrape(driver, query, pages)
        save_products(job_id, products)
        update_job_status(job_id, JobStatus.done)
    except Exception as ex:
        logger.exception("Job falhou", job_id=job_id, error=str(ex))
        update_job_status(job_id, JobStatus.error, error=str(ex))
    finally:
        if driver:
            driver.quit()


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("", response_model=JobResponse, status_code=202)
def start_scrape(body: ScrapeRequest, background_tasks: BackgroundTasks) -> JobResponse:
    job_id = str(uuid.uuid4())
    create_job(job_id)
    background_tasks.add_task(_run_job, job_id, body.query, body.pages)
    logger.info("Job criado", job_id=job_id, query=body.query, pages=body.pages)
    return JobResponse(job_id=job_id, status=JobStatus.pending)


@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(job_id: str) -> JobResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job não encontrado")

    result = get_products(job_id) if job["status"] == JobStatus.done else None

    return JobResponse(
        job_id=job_id,
        status=job["status"],
        result=result,
        error=job["error"],
    )
