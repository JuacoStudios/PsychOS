"""
FastAPI Main Application for PsycheOS.

Main entry point for the PsycheOS REST API.
Provides endpoints for accessing and manipulating the consciousness knowledge graph.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .endpoints import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Yields:
        None
    """
    # Startup
    logger.info("Starting PsycheOS API server")
    
    # Ensure data directories exist
    data_dirs = ["data/sources", "data/processed", "data/graph"]
    for dir_path in data_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {dir_path}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PsycheOS API server")


# Create FastAPI application
app = FastAPI(
    title="PsycheOS API",
    description="REST API for the PsycheOS consciousness knowledge graph",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint.
    
    Returns:
        Welcome message and API information
    """
    return {
        "message": "Welcome to PsycheOS API",
        "version": "0.1.0",
        "docs": "/docs",
        "api": "/api/v1",
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Health status of the API
    """
    return {
        "status": "healthy",
        "service": "PsycheOS API",
        "timestamp": "2024-01-01T00:00:00Z",  # Would use datetime in production
    }


@app.get("/info")
async def api_info() -> Dict[str, Dict]:
    """
    API information endpoint.
    
    Returns:
        Detailed information about the API
    """
    return {
        "api": {
            "name": "PsycheOS API",
            "version": "0.1.0",
            "description": "REST API for consciousness knowledge graph",
        },
        "endpoints": {
            "theories": "/api/v1/theories - List consciousness theories",
            "graph_stats": "/api/v1/graph/stats - Get graph statistics",
            "ingest_pdf": "/api/v1/ingest/pdf - Ingest PDF files",
            "ingest_video": "/api/v1/ingest/video - Ingest YouTube videos",
            "search": "/api/v1/search - Search knowledge graph",
        },
        "data": {
            "sources_dir": "data/sources",
            "processed_dir": "data/processed",
            "graph_dir": "data/graph",
        },
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting PsycheOS API server on http://localhost:8000")
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )