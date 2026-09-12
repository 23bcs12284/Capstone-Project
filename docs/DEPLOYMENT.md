# Deployment Documentation

## Overview

This document covers the deployment architecture for the Explainable AI Loan Approval Prediction System, including Docker containerization, docker-compose orchestration with 3 services, and local development setup.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Docker Network                  │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Streamlit│  │ FastAPI  │  │  PostgreSQL   │  │
│  │ Dashboard│──│ Backend  │──│  Database     │  │
│  │ :8501    │  │ :8000    │  │  :5432        │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## Docker Configuration

### Dockerfile (Backend API)

```dockerfile
# deployment/Dockerfile.api
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY models_saved/ ./models_saved/
COPY artifacts/ ./artifacts/
COPY config/ ./config/
COPY preprocessing/ ./preprocessing/
COPY explainability/ ./explainability/
COPY fairness/ ./fairness/

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the API server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### Dockerfile (Dashboard)

```dockerfile
# deployment/Dockerfile.dashboard
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard/ ./dashboard/
COPY config/ ./config/
COPY artifacts/ ./artifacts/
COPY models_saved/ ./models_saved/

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "dashboard/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

---

## Docker Compose (3 Services)

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Service 1: FastAPI Backend
  api:
    build:
      context: .
      dockerfile: deployment/Dockerfile.api
    container_name: loan-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://loan_user:loan_pass@db:5432/loan_db
      - MODEL_PATH=/app/models_saved/logistic_regression.pkl
      - PREPROCESSOR_PATH=/app/artifacts/preprocessor.pkl
      - LOG_LEVEL=info
    volumes:
      - ./logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - loan-network

  # Service 2: Streamlit Dashboard
  dashboard:
    build:
      context: .
      dockerfile: deployment/Dockerfile.dashboard
    container_name: loan-dashboard
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://api:8000
      - DASHBOARD_MODE=connected
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - loan-network

  # Service 3: PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: loan-db
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=loan_db
      - POSTGRES_USER=loan_user
      - POSTGRES_PASSWORD=loan_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U loan_user -d loan_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - loan-network

volumes:
  postgres_data:
    driver: local

networks:
  loan-network:
    driver: bridge
```

---

## Deployment Commands

### Docker Compose Operations

```bash
# Build all services
docker-compose build

# Start all services (detached)
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api

# Stop all services
docker-compose down

# Stop and remove volumes (clean reset)
docker-compose down -v

# Rebuild a specific service
docker-compose build api
docker-compose up -d api
```

### Individual Docker Commands

```bash
# Build API image
docker build -f deployment/Dockerfile.api -t loan-api:latest .

# Run API container standalone
docker run -p 8000:8000 --name loan-api loan-api:latest

# Build dashboard image
docker build -f deployment/Dockerfile.dashboard -t loan-dashboard:latest .

# Run dashboard container standalone
docker run -p 8501:8501 --name loan-dashboard loan-dashboard:latest
```

---

## Local Development Commands

### Prerequisites

```bash
# Python 3.10+
python --version

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Running Services Locally

```bash
# Start the FastAPI backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Start the Streamlit dashboard (connected mode)
streamlit run dashboard/app.py -- --mode connected

# Start the Streamlit dashboard (standalone mode)
streamlit run dashboard/app.py -- --mode standalone

# Run database migrations
python database/migrate.py

# Train models
python training/train_all_models.py

# Run tests
pytest tests/ -v --cov=./ --cov-report=html
```

### Environment Variables

```bash
# .env file
DATABASE_URL=postgresql://loan_user:loan_pass@localhost:5432/loan_db
MODEL_PATH=models_saved/logistic_regression.pkl
PREPROCESSOR_PATH=artifacts/preprocessor.pkl
API_BASE_URL=http://localhost:8000
LOG_LEVEL=debug
SECRET_KEY=your-secret-key-here
```

---

## Health Checks

| Service    | Endpoint                        | Expected Response |
|------------|--------------------------------|-------------------|
| API        | `GET /health`                  | `{"status": "ok"}`|
| Dashboard  | `GET /_stcore/health`          | HTTP 200          |
| Database   | `pg_isready -U loan_user`     | Exit code 0       |

---

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Specification](https://docs.docker.com/compose/compose-file/)
- [Uvicorn Deployment](https://www.uvicorn.org/deployment/)
- [Streamlit Deployment](https://docs.streamlit.io/deploy)
