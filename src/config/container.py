"""Dependency injection container configuration."""
from dependency_injector import containers, providers

from src.adapter.driven.etl.dagster_adapter import DagsterETLAdapter
from src.adapter.driven.model.sklearn_adapter import SklearnModelAdapter
from src.adapter.driven.storage.postgres_adapter import PostgresAdapter
from src.adapter.driven.storage.postgres_resource import PostgresResource
from src.adapter.driving.fastapi.handler import FastAPIHandler
from src.core.service.prediction_service import PredictionService

from .settings import get_settings


class Container(containers.DeclarativeContainer):
    """Application container."""

    # Configuration
    config = providers.Singleton(get_settings)

    # Storage
    postgres_resource = providers.Singleton(
        PostgresResource, connection_url=config.provided.database_url
    )

    # Storage Adapter (implements StoragePort)
    storage_adapter = providers.Singleton(
        PostgresAdapter,
        connection_url=config.provided.database_url,
    )

    # Model
    model = providers.Singleton(
        SklearnModelAdapter,
        model_path=config.provided.MODEL_PATH,
    )

    # ETL
    etl_adapter = providers.Singleton(
        DagsterETLAdapter,
    )

    # Services
    prediction_service = providers.Singleton(
        PredictionService,
        etl=etl_adapter,
        storage=storage_adapter,
    )

    # Input Port Implementation
    input_port = providers.Singleton(
        FastAPIHandler,
        prediction_service=prediction_service,
    )

    # Wire modules for dependency injection
    wiring_config = containers.WiringConfiguration(
        modules=["src.adapter.driving.fastapi.app", "src.adapter.driven.etl.assets"]
    )


# Create and configure the container
container = Container()
