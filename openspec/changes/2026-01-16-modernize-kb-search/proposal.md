# Proposal: Modernize Knowledge Base Search with BGE-M3 and Sparse Vectors

## Goal
To upgrade the RAG system's search capabilities from basic vector search + application-level RRF to a more robust, state-of-the-art hybrid search using Qdrant's native Sparse Vector support and the BGE-M3 all-in-one embedding model.

## Context
Current search implementation uses separate vector lookup and payload-based keyword filtering, merging results in the application layer. This approach is limited in handling Chinese/English mix and doesn't leverage advanced neural keyword weighting. Qdrant's sparse vector support combined with BGE-M3 allows for a more unified and accurate hybrid retrieval.

## Proposed Changes
- Introduce BGE-M3 model for both dense and sparse embedding generation.
- Enable Sparse Vector support in Qdrant repository.
- Upgrade Ingestion pipeline to generate and store sparse vectors.
- Simplify/Optimize search logic to leverage Qdrant's native hybrid retrieval (if applicable) or better coordinate dense/sparse scoring.

## Success Criteria
- [ ] Ingestion service can generate both dense and sparse vectors for new documents.
- [ ] Qdrant collection is configured with both dense and sparse vector parameters.
- [ ] Search retrieval performance (Recall@K) improves for keyword-intensive queries.
- [ ] System handles Chinese/English hybrid content more effectively without manual Jieba/HanLP tokenization.
- [ ] Support for dynamic hardware fallback (GPU/CPU) is implemented and verified.
