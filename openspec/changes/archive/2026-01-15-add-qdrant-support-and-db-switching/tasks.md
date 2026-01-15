## 1. Foundation
- [x] 1.1 Add `qdrant-client` to optional dependencies in `pyproject.toml` <!-- id: 1 -->
- [x] 1.2 Update `Settings` to include `vector_db_type` and Qdrant config <!-- id: 2 -->

## 2. Infrastructure Refactoring
- [x] 2.1 Extract current Chroma logic into `ChromaRepository` <!-- id: 3 -->
- [x] 2.2 Implement `QdrantRepository` following the `KnowledgeBaseRepository` interface <!-- id: 4 -->
- [x] 2.3 Create a repository factory to handle instantiation at startup <!-- id: 5 -->

## 3. DevOps & Verification
- [x] 3.1 Update `docker-compose.yml` with optional Qdrant service <!-- id: 6 -->
- [x] 3.2 Create verification script for Qdrant storage/search <!-- id: 7 -->
- [x] 3.3 Update `TECHNICAL_BRIEF.md` with multi-DB capability <!-- id: 8 -->
