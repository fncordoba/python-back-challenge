from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.adapters.web.handlers import router as api_router
from src.adapters.web.auth_handlers import router as auth_router
from src.adapters.observability import ObservabilityMiddleware
from src.domain.exceptions import DomainError

def create_app() -> FastAPI:
    app = FastAPI(
        title="School Payments API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Middleware
    app.add_middleware(ObservabilityMiddleware)

    # Exception Handlers
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=400,
            content={
                "error_code": exc.__class__.__name__,
                "message": str(exc),
                "request_id": request.headers.get("X-Request-Id")
            }
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "InternalServerError",
                "message": str(exc),
                "request_id": request.headers.get("X-Request-Id")
            }
        )

    # Routes
    app.include_router(auth_router)
    app.include_router(api_router)
    
    return app
