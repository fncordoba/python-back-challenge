import structlog
import uuid
import time
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

# Context Vars
request_id_var = ContextVar("request_id", default=None)
trace_id_var = ContextVar("trace_id", default=None)

# Configure Structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        req_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
        
        request_id_var.set(req_id)
        trace_id_var.set(trace_id)
        
        # Log Request (minimal)
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            request_id=req_id,
            trace_id=trace_id
        )
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            logger.info(
                "request_completed",
                status_code=response.status_code,
                latency_ms=process_time,
                request_id=req_id
            )
            
            response.headers["X-Request-Id"] = req_id
            return response
            
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                "request_failed",
                error=str(e),
                latency_ms=process_time,
                request_id=req_id
            )
            raise e
