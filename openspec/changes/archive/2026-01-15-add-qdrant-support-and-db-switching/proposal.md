# Change: Add Qdrant Support and Multi-DB Switching

## Why
As the project moves towards production scale, ChromaDB (while excellent for local development) may face performance or scalability limitations. Qdrant offers superior scalability, gRPC support, and industrial-grade features. By implementing a switchable architecture, we allow users to choose the right engine for their scale without changing core logic, adhering to Clean Architecture principles.

## What Changes
- **Infrastructure Layer**: Implement `QdrantRepository` as a new implementation of `KnowledgeBaseRepository`.
- **Abstraction**: Refactor existing Chroma logic into a dedicated `ChromaRepository`.
- **Configuration**: Add `VECTOR_DB_TYPE` and `QDRANT_URL/API_KEY` to settings.
- **Orchestration**: Add a Qdrant service to `docker-compose.yml` (optional/disabled by default).
- **Factory Pattern**: Implement a provider/factory function to inject the correct repository based on configuration.

## Impact
- **Affected specs**: `architecture` (multi-DB support), `ingestion` (compatibility).
- **Affected code**: `settings.py`, `infrastructure/persistence/`, `dependencies.py` (if exists).
- **Breaking changes**: None, fallback defaults to Chroma.
