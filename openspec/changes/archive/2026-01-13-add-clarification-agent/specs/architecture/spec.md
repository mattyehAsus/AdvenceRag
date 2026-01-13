# Architecture Specification Delta

## ADDED Requirements

### Requirement: Intelligent Query Handling
The system MUST be able to handle ambiguous queries by asking clarifying questions instead of guessing.

#### Scenario: Ambiguity Detection
- **GIVEN** a user query that is vague or missing key entities (e.g., "Where is it?")
- **WHEN** the Orchestrator processes the query
- **THEN** it MUST route the request to a `Clarification Agent`
- **AND** the system MUST return a clarifying question to the user.
