# Proposal: Align OpenSpecs with Clean Architecture

## Why
Current specifications contain "leaks" that violate Clean Architecture principles:
1. **Agent Coupling**: `agents/spec.md` mandates that agents handle hybrid search logic, whereas it should be an application-layer concern.
2. **Infrastructure Coupling**: `ingestion/spec.md` explicitly mentions `ChromaDB`, which couples the requirement to a specific vendor/technology.
3. **Layer Separation**: Architecture specs need to more clearly define that Search logic belongs to Use Cases, not Agent "tools".

## What Changes
- **agents/spec.md**: Update requirements to focus on agents as *consumers* of search capabilities, not implementers.
- **ingestion/spec.md**: Replace "ChromaDB" with "Vector Storage" or "Abstract Persistence" to maintain vendor neutrality.
- **architecture/spec.md**: Strengthen the enforcement of "Logic in Application Layer".

## Benefits
- **Vender Neutrality**: Allows changing the vector database (e.g., to Qdrant) without updating core specifications.
- **Testability**: Encourages testing business logic (Search) independently of the Agent framework.
- **Clarity**: Better separation of concerns makes the system easier to understand and maintain.
