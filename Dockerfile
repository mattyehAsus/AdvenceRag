# --------------------------------
# Stage 1: Base (Shared OS dependencies)
# --------------------------------
FROM python:3.11-slim AS base

WORKDIR /app

# Install common system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Force uv to use our pre-built venv and avoid project discovery
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# --------------------------------
# Stage 2a: Search Builder
FROM base AS builder-search
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv /opt/venv && \
    VIRTUAL_ENV=/opt/venv uv pip install --index-strategy unsafe-best-match --extra-index-url https://download.pytorch.org/whl/cpu ".[search]"

# --------------------------------
# Stage 2b: Ingest Builder
FROM base AS builder-ingest
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv /opt/venv && \
    VIRTUAL_ENV=/opt/venv uv pip install ".[ingest,rerank]"

# --------------------------------
# Stage 3: Search Runtime
FROM base AS search

# Copy venv from builder
COPY --from=builder-search /opt/venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source code
COPY src/ ./src/
COPY pyproject.toml ./
RUN mkdir -p /app/data/chroma /app/.sessions

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the FastAPI application
CMD ["python", "-m", "uvicorn", "advence_rag.main:app", "--host", "0.0.0.0", "--port", "8000"]

# --------------------------------
# Stage 4: Ingest Runtime
FROM base AS ingest

# Install heavy system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils tesseract-ocr libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# Copy venv from builder
COPY --from=builder-ingest /opt/venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source code
COPY src/ ./src/
COPY pyproject.toml ./
RUN mkdir -p /app/data/ingest /app/data/chroma /app/.sessions

# Default to running the background scheduler directly
CMD ["python", "-m", "advence_rag.cli", "scheduler", "--watch", "/app/data/ingest"]
