## ADDED Requirements

### Requirement: Environment-Specific Runtime Targets
The system **SHALL** support specialized runtime environments for Search and Ingestion to optimize resource utilization and deployment footprint.

#### Scenario: Lightweight Search Service
- **GIVEN** a deployment target focused on high-concurrency querying
- **WHEN** building the "search" target
- **THEN** the image MUST exclude heavy document processing binaries (e.g., Tesseract, Poppler)
- **AND** MUST provide a SOTA reranking capability using CPU-optimized frameworks.

#### Scenario: Heavy-Duty Ingestion Service
- **GIVEN** a deployment target focused on document processing
- **WHEN** building the "ingest" target
- **THEN** the image MUST include all necessary OCR and PDF parsing engines
- **AND** SHOULD support GPU acceleration for optimized throughput.
