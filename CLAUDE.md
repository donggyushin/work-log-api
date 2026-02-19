# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based work/daily log API with MongoDB backend, containerized using Docker. The project uses Python 3.14 and `uv` as the package manager.

## Development Commands

### Environment Setup
```bash
# Copy environment template and configure
cp .env.example .env
# Edit .env with your MongoDB credentials
```

### Docker Container Management
```bash
make up          # Start all containers (API, MongoDB, Mongo Express)
make down        # Stop all containers
make restart     # Restart containers
make logs        # View real-time logs
make build       # Rebuild Docker images
make clean       # Remove all containers, images, and volumes
make mongo-shell # Access MongoDB shell
```

### Local Development
```bash
uv sync          # Install/sync dependencies
uv run main.py   # Run API server locally
```

### Service Endpoints
- API: http://localhost:8000/api/v1
- MongoDB Admin UI (Mongo Express): http://localhost:8081
- MongoDB: localhost:27017

## Architecture

### Clean Architecture Pattern
The codebase follows clean architecture with clear separation of concerns:

```
src/
├── domain/              # Core business logic (no framework dependencies)
│   ├── entities/        # Domain models (User)
│   ├── interfaces/      # Abstract interfaces (repositories, providers)
│   ├── services/        # Business logic services (AuthService)
│   └── exceptions.py    # Domain-specific exceptions
├── infrastructure/      # External concerns (DB, crypto, JWT)
│   ├── database.py      # MongoDB connection management
│   ├── mongo_*_repository.py  # Repository implementations
│   ├── bcrypt_hasher.py       # Password hashing
│   └── py_jwt_provider.py     # JWT token generation
└── presentation/        # HTTP/API layer
    └── api.py           # FastAPI routes
```

**Key Architectural Patterns:**

1. **Dependency Inversion**: Domain layer defines interfaces (`UserRepository`, `Hasher`, `JWTProvider`, `RefreshTokenRepository`), infrastructure implements them
2. **Repository Pattern**: Data access abstracted via repository interfaces
   - MongoDB `_id` ↔ User `id` conversion happens in repositories
   - Use `model_dump(exclude={"id"})` when inserting, convert `_id` to `id` string when reading
3. **Service Layer**: `AuthService` contains registration business logic, depends only on interfaces
4. **Domain Exceptions**: Business rule violations raise domain exceptions (`EmailAlreadyExistsError`, `PasswordLengthNotEnoughError`)

**MongoDB Integration Pattern:**
- Repositories convert between MongoDB documents (with `_id` as ObjectId) and domain entities (with `id` as str)
- When creating: exclude `id`, get `inserted_id` from result, return entity with `id=str(result.inserted_id)`
- When reading: `result.pop("_id")` and assign to `result["id"] = str(_id)` before constructing entity

### Technology Stack
- **Framework**: FastAPI with Uvicorn ASGI server
- **Database**: MongoDB 7 with Motor (async MongoDB driver)
- **Authentication**: JWT tokens (access + refresh), bcrypt password hashing
- **Package Manager**: uv (fast Python package manager)
- **Python Version**: 3.14
- **Containerization**: Docker + Docker Compose

### Container Architecture
Three services run in Docker Compose:
1. **api** (`dailylog`): FastAPI application with hot-reload via volume mounts
2. **mongodb** (`dailylog-mongodb`): MongoDB 7 database with persistent volume
3. **mongo-express** (`dailylog-mongo-express`): Web-based MongoDB admin interface

Volume mounts for development:
- `./src:/app/src` - Enables hot-reload of source code
- `./main.py:/app/main.py` - Enables hot-reload of entry point

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on pushes/PRs to `main`:
1. Creates test environment with `.env` file
2. Starts Docker containers via `make up`
3. Verifies all three containers are running
4. Tests API endpoint (`/api/v1`) returns expected response
5. Outputs container logs on failure

## Environment Variables

Required variables in `.env`:
- `MONGO_INITDB_ROOT_USERNAME` - MongoDB root username
- `MONGO_INITDB_ROOT_PASSWORD` - MongoDB root password
- `MONGO_PORT` - MongoDB port (default: 27017)
- `MONGO_EXPRESS_PORT` - Mongo Express UI port (default: 8081)
- `MONGO_EXPRESS_USERNAME` - Mongo Express login username
- `MONGO_EXPRESS_PASSWORD` - Mongo Express login password

## Code Conventions

When extending this codebase:
- **Domain Layer**: Define interfaces in `src/domain/interfaces/`, implement in `infrastructure/`
- **Entities**: Place new domain entities in `src/domain/entities/` (pure Pydantic models, no DB concerns)
- **Services**: Business logic goes in `src/domain/services/`, depends only on domain interfaces
- **Repositories**: Implement repository interfaces in `infrastructure/mongo_*_repository.py`
  - Collection name should match entity (e.g., `users` for User, `refresh_tokens` for RefreshToken)
  - Always handle `_id` ↔ `id` conversion at repository boundaries
- **API Routes**: Add routes in `src/presentation/api.py` or create new router modules
- **Exceptions**: Domain business rule violations raise exceptions from `src/domain/exceptions.py`
- Follow FastAPI async patterns (`async def` for route handlers and repository methods)
- Container names follow pattern: `dailylog-{service}`
