# School Payments Backend

A robust, hex-architecture backend for managing Schools, Students, Invoices, and Payments, with a focus on reliable Account Statements.

## Features

- **Hexagonal Architecture**: Strict separation of concerns.
- **CQRS**: Validated Commands and Optimized Queries.
- **CRUD Operations**: Complete Create, Read, Update, Delete with Pagination.
- **Authentication**: JWT & RBAC (Admin, School, Student roles).
- **Account Statements**: Cached calculations with versioning strategy.
- **Resilience**: Redis Circuit Breaker for graceful degradation.
- **Observability**: Structured JSON logging with request tracing.

## Tech Stack

- Python 3.11+
- FastAPI
- PostgreSQL (Async SQLAlchemy 2.0)
- Redis
- Docker Compose

## Quick Start

1.  **Build and Run**:
    ```bash
    docker compose up --build
    ```

2.  **Verify**:
    - Health Check: `http://localhost:8000/health`
    - API Docs: `http://localhost:8000/docs`

## Testing

Runs unit tests inside the container.

```bash
docker compose exec api pytest
```

## Documentation

- [Architecture Reference](architecture.md)
- [API Test Cases (Manual)](docs/api-test-cases.md)
- [Decision Records](docs/decisions.md)
