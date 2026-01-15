# Proposal: RAG Agent Workflow Improvements

## Summary
Improve the RAG agent workflow to ensure reliable streaming output, correct agent orchestration, and accurate source citations.

## Problem Statement
1. **Hidden Streaming**: Output from `search_agent` was hidden in `<thought>` blocks.
2. **Missing Conclusion**: The pipeline sometimes ended without a final answer from `writer_agent`.
3. **Orchestration Unreliability**: LLM-based routing in `orchestrator_agent` was inconsistent.
4. **Unknown Sources**: Documents were cited as "unknown" in the final answer.

## Proposed Solution
1. **Sequential Pipeline**: Implement `rag_pipeline` using `SequentialAgent` to enforce Search -> Review -> Write.
2. **Forced Text Output**: Remove tools from `writer_agent` to force direct markdown streaming.
3. **Source Metadata**: Update `search_agent` to verify and output document metadata (filename/title) for citations.
4. **Configuration**: Add `RAG_PIPELINE_MODE` to switch between simple and full pipelines.

## Verification Plan
Verified via manual `curl` requests and log inspection that the full pipeline executes sequentially and outputs correct citations.
