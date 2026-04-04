import logging
import os
import time
import uuid

from app.logging_ext import set_request_id, setup_logging

setup_logging(os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("aris.worker")


def process_job(job_id: str, parent_request_id: str | None = None):
    rid = set_request_id(parent_request_id or str(uuid.uuid4()))
    start = time.perf_counter()
    try:
        # simulate work
        time.sleep(0.05)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "job_completed",
            extra={
                "event": "worker_job",
                "request_id": rid,
                "job_id": job_id,
                "status_code": 200,
                "duration_ms": duration_ms,
            },
        )
    except Exception:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.exception(
            "job_failed",
            extra={
                "event": "worker_job_error",
                "request_id": rid,
                "job_id": job_id,
                "status_code": 500,
                "duration_ms": duration_ms,
            },
        )
        raise


if __name__ == "__main__":
    logger.info("worker_started", extra={"event": "worker_startup", "request_id": ""})
    # demo loop
    n = 0
    while True:
        n += 1
        process_job(job_id=f"job-{n}")
        time.sleep(2)