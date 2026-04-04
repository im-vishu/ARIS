import time
import logging
from fastapi import FastAPI, Request

logger = logging.getLogger("aris.request")


def install_request_logging(app: FastAPI) -> None:
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        request_id = getattr(request.state, "request_id", None)

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                "request_complete",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.url.query),
                    "status_code": status_code if "status_code" in locals() else 500,
                    "duration_ms": duration_ms,
                    "client_ip": request.client.host if request.client else None,
                    "request_id": request_id,
                },
            )