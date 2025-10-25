# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI application with PostgreSQL database, featuring a REST API for managing items and users. The project uses SQLAlchemy for ORM, Pydantic for data validation, and supports both local and Docker deployment.

## Development Commands

### Local Development

```bash
# Start the development server
uvicorn main:app --reload

# Start on a different port
uvicorn main:app --reload --port 8001

# Run tests
pytest

# Run specific test
pytest test_main.py::test_create_item

# Run tests with coverage
pytest --cov=main --cov-report=html

# Run tests matching a pattern
pytest -k "test_create"
```

### Docker Development

```bash
# Start all services (FastAPI, PostgreSQL, pgAdmin)
docker-compose up -d

# Rebuild and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f web

# Stop all services
docker-compose down

# Stop and remove volumes (deletes database)
docker-compose down -v

# Execute command in container
docker-compose exec web pytest

# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d fastapi_db
```

### Database Migrations (Alembic)

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create migration from model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View current migration version
alembic current

# View migration history
alembic history
```

## Architecture

### Core Application Structure

The application follows a layered architecture:

1. **main.py** - FastAPI application entry point with CORS middleware and route definitions
2. **database.py** - SQLAlchemy engine, session management, and `get_db()` dependency
3. **models.py** - SQLAlchemy ORM models (database schema)
4. **schemas.py** - Pydantic models for request/response validation
5. **config.py** - Environment configuration using pydantic-settings

### Database Layer

- **Connection Management**: SQLAlchemy session created per request via `get_db()` dependency
- **Models**: Base class from `database.py` provides declarative base for all models
- **Auto-create Tables**: `models.Base.metadata.create_all(bind=engine)` in main.py creates tables on startup (development only)

### Environment Configuration

The application uses `.env` file for configuration:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Application secret key
- `DEBUG`: Debug mode flag

Configuration is loaded via `config.py` using pydantic-settings, which automatically reads from `.env`.

### Testing Architecture

Tests use in-memory SQLite database with dependency override:
- `test_main.py` overrides `get_db()` to use TestingSessionLocal
- FastAPI TestClient provides synchronous test interface
- Fixtures available for reusable test data

### API Pattern

All endpoints follow consistent patterns:
- POST endpoints return 201 status with created resource
- GET endpoints support pagination via `skip` and `limit` query params
- PUT endpoints fully replace resources
- DELETE endpoints return 204 No Content
- 404 responses use HTTPException with descriptive messages

## Key Implementation Details

### Database Session Management

Always use `db: Session = Depends(get_db)` to get database sessions. The dependency ensures proper cleanup via try/finally block in database.py:16-21.

### Model Changes

When modifying models:
1. Update SQLAlchemy model in `models.py`
2. Update corresponding Pydantic schema in `schemas.py`
3. Create Alembic migration: `alembic revision --autogenerate -m "description"`
4. Apply migration: `alembic upgrade head`

### Adding New Endpoints

Follow the pattern in main.py:
1. Define Pydantic schemas for request/response
2. Use appropriate response_model and status_code
3. Include `db: Session = Depends(get_db)` for database access
4. Handle 404 cases with HTTPException
5. Use async def for endpoints

### Docker Database Connection

When running in Docker, the DATABASE_URL uses service name `db` as hostname (docker-compose.yml:32). For local development, use `localhost`.

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /items` - Create item (returns 201)
- `GET /items` - List items (supports skip/limit pagination)
- `GET /items/{item_id}` - Get single item
- `PUT /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item (returns 204)

## Available Documentation

- **QUICK_START.md** - 5-minute setup guide for both local and Docker
- **DOCKER_GUIDE.md** - Comprehensive Docker usage and troubleshooting
- **ALEMBIC_GUIDE.md** - Complete database migration setup and workflow
- **auth_example.py** - Example authentication implementation
- **websocket_example.py** - Example WebSocket implementation

## Common Patterns

### Error Handling
```python
item = db.query(models.Item).filter(models.Item.id == item_id).first()
if not item:
    raise HTTPException(status_code=404, detail="Item not found")
```

### Model Updates
```python
for key, value in item_update.model_dump().items():
    setattr(db_item, key, value)
db.commit()
db.refresh(db_item)
```

### Pagination
```python
items = db.query(models.Item).offset(skip).limit(limit).all()
```
