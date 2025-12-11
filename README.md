# Loan Application Processing Service

A FastAPI microservice for processing loan application

## Architecture

```
src/
├── core/                           # Configuration
│   └── config/                     # Split by concern (app, db, redis, kafka, loan)
│
├── domain/                         # Inner layer (pure business logic, no external deps)
│   ├── ports/                      # Abstract interfaces
│   │   ├── repository.py           # BaseRepository[T]
│   │   ├── cache.py                # Cache
│   │   ├── message_broker.py       # MessageBroker
│   │   └── message_consumer.py     # MessageConsumer
│   ├── exceptions.py               # Domain exceptions
│   └── applications/loan/          # Loan domain
│       ├── entity.py               # LoanApplication dataclass
│       ├── value_objects.py        # LoanApplicationStatus enum
│       ├── ports.py                # LoanApplicationRepository
│       ├── processor.py            # Business rules + LoanProcessingRules
│       ├── use_cases.py            # Application services
│       └── cached_repository.py    # Decorator pattern for caching
│
├── infra/                          # Outer layer (implementations)
│   ├── db/
│   │   ├── session.py              # SQLAlchemy async setup
│   │   ├── migrations/             # Alembic migrations
│   │   └── loan_application/
│   │       ├── model.py            # ORM model
│   │       └── repository.py       # PostgreSQL implementation
│   ├── cache/
│   │   └── redis.py                # Redis implementation
│   └── messaging/
│       └── kafka.py                # Kafka producer/consumer
│
├── api/                            # HTTP interface layer
│   ├── schemas.py                  # Pydantic request/response models
│   ├── dependencies.py             # Dependency injection wiring
│   └── v1/
│       └── applications.py         # ApplicationController
│
├── consumer/                       # Kafka consumer service
│   ├── dependencies.py             # Consumer DI wiring
│   └── main.py                     # Consumer entrypoint
│
└── main.py                         # FastAPI entrypoint
```

## Clean Architecture

| Layer | Dependencies | Notes |
|-------|-------------|-------|
| **Domain** | None (pure Python) | Business logic, no imports from core/infra/api |
| **Infrastructure** | Domain ports, Core | Implements domain interfaces |
| **API/Consumer** | Domain, Infra, Core | Wires everything via dependency injection |

**Key principle:** Dependencies point inward. Domain knows nothing about databases, caching, or HTTP.


## API Endpoints

```
POST /api/v1/applications
{
    "applicant_id": "user_123",
    "amount": 10000,
    "term_months": 12
}
→ 202 Accepted (queued for async processing)

GET /api/v1/applications/{applicant_id}
→ 200 OK (returns status from cache/database)

```

## Processing Flow

```
1. API receives request
2. Domain processor validates (applicant_id, amount, term)
3. Published to Kafka (key=applicant_id for ordering)
4. Consumer picks up message
5. Domain processor determines status (approved/rejected)
6. Saved to PostgreSQL via CachedRepository
7. Cached in Redis for fast lookups
```

## Running

```bash
# Start all services (API, Consumer, PostgreSQL, Redis, Kafka)
docker-compose up --build

# Or run in background
docker-compose up -d --build

# View logs
docker-compose logs -f api
docker-compose logs -f consumer

# Stop all
docker-compose down
```

**Access:**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

## Database Migrations

```bash
# Run inside api container
docker-compose exec api alembic upgrade head

# Generate new migration
docker-compose exec api alembic revision --autogenerate -m "description"
```

## Configuration

All settings via environment variables (see `env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka brokers |
| `LOAN_APPROVAL_THRESHOLD` | `50000` | Auto-approve below this |
| `CACHE_TTL_SECONDS` | `3600` | Redis cache TTL |

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Unit tests only
pytest tests/unit/
```

## Project Decisions

1. **Config split by concern** - `database.py`, `redis.py`, `kafka.py`, `loan.py`
2. **Domain purity** - No settings imports in domain; rules injected via `LoanProcessingRules`
3. **Cached decorator in domain** - Only depends on domain ports, not infra
4. **Consumer as separate service** - Scales independently, shares domain code
5. **Key-based Kafka partitioning** - Messages for same applicant go to same partition
