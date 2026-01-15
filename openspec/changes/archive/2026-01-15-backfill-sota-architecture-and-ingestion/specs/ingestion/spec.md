## ADDED Requirements

### Requirement: Lifecycle Management for Ingested Files
The ingestion pipeline **MUST** automatically manage the lifecycle of processed files to prevent re-processing and maintain directory cleanliness.

#### Scenario: Successful Archiving
- **GIVEN** a file in the watched ingestion directory
- **WHEN** the file is successfully processed and indexed
- **THEN** the system MUST move the file to a `processed/` subdirectory.

#### Scenario: Failure Archiving
- **GIVEN** a file in the watched ingestion directory
- **WHEN** processing fails due to an error
- **THEN** the system MUST move the file to an `error/` subdirectory.

### Requirement: Diagnostic Logging for Ingestion Failures
For every document that fails processing, the system **SHALL** generate an associated diagnostic log.

#### Scenario: Error Log Generation
- **WHEN** a file is moved to the `error/` subdirectory
- **THEN** the system MUST create a corresponding `.log` file containing the specific error message and timestamp.

### Requirement: Immediate Ingestion Scan
The background ingestion scheduler **SHALL** perform an initial scan of the watch directory immediately upon service startup.

#### Scenario: Startup Processing
- **WHEN** the Ingest service starts
- **THEN** it MUST perform a full scan of the directory before entering the regular interval sleep cycle.
