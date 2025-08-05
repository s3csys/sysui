from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import socket
import platform

from app.api.v1 import api_router
from app.api import setup as setup_router
from app.core.config import settings
from app.middleware import RateLimitMiddleware
from app.core.security import log_security_event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title=settings.SERVER_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)
    
    # Add exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )
    
    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} {response.status_code} "
            f"({process_time:.2f}s)"
        )
        return response
    
    # Add global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        # Log security event for unhandled exceptions
        log_security_event(
            "unhandled_exception",
            {
                "path": request.url.path,
                "method": request.method,
                "client_ip": request.client.host if request.client else "unknown",
                "exception_type": exc.__class__.__name__,
                "exception_message": str(exc)
            },
            request,
            level="error"
        )
        
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    
    # Include setup router with API_V1_STR prefix
    app.include_router(setup_router.router, prefix=settings.API_V1_STR)

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Add health check endpoint
    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    @app.get("/api/v1/status")
    def get_status():
        is_configured = os.path.exists('.env')
        return {"configured": is_configured}
    
    # Add startup event handler
    @app.on_event("startup")
    async def startup_event():
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        os_info = f"{platform.system()} {platform.release()}"
        
        log_security_event(
            "application_startup",
            {
                "hostname": hostname,
                "ip": ip,
                "os": os_info,
                "python_version": platform.python_version(),
                "app_version": settings.SERVER_NAME
            },
            level="info"
        )
        logger.info(f"Application started on {hostname} ({ip})")
    
    # Add shutdown event handler
    @app.on_event("shutdown")
    async def shutdown_event():
        hostname = socket.gethostname()
        
        log_security_event(
            "application_shutdown",
            {
                "hostname": hostname,
                "app_version": settings.SERVER_NAME
            },
            level="info"
        )
        logger.info("Application shutting down")
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)