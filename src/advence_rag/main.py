from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from advence_rag.interfaces.api.v1.chat import router as chat_router
from advence_rag.interfaces.api.v1.ingest import router as ingest_router
from advence_rag.config import get_settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("advence_rag")

settings = get_settings()

# Ensure GOOGLE_API_KEY is exported to os.environ for ADK to see it
import os
if settings.google_api_key:
    os.environ["GOOGLE_API_KEY"] = settings.google_api_key

app = FastAPI(
    title="Advence RAG API",
    description="Clean Architecture RAG Service with OpenAI Compatibility",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat_router, prefix="/v1", tags=["OpenAI"])
app.include_router(ingest_router, prefix="/api/v1", tags=["Ingest"])

@app.get("/")
async def root():
    return {
        "message": "Advence RAG API is running",
        "docs": "/docs",
        "openai_compatible": "/v1/chat/completions"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
