# evaluation Specification

## Purpose
TBD - created by archiving change add-evaluation-framework. Update Purpose after archive.
## Requirements
### Requirement: Automated Evaluation
The system MUST support automated evaluation of agent responses against a predefined golden dataset.

#### Scenario: Successful Evaluation Run
- **WHEN** the evaluation script is executed with a valid golden dataset
- **THEN** it MUST run each test case through the orchestrator
- **AND** generate a report containing individual scores and overall metrics (pass rate, average score)

### Requirement: Golden Dataset Schema
The golden dataset MUST follow a structured format to allow programmatic processing.

#### Scenario: Dataset Validation
- **WHEN** loading the golden dataset
- **THEN** each entry MUST contain a unique `id`, a `query`, and the `expected_category` (e.g., ambiguous, clear, irrelevant)

