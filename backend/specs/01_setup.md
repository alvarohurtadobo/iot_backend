Create a basic FastAPI project for an IoT data centralization platform called iotMonitor. It must have PostgreSQL database configuration and a health endpoint. First make it work locally, then dockerize it.

## STEP 1: Create basic project structure

Create the folder structure:
```
iot_monitor/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   └── db/
│       ├── __init__.py
│       └── base.py
├── pyproject.toml
└── README.md
```

## STEP 2: Configure dependencies

Create pyproject.toml with these minimum dependencies:
- fastapi (>=0.104.0)
- uvicorn[standard] (>=0.24.0)
- sqlalchemy (>=2.0.0)
- psycopg2-binary (>=2.9.0)
- pydantic-settings (>=2.0.0)
- python-dotenv (>=1.0.0)

## STEP 3: Create application configuration

In app/core/config.py:
- Create Settings class using pydantic-settings
- Include PROJECT_NAME, VERSION
- Include DATABASE_URL for PostgreSQL
- Configure to read environment variables


## STEP 4: Create basic FastAPI application

In app/main.py:
- Create FastAPI instance with title and version from config
- GET "/" endpoint that returns welcome message
- GET "/health" endpoint that returns status, service name and version
- DO NOT create other endpoints yet

## STEP 5: Verify local operation

Install dependencies and run:
```bash
uv sync
uv run uvicorn app.main:app --reload
```

Verify that they respond:
- http://localhost:8000/ (welcome message)
- http://localhost:8000/health (status ok)
- http://localhost:8000/docs (automatic documentation)

## STEP 6: Create Dockerfile

- Use Python 3.11-slim image
- Install uv for dependency management
- Copy and install dependencies from pyproject.toml
- Copy application code
- Expose port 8000
- Command to run uvicorn with hot reload

## STEP 7: Create docker-compose.yml

Configure two services:

**db service:**
- PostgreSQL 15
- Environment variables: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
- Port 5432
- Volume for data persistence

**api service:**
- Build from local Dockerfile
- Port 8000
- Volume for development (hot reload)
- Environment variables for DB connection
- Depends on db service

## STEP 8: Verify Docker operation

Run:
```bash
docker-compose up --build
```

Verify that they respond the same as locally:
- http://localhost:8000/
- http://localhost:8000/health
- http://localhost:8000/docs

## STEP 9: Configure database connection

In app/db/base.py:
- Configure SQLAlchemy engine
- Create SessionLocal for DB sessions
- Create declarative Base for future models
- get_db() function for dependency injection
