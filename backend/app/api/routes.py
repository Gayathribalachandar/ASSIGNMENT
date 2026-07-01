import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import (
    APIRouter,
    Request,
    UploadFile,
    File,
    HTTPException
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.services.candidate_service import CandidateService

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

candidate_service = CandidateService()

class TransformRequest(BaseModel):
    sources: List[Dict[str, Any]]
    config: Optional[Dict[str, Any]] = None

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the main upload page.
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )

from fastapi import UploadFile, File

@router.post("/process")
async def process_candidate(
    resume: UploadFile = File(...),
    structured_file: UploadFile = File(...)
):
    try:
        result = await candidate_service.process_uploads(
            [resume],
            [structured_file]
        )

        return JSONResponse(result)

    except Exception as e:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
@router.get("/candidate")
async def get_sample_candidate():
    """
    Returns the bundled sample candidate transformed from ATS JSON plus recruiter notes.
    """
    try:
        # Load sample files
        root = Path(__file__).resolve().parents[3]
        ats_path = root / "sample_data" / "ats" / "candidate.json"
        notes_path = root / "sample_data" / "resume" / "recruiter_notes.txt"
        
        if not ats_path.exists() or not notes_path.exists():
            # Try alternate path just in case
            ats_path = Path("../sample_data/ats/candidate.json")
            notes_path = Path("../sample_data/resume/recruiter_notes.txt")
            
        with open(ats_path, "r", encoding="utf-8") as f:
            ats = json.load(f)
        notes = notes_path.read_text(encoding="utf-8")
        
        sources = [
            {"type": "ats_json", "data": ats},
            {"type": "recruiter_notes", "data": {"text": notes}}
        ]
        
        result = CandidateService.transform(sources)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate sample candidate: {str(e)}"
        )

@router.post("/transform")
async def transform_sources(req: TransformRequest):
    """
    Transform custom candidate sources using the pipeline.
    """
    try:
        result = CandidateService.transform(req.sources, req.config)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )