# ================================================================
# normalize.py — ATILA Smart Ticket Normalization API Route
# ================================================================
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.services.normalizers import normalize_ticket, load_platform_map
import json, logging

router = APIRouter(prefix="/normalize", tags=["Normalization"])

# Load the platform map once at startup
try:
    PLATFORM_MAP = load_platform_map("config/platform_map.yaml")
except Exception as e:
    logging.error(f"Failed to load platform map: {e}")
    PLATFORM_MAP = {}

@router.post("/{source}")
async def normalize_source_ticket(source: str, request: Request):
    """
    Normalize any incoming raw ticket JSON into ATILA's Smart Table schema.

    Example:
    POST /normalize/github
    {
        "id": 123,
        "title": "Bug: login error",
        "body": "User cannot login",
        "state": "open",
        "assignee": {"login": "david"},
        "labels": [{"name": "bug"}],
        "repository": {"name": "mlops"}
    }
    """
    if not PLATFORM_MAP:
        raise HTTPException(status_code=500, detail="Platform map not loaded")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    source = source.lower().strip()
    if source not in PLATFORM_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported platform: {source}. Must be one of: {', '.join(PLATFORM_MAP.keys())}",
        )

    try:
        normalized = normalize_ticket(source, payload, PLATFORM_MAP)
        return JSONResponse(content=normalized)
    except Exception as e:
        logging.exception(f"Normalization error for source={source}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
