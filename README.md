# Housing ML Pipeline

## Overview
Housing price prediction ETL service using FastAPI, Dagster, and a ML model.

## Development Environment:

- Python 3.11
- Poetry for dependency management
- Ruff for linting and formatting
- MyPy for type checking
- Pre-commit hooks

## Setup:

1. Install Poetry
2. Run make setup to install dependencies
3. Run make check to verify installation

## Project Structure:

- `src/`: Source code following hexagonal architecture
- `tests/:` Test files
- `Makefile`: Development commands
- `pyproject.toml`: Project configuration

## Commands:

- `make setup`: Install dependencies
- `make test`: Run tests
- `make lint`: Run linting
- `make format`: Format code
- `make check`: Run all checks
- `make clean`: Clean cache files

## License
MIT License
