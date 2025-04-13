# Housing ML Pipeline

A machine learning pipeline for housing price predictions using hexagonal architecture, FastAPI, Dagster, and PostgreSQL. This project demonstrates clean architecture principles and modern development practices for building maintainable, testable, and scalable ML systems.

## Overview

This project implements a machine learning pipeline for predicting housing prices based on property characteristics. It follows hexagonal architecture principles to create a maintainable, testable, and scalable system.

### Key Features
- **Asynchronous Processing**: Submit prediction requests and retrieve results asynchronously
- **Clean Architecture**: Clear separation of concerns with ports and adapters
- **ETL Pipeline**: Automated data cleaning, transformation, and prediction workflow
- **RESTful API**: Simple HTTP interface for submitting and retrieving predictions
- **Dockerized**: Easy deployment with containerized services

### How It Works
1. **Submit Data**: Send housing property data to `POST /predictions` endpoint
2. **Process Asynchronously**: The system triggers a Dagster ETL pipeline and returns a run ID
3. **Pipeline Execution**: The pipeline performs:
   - Data cleaning and transformation
   - Clean data persistence to PostgreSQL
   - ML model prediction on the data
   - Result storage in PostgreSQL
4. **Check Status**: Use `GET /predictions/{run-id}` to check the current status of any pipeline run

This architecture demonstrates clean code principles, dependency injection, and separation of concerns while providing a practical solution for ML prediction workflows.

## Architecture

The project follows hexagonal (ports and adapters) architecture:

### Core Domain
- **Entities**: `HousingRecord`, `Prediction`, `PredictionStatus`
- **Value Objects**: `OceanProximity`
- **Domain Services**: `PredictionService`
- **Ports**: `InputPort`, `ETLPort`, `StoragePort`, `ModelPort`

### Adapters
- **Driving Adapters**:
  - FastAPI REST API
  - FastAPI Handler
  - API Models (Request/Response DTOs)
- **Driven Adapters**:
  - PostgreSQL Adapter
  - Sklearn Model Adapter
  - Dagster ETL Adapter

### External Systems
- PostgreSQL Database
- Dagster Pipeline
- ML Model (scikit-learn)

### Architecture Diagrams
- [Component Diagram](plantuml.svg) - Shows the hexagonal architecture components and their relationships
- [Sequence Diagram](sequence.svg) - Illustrates the prediction request and result flows

## Prerequisites

- Docker
- Docker Compose
- Python 3.9+ (for local development)
- Poetry (for local development)

## Setup

### 1. Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd housing-ml-pipeline

# Create and activate a Python 3.9 virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Poetry
pip install poetry

# Install dependencies
poetry install
```

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Create models directory
mkdir -p models
```

### 3. Model Setup
```bash
# Copy your trained model
cp /path/to/your/model.joblib models/model.joblib
```

### 4. Start Services
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f
```

## API Documentation

The API documentation is available in several formats:

- [OpenAPI Specification](openapi.json) - Complete API specification in JSON format
- [Swagger UI](http://localhost:8000/docs) - Interactive API documentation (when running)
- [ReDoc](http://localhost:8000/redoc) - Alternative API documentation (when running)

## API Endpoints

### Submit Prediction Request
```bash
POST /predictions
Content-Type: application/json

{
    "longitude": -122.23,
    "latitude": 37.88,
    "housing_median_age": 41.0,
    "total_rooms": 880.0,
    "total_bedrooms": 129.0,
    "population": 322.0,
    "households": 126.0,
    "median_income": 8.3252,
    "ocean_proximity": "NEAR BAY"
}
```

### Get Prediction Result
```bash
GET /predictions/{run_id}
```

## Project Structure

```
.
├── src/
│   ├── adapter/           # Adapters for external services
│   │   ├── driving/       # Driving adapters (FastAPI)
│   │   └── driven/        # Driven adapters (PostgreSQL, ML, Dagster)
│   ├── core/              # Core domain logic
│   │   ├── domain/        # Domain entities and value objects
│   │   ├── port/          # Port interfaces
│   │   └── service/       # Domain services
│   └── config/            # Configuration and DI container
├── models/                # Model artifacts directory
├── tests/                # Test suite
├── docker-compose.yml    # Docker services configuration
├── docker-compose.dev.yml # Development environment configuration
├── Dockerfile           # Application container definition
├── pyproject.toml       # Python dependencies
└──
```

## Development

### Commands
```bash
# Install dependencies and set up pre-commit hooks
make setup

# Run tests
make test

# Run tests with coverage
make coverage

# Lint and type checking
make lint

# Format code
make format

# Run all checks (format, lint, test)
make check

# Clean cache files
make clean

# Update dependencies
make update
```

### Development Tools
- Poetry for dependency management
- Ruff for linting
- MyPy for type checking
- Pre-commit hooks for code quality

## Troubleshooting

### Common Issues

#### 1. PostgreSQL Connection
- **Issue**: App can't connect to PostgreSQL
- **Solution**: Check PostgreSQL container health
```bash
docker-compose ps
docker-compose logs postgres
```

#### 2. Model Loading
- **Issue**: Model file not found
- **Solution**: Verify model path and permissions
```bash
docker-compose exec app ls -l /app/models
```

#### 3. Dagster Issues
- **Issue**: Dagster UI not accessible
- **Solution**: Check Dagster logs
```bash
docker-compose logs dagster-webserver
```

#### 4. Port Conflicts
- **Issue**: Services fail to start
- **Solution**: Check port usage
```bash
# Windows
netstat -ano | findstr "5432 8000 3000"
# Linux/Mac
lsof -i :5432,8000,3000
```

## Verification

### 1. Check Services
```bash
docker-compose ps
```

### 2. Verify API
```bash
curl http://localhost:8000/docs
```

### 3. Verify Dagster UI
- Open http://localhost:3000 in browser

## License
MIT License
