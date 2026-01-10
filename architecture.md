# Architecture Definition: School Payments Backend

**Status**: APPROVED
**Date**: 2026-01-10
**Version**: 1.0

## 1. Overview & Objectives

The goal is to provide a robust, maintainable backend for managing Schools, Students, Invoices, and Payments. The core value prop is generating accurate and efficient Account Statements.

**Key Engineering Values**:
- **Strict Hexagonal Architecture**: Isolate domain from infrastructure.
- **CQRS**: Segregate write (Command) and read (Query) models to optimize for complex reporting (Statements) vs transactional integrity (Payments).
- **Resilience**: Graceful degradation via Circuit Breakers (Redis).
- **Observability**: Distributed tracing-ready logs with correlation IDs.

## 2. Global Architecture

The system follows a strict **Ports & Adapters (Hexagonal)** layout.

### Module Boundaries

```mermaid
graph TD
    subgraph "Domain (Core)"
        Entities
        ValueObjects
        DomainServices
    end

    subgraph "Application (Use Cases)"
        Commands[Command Handlers]
        Queries[Query Handlers]
        Ports[Ports / Interfaces]
        Commands --> Entities
        Queries --> Entities
    end

    subgraph "Adapters (Infrastructure)"
        Web[FastAPI]
        Persistence[SQLAlchemy/Postgres]
        Cache[Redis]
        Obs[Observability]
    end

    Web --> Commands
    Web --> Queries
    Commands --> Ports
    Queries --> Ports
    Persistence ..|> Ports
    Cache ..|> Ports
```

### Directory Structure

```text
src/
├── domain/            # Pure Python business logic. NO imports from adapters/frameworks.
│   ├── entities.py
│   ├── value_objects.py
│   └── exceptions.py
├── application/       # Orchestration. Depends only on Domain.
│   ├── commands/
│   ├── queries/
│   └── ports/         # Interfaces (Repositories, Cache, UoW)
├── adapters/          # Implementation details.
│   ├── web/           # FastAPI routers, schemas
│   ├── persistence/   # SQLAlchemy models, repositories
│   ├── cache/         # Redis client, Circuit Breaker
│   └── resilience/    # Circuit Breaker implementation
└── main.py            # Entrypoint, DI container wiring
```

## 3. CQRS Strategy

- **Commands**: Handle side effects.
    - Return: `CommandResult` (usually ID of created entity or Success).
    - Writes to: Primary DB (PostgreSQL).
    - Invalidate: Related Cache entries.
- **Queries**: Handle reads.
    - Return: DTOs customized for the client view.
    - Reads from: Primary DB (optimized queries) or Cache (Redis).

**Justification**: Account statements require aggregating multiple invoices and payments. Keeping read logic separate allows for optimization (e.g., raw SQL or specialized views) without polluting domain entities with display logic.

## 4. Domain Modeling

### Entities & Aggregates

*   **School**: Root.
*   **Student**: Belongs to School.
*   **Invoice**: Root of financial transaction.
    *   State Machine: `PENDING` -> `PARTIALLY_PAID` -> `PAID`.
    *   `OVERDUE` is a computed state based on `due_date` and `current_time`.
*   **Payment**: Immutable record linked to Invoice.

### Invariants

1.  **Payment Validation**: `Payment.amount` <= `Invoice.amount_remaining`.
2.  **Integrity**: A Student with existing Invoices cannot be hard-deleted (Soft delete or blocked).
3.  **Currency**: Multi-currency support implied by "Currency" field, but MVP assumes consistency per invoice.

## 5. Caching Strategy (Redis)

Goal: Offload expensive Account Statement generation.

- **Key Schema**:
    - `school:{id}:statement:v{version}`
    - `student:{id}:statement:v{version}`
- **Versioning**:
    - A specific `version` counter is stored in Redis for each School/Student.
    - **Write Path**: When a Command (Create Invoice, Add Payment) succeeds, it increments the relevant version counter in Redis.
    - **Read Path**: Query fetches current version -> builds key -> checks cache. If miss -> DB Query -> Set Cache.
- **TTL**: 60 seconds. Rationale: Statements are high-read, but financial data must be fresh. 60s is a balance between load reduction and eventual consistency.
- **Serialization**: JSON.

## 6. Resilience & Circuit Breaker

To prevent cascading failures when Redis is down:

- **Component**: `RedisCircuitBreaker`.
- **States**:
    - `CLOSED`: Normal operation.
    - `OPEN`: Failures exceeded threshold. Fast fail.
    - `HALF_OPEN`: Test probe.
- **Fallback**: If Circuit is OPEN or Redis call fails, the Query Handler **must** transparently fallback to fetching data directly from PostgreSQL. The API client should NOT perceive the failure (Degraded Mode).

## 7. Observability & Logging

- **Format**: JSON Structured Logging.
- **Context**: Every request generates a `request_id`.
- **Propagation**: `request_id` must be passed via `contextvars` to all layers.
- **Fields**:
    - `level`, `timestamp`, `message`, `service`, `request_id`, `trace_id`.
    - `latency_ms` (in middleware).

## 8. Definition of Done

- [ ] `docker compose up` runs without errors.
- [ ] API responds to all defined endpoints.
- [ ] Migrations applied automatically or via documented command.
- [ ] Unit tests pass (Pytest).
- [ ] Manual verification via `docs/api-test-cases.md` is successful.
