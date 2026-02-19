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
├── domain/          # Core business logic and entities
│   └── entities/    # Domain models (e.g., user.py)
└── presentation/    # API layer
    └── api.py       # FastAPI app and routes
```

**Key Points:**
- `domain/entities/` contains pure business objects with no framework dependencies
- `presentation/` handles HTTP concerns using FastAPI
- Entry point is `main.py` which imports the FastAPI app from `src.presentation.api`
- Expected future layers: `application/` (use cases), `infrastructure/` (DB, external services)

### Technology Stack
- **Framework**: FastAPI with Uvicorn ASGI server
- **Database**: MongoDB 7 with Motor (async driver expected for future implementation)
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
- Place new domain entities in `src/domain/entities/`
- Add API routes in `src/presentation/api.py` or create new router modules
- Future MongoDB integration should use Motor (async MongoDB driver for Python)
- Follow FastAPI async patterns (`async def` for route handlers)
- Container names follow pattern: `dailylog-{service}`
