# Change: Add Evaluation Framework

## Why
The project lacks a standardized way to quantitatively evaluate the performance of the Multi-Agent RAG system across different versions and configurations. This framework provides automated testing against a golden dataset to ensure quality and prevent regressions.

## What Changes
- [NEW] Automated evaluation script `tests/evaluation/run_eval.py`.
- [NEW] Golden dataset `tests/evaluation/golden_dataset.json` containing ground truth mappings.
- [NEW] Scoring metrics (exact match, partial match) for agent responses.

## Impact
- Affected specs: `evaluation` (new capability)
- Affected code: `tests/evaluation/`
