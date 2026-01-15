import asyncio
from typing import List
from advence_rag.domain.entities import SearchResult
from advence_rag.application.use_cases.search import HybridSearchUseCase

async def test_rrf():
    # Mock results
    vector_results = [
        SearchResult(content="content1", metadata={}, id="doc1", score=0.9),
        SearchResult(content="content2", metadata={}, id="doc2", score=0.8),
        SearchResult(content="content3", metadata={}, id="doc3", score=0.7),
    ]
    
    keyword_results = [
        SearchResult(content="content2", metadata={}, id="doc2", score=10.0),
        SearchResult(content="content3", metadata={}, id="doc3", score=5.0),
        SearchResult(content="content4", metadata={}, id="doc4", score=2.0),
    ]
    
    # doc2: rank 2 (vector) + rank 1 (keyword) -> 1/(60+2) + 1/(60+1) = 0.016129 + 0.016393 = 0.032522
    # doc3: rank 3 (vector) + rank 2 (keyword) -> 1/(60+3) + 1/(60+2) = 0.015873 + 0.016129 = 0.032002
    # doc1: rank 1 (vector) + rank None (keyword) -> 1/(60+1) = 0.016393
    # doc4: rank None (vector) + rank 3 (keyword) -> 1/(60+3) = 0.015873
    
    use_case = HybridSearchUseCase(None, None)
    fused = use_case._reciprocal_rank_fusion([vector_results, keyword_results], top_k=10)
    
    print("Fused Results:")
    for i, res in enumerate(fused):
        print(f"{i+1}. ID: {res.id}, RRF Score: {res.score:.6f}")
        
    assert fused[0].id == "doc2"
    assert fused[1].id == "doc3"
    assert fused[2].id == "doc1"
    assert fused[3].id == "doc4"
    print("\n✅ RRF Fusion Logic Verified!")

if __name__ == "__main__":
    asyncio.run(test_rrf())
