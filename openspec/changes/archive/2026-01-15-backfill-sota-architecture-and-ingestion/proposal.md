# Change: Backfill SOTA Architecture and Ingestion Optimizations

## Why
The project has recently undergone significant architectural improvements to achieve SOTA RAG performance, including service splitting, automated archiving, and runtime optimizations. These changes were implemented to address image size issues and improve operational reliability, but they are not yet documented in the OpenSpec system.

## What Changes
- **Service Splitting**: Documented the separation into `search` (lightweight) and `ingest` (heavy-duty) Docker targets.
- **Automated Archiving**: Defined the requirements for moving processed files to `processed/` and failed files to `error/`.
- **Scheduler Optimizations**: Formalized the requirement for immediate scans on startup.
- **Diagnostic Logging**: Added requirements for per-file error logs in the ingestion pipeline.

## Impact
- **Affected specs**: `architecture`, `ingestion`.
- **Affected code**: `Dockerfile`, `docker-compose.yml`, `optimization.py`, `cli.py`.
