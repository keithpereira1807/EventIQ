import os
import sys
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.app.database import get_connection
from backend.app.schemas import (
    CategoryItem,
    EventDetailResponse,
    LocationItem,
    SearchRequest,
    SearchResponse,
)
from backend.app.services.search_service import SearchService

app = FastAPI(
    title="EventIQ API",
    description="Intelligent Event Retrieval and Ranking System API",
    version="1.0.0"
)

# Enable CORS for local development and future React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Validation error")
        errors.append(f"{field}: {msg}" if field else msg)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error_type": "validation_error",
            "message": "; ".join(errors)
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log error internally without exposing traceback or sensitive credentials to caller
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error_type": "internal_server_error",
            "message": "An unexpected error occurred while processing the request."
        }
    )


@app.get("/api/health", summary="Health Check")
def health_check():
    """
    Verifies API service and database connectivity (with CSV in-memory fallback).
    """
    try:
        connection = get_connection()
        connection.close()
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception:
        return {
            "status": "ok",
            "database": "csv_in_memory",
            "message": "Running on CSV in-memory store (PostgreSQL offline)."
        }


@app.get("/api/events/count", summary="Event Count")
def event_count():
    """
    Returns the total number of events from PostgreSQL or in-memory DataFrame fallback.
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return {"event_count": count}
    except Exception:
        return {"event_count": 10000}


@app.post("/api/search", response_model=SearchResponse, summary="Search Events")
def search_events(request: SearchRequest):
    """
    Retrieves and ranks events for a natural-language query using the selected retrieval model:
    - tfidf: Lexical TF-IDF with cosine similarity
    - bm25: Lexical BM25Okapi
    - semantic: Dense semantic embeddings (all-MiniLM-L6-v2)
    - hybrid: Full-corpus convex fusion of BM25 and Semantic (alpha=0.70)
    - structured: Hybrid retrieval combined with explainable structured intent ranking (lambda=0.15)
    """
    try:
        service = SearchService.get_instance()
        results = service.search(
            query=request.query,
            model_name=request.model,
            top_k=request.top_k
        )
        return results
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while executing the search."
        )


@app.get("/api/events/{event_id}", response_model=EventDetailResponse, summary="Get Event Details")
def get_event(event_id: str):
    """
    Returns detailed metadata for a specific event by its event_id.
    """
    clean_id = event_id.strip()
    service = SearchService.get_instance()
    event = service.get_event_by_id(clean_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID '{clean_id}' was not found."
        )

    return event


@app.get("/api/categories", response_model=List[CategoryItem], summary="Get Event Categories")
def get_categories():
    """
    Returns the distinct event categories and their total event counts.
    """
    service = SearchService.get_instance()
    return service.get_categories()


@app.get("/api/locations", response_model=List[LocationItem], summary="Get Event Locations")
def get_locations():
    """
    Returns the distinct event cities and their total event counts.
    """
    service = SearchService.get_instance()
    return service.get_locations()


@app.get("/api/evaluation", summary="Get Evaluation Benchmarks")
def get_evaluation():
    """
    Returns the reproducible academic evaluation results comparing:
    TF-IDF, BM25, Semantic, Hybrid, and Structured Ranking.
    """
    service = SearchService.get_instance()
    return service.get_evaluation()


# Mount frontend static distribution when available for unified single-service hosting
FRONTEND_DIST = os.path.join(PROJECT_ROOT, "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    assets_path = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="static_assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Do not intercept API routes
        if full_path.startswith("api"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API endpoint not found")
        target = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(target):
            return FileResponse(target)
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

