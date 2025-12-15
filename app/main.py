from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import settings
from app.api.v1.api import api_router
from app.middleware.security import SecurityMiddleware, setup_cors

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Set up CORS with security configuration
setup_cors(app)

# Create directories if they don't exist
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

assets_dir = Path("assets")
assets_dir.mkdir(exist_ok=True)

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "message": "Welcome to E-Commerce API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
