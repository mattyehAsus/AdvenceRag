## Context
The system currently relies solely on ChromaDB. This change introduces a plugin-based architecture for the persistence layer.

## Goals
- Support switching between Chroma and Qdrant via `VECTOR_DB_TYPE`.
- Maintain unified `KnowledgeBaseRepository` interface.
- Ensure 100% functional parity between both database implementations.

## Design Decisions
1.  **Repository Factory**: We will use a factory function in the application startup or dependency injection layer to resolve the implementation.
2.  **Shared Vector Logic**: If possible, shared logic (like local BM25 ranking) will remain in the Repository layer to ensure consistency regardless of the vector engine.
3.  **Docker Profiles**: We will use Docker Compose profiles or commented-out service definitions to keep the default deployment lightweight while allowing "Qdrant Mode" with a single flag.

## Risks
- **Data Migration**: Switching databases does not automatically migrate data. Users must re-ingest documents when switching types. We MUST document this.
