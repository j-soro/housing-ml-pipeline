.PHONY: setup test lint clean format check install

# Development Setup
setup:
	poetry install
	poetry run pre-commit install

# Run tests
test:
	poetry run pytest

# Run tests with coverage
coverage:
	poetry run pytest --cov=src --cov-report=term-missing

# Lint and type checking
lint:
	poetry run ruff check .
	poetry run mypy .

# Format code
format:
	poetry run ruff format .
	poetry run ruff check --fix .

# Run all checks (useful for pre-commit)
check: format lint test

# Clean python cache files
ifeq ($(OS),Windows_NT)
clean:
	if exist "__pycache__" rmdir /s /q "__pycache__"
	if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
	if exist ".ruff_cache" rmdir /s /q ".ruff_cache"
	if exist ".mypy_cache" rmdir /s /q ".mypy_cache"
	if exist ".coverage" del /f .coverage
else
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
endif

# Install dependencies
install:
	poetry install

# Update dependencies
update:
	poetry update
