# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based AI-powered diary/daily log API with MongoDB backend, containerized using Docker. The project uses Python 3.14 and `uv` as the package manager.

**Core Features:**
- User authentication (JWT-based with access/refresh tokens)
- Auto-generated user nicknames (형용사 + 명사 pattern, e.g., "행복한루피")
- Email verification via Resend
- AI-powered diary writing using Anthropic Claude (Sonnet 4.5)
- Conversational diary creation through chat sessions
- AI generates diary entries in the style of Korean author Lee Yeongdo (이영도)

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
make typecheck   # Run mypy type checking
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
│   ├── entities/        # Domain models (User, ChatMessage, ChatSession, Diary)
│   ├── interfaces/      # Abstract interfaces (repositories, providers, AI chatbot)
│   ├── services/        # Business logic services (AuthService, DiaryService)
│   └── exceptions.py    # Domain-specific exceptions
├── infrastructure/      # External concerns (DB, crypto, JWT, AI)
│   ├── database.py      # MongoDB connection management
│   ├── mongo_*_repository.py  # Repository implementations
│   ├── bcrypt_hasher.py       # Password hashing
│   ├── py_jwt_provider.py     # JWT token generation
│   ├── anthropic_ai_chat_bot.py  # Anthropic Claude integration
│   └── resend_email_sender.py    # Email sending via Resend
└── presentation/        # HTTP/API layer
    ├── api.py           # FastAPI routes
    └── dependencies.py  # Dependency injection setup
```

**Key Architectural Patterns:**

1. **Dependency Inversion**: Domain layer defines interfaces, infrastructure implements them
   - Repositories: `UserRepository`, `ChatRepository`, `DiaryRepository`, `RefreshTokenRepository`
   - Providers: `Hasher`, `JWTProvider`, `VerificationCodeGenerator`, `RandomNameGenerator`
   - External services: `AIChatBot`, `EmailSender`
2. **Repository Pattern**: Data access abstracted via repository interfaces
   - MongoDB `_id` ↔ entity `id` conversion happens in repositories
   - Use `model_dump(exclude={"id"})` when inserting, convert `_id` to `id` string when reading
   - Subdocuments in arrays (e.g., messages in ChatSession) get `ObjectId()` generated explicitly
3. **Service Layer**: Business logic in services, depends only on domain interfaces
   - `AuthService`: User registration (with auto-generated nicknames), login, token refresh
   - `EmailVerificationService`: Send/verify email codes
   - `DiaryService`: AI chat session management, diary generation
4. **Domain Exceptions**: Business rule violations raise domain exceptions (`EmailAlreadyExistsError`, `NotFoundError`, `ExpiredError`)

**MongoDB Integration Pattern:**
- Repositories convert between MongoDB documents (with `_id` as ObjectId) and domain entities (with `id` as str)
- When creating: exclude `id`, get `inserted_id` from result, return entity with `id=str(result.inserted_id)`
- When reading: `result.pop("_id")` and assign to `result["id"] = str(_id)` before constructing entity
- When adding to arrays: use `$push` operator with explicit `ObjectId()` for subdocuments
  ```python
  message_dict = message.model_dump(exclude={"id"})
  message_dict["_id"] = ObjectId()
  await collection.update_one({"_id": ObjectId(session.id)}, {"$push": {"messages": message_dict}})
  ```

**AI Chatbot Integration Pattern:**
- `AIChatBot` interface abstracts AI provider (currently Anthropic Claude)
- `DiaryService` orchestrates chat sessions and diary generation
- System prompts define AI behavior (e.g., Lee Yeongdo writing style)
- AI responses parsed using regex patterns for structured output:
  ```
  [TITLE_START]제목[TITLE_END]
  [CONTENT_START]내용[CONTENT_END]
  ```

### Technology Stack
- **Framework**: FastAPI with Uvicorn ASGI server
- **Database**: MongoDB 7 with Motor (async MongoDB driver)
- **Authentication**: JWT tokens (access + refresh), bcrypt password hashing
- **AI**: Anthropic Claude API (claude-sonnet-4-5-20250929)
- **Email**: Resend API for email verification
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
1. **Type Check Job**: Runs mypy type checking first to catch type errors early
2. **Docker Test Job** (runs after type check passes):
   - Creates test environment with `.env` file
   - Starts Docker containers via `make up`
   - Verifies all three containers are running
   - Tests API endpoint (`/api/v1`) returns expected response
   - Outputs container logs on failure

## Type Checking

The project uses **mypy** for static type checking to catch errors before runtime:

```bash
make typecheck              # Run type checking locally
uv run mypy src/ --pretty   # Direct mypy command
```

**Configuration** (in `pyproject.toml`):
- `ignore_missing_imports = true` - External libraries without type stubs are ignored
- `check_untyped_defs = true` - Check function bodies even without type annotations
- `no_implicit_optional = true` - Require explicit `Optional[]` for nullable parameters
- `warn_unreachable = true` - Warn about unreachable code

**When to run:**
- Before committing code changes
- After adding new dependencies to services
- When modifying dependency injection in `dependencies.py`

Type checking runs automatically in CI and will block PRs if errors are found.

## Environment Variables

Required variables in `.env`:
- `JWT_SECRET_KEY` - Secret key for JWT token signing
- `MONGO_INITDB_ROOT_USERNAME` - MongoDB root username
- `MONGO_INITDB_ROOT_PASSWORD` - MongoDB root password
- `MONGO_PORT` - MongoDB port (default: 27017)
- `MONGO_EXPRESS_PORT` - Mongo Express UI port (default: 8081)
- `MONGO_EXPRESS_USERNAME` - Mongo Express login username
- `MONGO_EXPRESS_PASSWORD` - Mongo Express login password
- `RESEND_API_KEY` - Resend API key for email verification
- `ANTHROPIC_API_KEY` - Anthropic API key for Claude AI integration

## Code Conventions

When extending this codebase:
- **Domain Layer**: Define interfaces in `src/domain/interfaces/`, implement in `infrastructure/`
- **Entities**: Place new domain entities in `src/domain/entities/` (pure Pydantic models, no DB concerns)
- **Services**: Business logic goes in `src/domain/services/`, depends only on domain interfaces
- **Repositories**: Implement repository interfaces in `infrastructure/mongo_*_repository.py`
  - Collection name should match entity plural (e.g., `users`, `refresh_tokens`, `chats`, `diaries`)
  - Always handle `_id` ↔ `id` conversion at repository boundaries
  - For subdocuments in arrays, generate `ObjectId()` explicitly and use `$push`
- **API Routes**: Add routes in `src/presentation/api.py` or create new router modules
  - Use `Depends()` for dependency injection from `src/presentation/dependencies.py`
  - Handle domain exceptions with try/except, convert to HTTPException with appropriate status codes
  - **CRITICAL**: When adding dependencies to a service constructor, ALWAYS update the corresponding factory function in `dependencies.py`. Type checking will catch this mismatch.
- **Exceptions**: Domain business rule violations raise exceptions from `src/domain/exceptions.py`
  - Common exceptions: `NotFoundError`, `NotCorrectError`, `ExpiredError`, `EmailAlreadyExistsError`
  - Always import domain exceptions, not external library exceptions (e.g., NOT `from anthropic import NotFoundError`)
- Follow FastAPI async patterns (`async def` for route handlers and repository methods)
- Container names follow pattern: `dailylog-{service}`

## Domain Models

**Core Entities:**
- `User`: User account with email verification status
- `ChatMessage`: Single message in a chat (role: SYSTEM/USER/ASSISTANT)
- `ChatSession`: Conversation session with multiple messages
- `Diary`: AI-generated diary entry linked to chat session
- `EmailVerificationCode`: Temporary verification code with expiration

**Key Services:**
- `AuthService`: Registration (auto-generates nickname via `RandomNameGenerator`), login, token management
- `EmailVerificationService`: Send and verify email codes (10-minute expiration)
- `DiaryService`: Manage chat sessions and generate diaries
  - `get_chat_session()`: Get or create active session with system prompt
  - `send_chat_message()`: User sends message, AI responds
  - `write_diary()`: Parse AI response and save diary
  - `end_chat_session()`: Mark session as inactive

**Infrastructure Implementations:**
- `FakerRandomNameGenerator`: Uses Faker library to generate random Korean nicknames (형용사 + 명사 combinations like "행복한루피", "용감한펭귄")
- `AnthropicAIChatBot`: Anthropic Claude integration with proper `MessageParam` typing for type safety
