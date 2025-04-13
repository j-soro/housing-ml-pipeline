"""PostgreSQL adapter for storing housing data and predictions."""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
    create_engine,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from src.core.domain.entities.housing_record import HousingRecord
from src.core.domain.entities.prediction import Prediction, PredictionStatus
from src.core.domain.exceptions import StorageError
from src.core.port.storage_port import StoragePort

Base = declarative_base()


class CleanedHousingRecord(Base):
    """Cleaned housing record model."""

    __tablename__ = "cleaned_housing_records"

    id = Column(String, primary_key=True)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    housing_median_age = Column(Float, nullable=False)
    total_rooms = Column(Float, nullable=False)
    total_bedrooms = Column(Float, nullable=False)
    population = Column(Float, nullable=False)
    households = Column(Float, nullable=False)
    median_income = Column(Float, nullable=False)
    ocean_proximity = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to prediction
    prediction = relationship("PredictionRecord", back_populates="cleaned_record", uselist=False)


class PredictionRecord(Base):
    """Prediction record model."""

    __tablename__ = "predictions"

    id = Column(String, primary_key=True)
    cleaned_record_id = Column(String, ForeignKey("cleaned_housing_records.id"), nullable=False)
    prediction_value = Column(Float, nullable=False)
    run_id = Column(String, nullable=True)  # Keep run_id for predictions
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to cleaned record
    cleaned_record = relationship("CleanedHousingRecord", back_populates="prediction")


class PostgresAdapter(StoragePort):
    """PostgreSQL adapter for storing housing data and predictions."""

    def __init__(self, connection_url: str):
        """Initialize the PostgreSQL adapter.

        Args:
            connection_url: The PostgreSQL connection URL
        """
        self.engine = create_engine(connection_url)
        self.Session = sessionmaker(bind=self.engine)
        self.setup()  # Call setup() during initialization

    def setup(self) -> None:
        """Ensure tables exist."""
        Base.metadata.create_all(self.engine)

    def _get_session(self):
        """Get a new database session."""
        return self.Session()

    def save_housing_record(self, record: HousingRecord) -> str:
        """Save a housing record to the database.

        Args:
            record: The housing record to save

        Returns:
            The ID of the saved record

        Raises:
            SQLAlchemyError: If there is an error saving the record
        """
        try:
            with self._get_session() as session:
                # Create cleaned record
                cleaned_record = CleanedHousingRecord(
                    id=record.id,
                    longitude=record.longitude,
                    latitude=record.latitude,
                    housing_median_age=record.housing_median_age,
                    total_rooms=record.total_rooms,
                    total_bedrooms=record.total_bedrooms,
                    population=record.population,
                    households=record.households,
                    median_income=record.median_income,
                    ocean_proximity=record.ocean_proximity,
                )
                session.add(cleaned_record)
                session.commit()

                # Return the ID of the saved record
                return str(cleaned_record.id)
        except SQLAlchemyError as e:
            raise StorageError(f"Error saving housing record: {str(e)}") from e

    def get_housing_record(self, record_id: str) -> Optional[HousingRecord]:
        """Get a housing record from the database.

        Args:
            record_id: The ID of the record to get

        Returns:
            The housing record if found, None otherwise

        Raises:
            SQLAlchemyError: If there is an error getting the record
        """
        try:
            with self._get_session() as session:
                cleaned_record = session.query(CleanedHousingRecord).filter_by(id=record_id).first()
                if cleaned_record:
                    # Create a HousingRecord from the cleaned record
                    # First get the values from the SQLAlchemy model
                    record_dict = {
                        "id": cleaned_record.id,
                        "longitude": cleaned_record.longitude,
                        "latitude": cleaned_record.latitude,
                        "housing_median_age": cleaned_record.housing_median_age,
                        "total_rooms": cleaned_record.total_rooms,
                        "total_bedrooms": cleaned_record.total_bedrooms,
                        "population": cleaned_record.population,
                        "households": cleaned_record.households,
                        "median_income": cleaned_record.median_income,
                        "ocean_proximity": cleaned_record.ocean_proximity,
                    }
                    return HousingRecord(**record_dict)
                return None
        except SQLAlchemyError as e:
            raise StorageError(f"Error getting housing record: {str(e)}") from e

    def save_prediction(self, prediction: Prediction) -> str:
        """Save a prediction to the database.

        Args:
            prediction: The prediction to save

        Returns:
            The ID of the saved prediction

        Raises:
            SQLAlchemyError: If there is an error saving the prediction
        """
        try:
            with self._get_session() as session:
                # Use the ID from the prediction object
                prediction_record = PredictionRecord(
                    id=prediction.id,
                    cleaned_record_id=prediction.record_id,
                    prediction_value=prediction.value,
                    run_id=prediction.run_id,  # Save run_id from prediction
                    created_at=prediction.created_at,
                )
                session.add(prediction_record)
                session.commit()

                # Return the ID of the saved prediction
                return prediction.id
        except SQLAlchemyError as e:
            raise StorageError(f"Error saving prediction: {str(e)}") from e

    def get_prediction(self, run_id: str) -> Optional[Prediction]:
        """Get a prediction from the database by Dagster run ID.

        Args:
            run_id: The Dagster run ID to get the prediction for

        Returns:
            The prediction if found, None otherwise

        Raises:
            SQLAlchemyError: If there is an error getting the prediction
        """
        try:
            with self._get_session() as session:
                prediction_record = session.query(PredictionRecord).filter_by(run_id=run_id).first()
                if prediction_record:
                    # Create a HousingRecord from the cleaned record
                    cleaned_record = prediction_record.cleaned_record
                    record_dict = {
                        "id": cleaned_record.id,
                        "longitude": cleaned_record.longitude,
                        "latitude": cleaned_record.latitude,
                        "housing_median_age": cleaned_record.housing_median_age,
                        "total_rooms": cleaned_record.total_rooms,
                        "total_bedrooms": cleaned_record.total_bedrooms,
                        "population": cleaned_record.population,
                        "households": cleaned_record.households,
                        "median_income": cleaned_record.median_income,
                        "ocean_proximity": cleaned_record.ocean_proximity,
                    }
                    housing_record = HousingRecord(**record_dict)

                    # Create the prediction with the proper HousingRecord
                    prediction_dict = {
                        "id": prediction_record.id,
                        "record_id": prediction_record.cleaned_record_id,
                        "value": prediction_record.prediction_value,
                        "created_at": prediction_record.created_at,
                        "run_id": prediction_record.run_id,
                        "record": housing_record,
                        "status": PredictionStatus.COMPLETED,
                    }
                    return Prediction(**prediction_dict)
                return None
        except SQLAlchemyError as e:
            raise StorageError(f"Error getting prediction by run_id: {str(e)}") from e
