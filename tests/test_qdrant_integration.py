import asyncio
import logging
from advence_rag.domain.entities import Document
from advence_rag.infrastructure.persistence.repository_factory import get_repository
from advence_rag.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_qdrant_integration():
    settings = get_settings()
    if settings.vector_db_type != "qdrant":
        print(f"Skipping Qdrant test (Current DB: {settings.vector_db_type})")
        print("To test Qdrant, run: export VECTOR_DB_TYPE=qdrant")
        return

    logger.info("Initializing Repository (Factory Mode: Qdrant)")
    repo = get_repository()
    
    # 1. Add test documents
    docs = [
        Document(content="Qdrant is a vector database made in Rust.", metadata={"topic": "tech"}),
        Document(content="Python is a programming language used for AI.", metadata={"topic": "dev"}),
    ]
    
    logger.info("Adding documents...")
    res = await repo.add_documents(docs)
    logger.info(f"Add Result: {res}")
    
    # 2. Search Similar
    logger.info("Testing Search Similar...")
    results = await repo.search_similar("What is Rust used for?", top_k=2)
    for i, r in enumerate(results):
        print(f"Similar Result {i+1}: {r.content} (Score: {r.score:.4f})")
    
    # 3. Search Keyword
    logger.info("Testing Search Keyword...")
    results = await repo.search_keyword("Rust", top_k=1)
    for i, r in enumerate(results):
        print(f"Keyword Result {i+1}: {r.content} (Score: {r.score:.4f})")

    # 4. Cleanup/Delete
    if res.get("ids"):
        logger.info(f"Deleting documents: {res['ids']}")
        await repo.delete_documents(res["ids"])
    
    print("\n✅ Qdrant Integration Test Template Ready!")

if __name__ == "__main__":
    asyncio.run(test_qdrant_integration())
