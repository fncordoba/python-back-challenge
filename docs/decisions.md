# Architecture Decision Records

## ADR 001: Hexagonal Architecture
**Status**: Accepted
**Context**: We need a system that decouples business logic from frameworks to ensure long-term maintainability and testability.
**Decision**: Use Hexagonal Architecture (Ports & Adapters).
**Consequences**: extra boilerplate for DTOs and Adapters, but clear boundaries.

## ADR 002: CQRS for Account Statements
**Status**: Accepted
**Context**: Generating account statements requires aggregating data from invoices and payments. Doing this on the fly with ORM objects is inefficient.
**Decision**: Separate Write model (ORM) from Read model (Optimized SQL + DTOs).
**Consequences**: Reads are fast; complexity in maintaining two models.

## ADR 003: Redis Circuit Breaker
**Status**: Accepted
**Context**: Redis is used for caching statements. If Redis fails, the API must not crash.
**Decision**: Wrap Redis calls in a homemade Circuit Breaker. Fallback to DB query transparently.
**Consequences**: System is resilient to cache layer failure.
