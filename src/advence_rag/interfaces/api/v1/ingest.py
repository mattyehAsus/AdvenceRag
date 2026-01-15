from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import shutil
import os
from pathlib import Path
from typing import Any

from advence_rag.interfaces.api.v1.schemas import IngestResponse
from advence_rag.application.use_cases.ingest import IngestDocumentUseCase
from advence_rag.infrastructure.persistence.hybrid_repository import HybridKnowledgeBaseRepository
from advence_rag.domain.interfaces import KnowledgeBaseRepository
from advence_rag.config import get_settings

router = APIRouter()
settings = get_settings()

# Simple DI
def get_kb_repo() -> KnowledgeBaseRepository:
    return HybridKnowledgeBaseRepository()

def get_ingest_use_case(kb_repo: KnowledgeBaseRepository = Depends(get_kb_repo)):
    return IngestDocumentUseCase(kb_repo)

@router.post("/upload", response_model=IngestResponse)
async def upload_file(
    file: UploadFile = File(...)
):
    """Endpoint to upload a file for background ingestion."""
    file_path = settings.ingest_dir / file.filename
    
    try:
        # Avoid overwriting if you want, or just overwrite
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return IngestResponse(
            status="success",
            message=f"File {file.filename} uploaded to ingestion queue."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    ingest_use_case: IngestDocumentUseCase = Depends(get_ingest_use_case)
):
    """
    Endpoint to ingest a file into the RAG system immediately.
    WARNING: This requires heavy dependencies (docling/unstructured) in the current service.
    """
    file_path = settings.uploads_dir / file.filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        result = await ingest_use_case.execute(file_path)
        
        if result.get("status") == "success":
            return IngestResponse(
                status="success",
                added_count=len(result.get("ids", []))
            )
        else:
            return IngestResponse(
                status="error",
                error=result.get("error", "Unknown error")
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Optionally clean up the temporary file
        if file_path.exists():
            os.remove(file_path)
