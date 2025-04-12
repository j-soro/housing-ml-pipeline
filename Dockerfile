FROM python:3.9.13-slim

# Set environment variables
ENV PYTHONPATH=/app
ENV DAGSTER_HOME=/opt/dagster/dagster_home

# Create directories
RUN mkdir -p /app/models /app/src /opt/dagster/dagster_home

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies (only main dependencies, no dev dependencies)
RUN poetry install --only main --no-interaction --no-ansi

# Copy application code and Dagster config
COPY src /app/src/
COPY dagster.yaml workspace.yaml /opt/dagster/dagster_home/

# Debug: List contents and show container.py
RUN ls -la /app/src/config/ && head -n 3 /app/src/config/container.py

# Set working directory
WORKDIR /app

# Model will be mounted at runtime
VOLUME /app/models

# Environment variable for model path
ENV MODEL_PATH=/app/models/model.joblib

# Expose the port the app runs on
EXPOSE 8000
