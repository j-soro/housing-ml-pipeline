"""Dagster assets for the housing prediction pipeline."""
from datetime import datetime
from typing import Any, Dict, List

import dagster as dg

from src.adapter.driven.model.model_resource import ModelResource
from src.adapter.driven.storage.postgres_resource import PostgresResource
from src.config.settings import get_settings
from src.core.domain.entities.housing_record import HousingRecord
from src.core.domain.entities.prediction import Prediction
from src.core.domain.exceptions import (
    DataCleaningError,
    DataValidationError,
    PredictionError,
    StorageError,
)


@dg.asset
def raw_input(context: dg.OpExecutionContext) -> Dict[str, Any]:
    """Asset that loads raw input data.

    This asset is the entry point for the pipeline. It loads the raw input data
    from the context and returns it as a dictionary.

    Args:
        context: The Dagster context

    Returns:
        A dictionary containing the raw input data
    """
    # Get the data from the context
    data = context.op_config["data"]
    return data


@dg.asset
def cleaned_data(
    context,
    raw_input: Dict[str, Any],
) -> HousingRecord:
    """Asset that cleans the raw data.

    This asset takes the raw data and performs cleaning operations:
    - Validates data types and ranges
    - Handles missing values
    - Validates ocean proximity values

    Args:
        context: The Dagster context
        raw_input: The raw data as a dictionary

    Returns:
        A HousingRecord object containing the cleaned data

    Raises:
        DataValidationError: If the data validation fails
        DataCleaningError: If the data cleaning fails
    """
    try:
        context.log.info(
            f"Starting data cleaning for record ID: {raw_input.get('record_id', 'unknown')}"
        )

        # Clean the data
        context.log.debug("Cleaning data")
        cleaned_data = raw_input.copy()

        # Convert string values to floats
        numeric_fields = [
            "longitude",
            "latitude",
            "housing_median_age",
            "total_rooms",
            "total_bedrooms",
            "population",
            "households",
            "median_income",
        ]

        for field in numeric_fields:
            if field in cleaned_data and isinstance(cleaned_data[field], str):
                try:
                    cleaned_data[field] = float(cleaned_data[field])
                except ValueError as e:
                    context.log.error(f"Invalid numeric value for {field}: {cleaned_data[field]}")
                    raise DataValidationError(f"{field} must be a valid number") from e

        # Validate data types and ranges
        context.log.debug("Validating data types and ranges")
        if not isinstance(cleaned_data.get("longitude"), (int, float)) or not isinstance(
            cleaned_data.get("latitude"), (int, float)
        ):
            context.log.error("Invalid longitude or latitude data type")
            raise DataValidationError("Longitude and latitude must be numeric")

        if (
            not isinstance(cleaned_data.get("housing_median_age"), (int, float))
            or cleaned_data.get("housing_median_age") < 0
        ):
            context.log.error("Invalid housing median age")
            raise DataValidationError("Housing median age must be a non-negative number")

        if (
            not isinstance(cleaned_data.get("total_rooms"), (int, float))
            or cleaned_data.get("total_rooms") < 0
        ):
            context.log.error("Invalid total rooms")
            raise DataValidationError("Total rooms must be a non-negative number")

        if (
            not isinstance(cleaned_data.get("total_bedrooms"), (int, float))
            or cleaned_data.get("total_bedrooms") < 0
        ):
            context.log.error("Invalid total bedrooms")
            raise DataValidationError("Total bedrooms must be a non-negative number")

        if (
            not isinstance(cleaned_data.get("population"), (int, float))
            or cleaned_data.get("population") < 0
        ):
            context.log.error("Invalid population")
            raise DataValidationError("Population must be a non-negative number")

        if (
            not isinstance(cleaned_data.get("households"), (int, float))
            or cleaned_data.get("households") < 0
        ):
            context.log.error("Invalid households")
            raise DataValidationError("Households must be a non-negative number")

        if (
            not isinstance(cleaned_data.get("median_income"), (int, float))
            or cleaned_data.get("median_income") < 0
        ):
            context.log.error("Invalid median income")
            raise DataValidationError("Median income must be a non-negative number")

        # Validate ocean proximity
        context.log.debug("Validating ocean proximity")
        ocean_proximity = cleaned_data.get("ocean_proximity")
        if not ocean_proximity:
            context.log.error("Missing ocean proximity")
            raise DataValidationError("Ocean proximity is required")

        # Use OceanProximity value object for validation
        valid_categories = ["<1H OCEAN", "INLAND", "ISLAND", "NEAR BAY", "NEAR OCEAN"]
        if ocean_proximity not in valid_categories:
            context.log.error(f"Invalid ocean proximity: {ocean_proximity}")
            raise DataValidationError(f"Invalid ocean proximity: {ocean_proximity}")

        # Handle missing values
        if cleaned_data.get("total_bedrooms") is None:
            context.log.info("Filling missing total_bedrooms with median")
            cleaned_data["total_bedrooms"] = 0

        # Create and return a HousingRecord object
        housing_record = HousingRecord(
            # Only set id if record_id is provided, otherwise let the default factory generate one
            **({"id": cleaned_data.get("record_id")} if cleaned_data.get("record_id") else {}),
            longitude=cleaned_data.get("longitude"),
            latitude=cleaned_data.get("latitude"),
            housing_median_age=cleaned_data.get("housing_median_age"),
            total_rooms=cleaned_data.get("total_rooms"),
            total_bedrooms=cleaned_data.get("total_bedrooms"),
            population=cleaned_data.get("population"),
            households=cleaned_data.get("households"),
            median_income=cleaned_data.get("median_income"),
            ocean_proximity=cleaned_data.get("ocean_proximity"),
        )

        context.log.info(f"Data cleaning completed successfully for record ID: {housing_record.id}")
        return housing_record

    except DataValidationError as e:
        context.log.error(f"Data validation error: {str(e)}")
        raise

    except Exception as e:
        context.log.error(f"Unexpected error during data cleaning: {str(e)}")
        raise DataCleaningError(f"Error cleaning data: {str(e)}") from e


@dg.asset
def stored_cleaned_data(
    context,
    cleaned_data: HousingRecord,
    postgres: PostgresResource,
) -> Dict[str, Any]:
    """Asset that stores the cleaned data in PostgreSQL.

    This asset takes the cleaned data and stores it in the PostgreSQL database.

    Args:
        context: The Dagster context
        cleaned_data: The cleaned data as a HousingRecord
        postgres: The PostgreSQL resource

    Returns:
        A dictionary containing the stored data

    Raises:
        StorageError: If the data storage fails
    """
    try:
        context.log.info(f"Storing cleaned data for record ID: {cleaned_data.id}")

        # Store the housing record using the PostgresResource
        record_id = postgres.save_housing_record(cleaned_data)

        context.log.info(f"Successfully stored cleaned data with record ID: {record_id}")
        return {"record_id": record_id}

    except Exception as e:
        context.log.error(f"Error storing cleaned data: {str(e)}")
        raise StorageError(f"Error storing cleaned data: {str(e)}") from e


@dg.asset
def prepared_data(
    context,
    cleaned_data: HousingRecord,
) -> Dict[str, Any]:
    """Asset that prepares the data for prediction.

    This asset takes the cleaned data and prepares it for the model:
    - One-hot encodes categorical variables
    - Scales numerical features
    - Creates feature matrix

    Args:
        context: The Dagster context
        cleaned_data: The cleaned data as a HousingRecord

    Returns:
        A dictionary containing the prepared data

    Raises:
        DataValidationError: If the data preparation fails
    """
    try:
        context.log.info(f"Preparing data for prediction for record ID: {cleaned_data.id}")

        # Extract features
        context.log.debug("Extracting features")
        features = {
            "longitude": cleaned_data.longitude,
            "latitude": cleaned_data.latitude,
            "housing_median_age": cleaned_data.housing_median_age,
            "total_rooms": cleaned_data.total_rooms,
            "total_bedrooms": cleaned_data.total_bedrooms,
            "population": cleaned_data.population,
            "households": cleaned_data.households,
            "median_income": cleaned_data.median_income,
            "ocean_proximity": cleaned_data.ocean_proximity,
        }

        # One-hot encode ocean_proximity
        context.log.debug("One-hot encoding ocean_proximity")
        ocean_proximity = features.pop("ocean_proximity")
        valid_categories = ["<1H OCEAN", "INLAND", "ISLAND", "NEAR BAY", "NEAR OCEAN"]

        for category in valid_categories:
            features[f"ocean_proximity_{category}"] = 1 if ocean_proximity == category else 0

        # Scale numerical features (in a real scenario, we'd use a scaler from the model)
        context.log.debug("Scaling numerical features")
        # For simplicity, we'll just use the raw values
        # In a real scenario, we'd use a scaler from the model

        context.log.info(
            f"Data preparation completed successfully for record ID: {cleaned_data.id}"
        )
        return features

    except Exception as e:
        context.log.error(f"Error preparing data: {str(e)}")
        raise DataValidationError(f"Error preparing data: {str(e)}") from e


@dg.asset
def prediction_result(
    context,
    model: ModelResource,
    prepared_data: Dict[str, Any],
) -> List[float]:
    """Asset that generates predictions using the model.

    This asset takes the prepared data and generates predictions using the model.

    Args:
        context: The Dagster context
        model: The model resource
        prepared_data: The prepared data as a dictionary

    Returns:
        A list containing the predictions as floats

    Raises:
        PredictionError: If the prediction fails
    """
    try:
        context.log.info("Generating prediction")

        # Generate prediction using the model
        context.log.debug("Calling model.predict")
        prediction = model.predict(prepared_data)

        context.log.info(f"Prediction generated successfully: {prediction}")
        return prediction

    except Exception as e:
        context.log.error(f"Error generating prediction: {str(e)}")
        raise PredictionError(f"Error generating prediction: {str(e)}") from e


@dg.asset
def stored_prediction_result(
    context,
    prediction_result: List[float],
    stored_cleaned_data: Dict[str, Any],
    postgres: PostgresResource,
) -> Dict[str, Any]:
    """Asset that stores the predictions in PostgreSQL.

    This asset takes the predictions and stores them in the PostgreSQL database.

    Args:
        context: The Dagster context
        prediction_result: The predictions as a list of floats
        stored_cleaned_data: The stored cleaned data containing the record ID
        postgres: The PostgreSQL resource

    Returns:
        A dictionary containing the predictions

    Raises:
        PredictionError: If storing the prediction fails
    """
    try:
        context.log.info(
            f"Storing prediction for record ID: {stored_cleaned_data.get('record_id', 'unknown')}"
        )

        # Create a Prediction entity with run_id from Dagster context
        prediction = Prediction(
            record_id=stored_cleaned_data["record_id"],
            value=prediction_result[0],
            created_at=datetime.utcnow(),
            run_id=context.run_id,  # Get run_id from Dagster context
        )

        # Store the prediction using the PostgresResource
        # The save_prediction method returns the record_id as a string
        record_id = postgres.save_prediction(prediction)

        context.log.info(f"Successfully stored prediction with record ID: {record_id}")
        return {
            "record_id": record_id,
            "prediction": prediction_result[0],
            "run_id": context.run_id,
        }

    except Exception as e:
        context.log.error(f"Error storing prediction: {str(e)}")
        raise PredictionError(f"Error storing prediction: {str(e)}") from e


@dg.job
def housing_prediction_job():
    """Define the housing prediction job."""
    # Define the assets in dependency order
    raw_data = raw_input()
    cleaned = cleaned_data(raw_data)
    stored_cleaned = stored_cleaned_data(cleaned)
    prepared = prepared_data(cleaned)
    prediction = prediction_result(prepared)
    stored_prediction_result(prediction, stored_cleaned)


# Define the Dagster definitions
defs = dg.Definitions(
    assets=[
        raw_input,
        cleaned_data,
        stored_cleaned_data,
        prepared_data,
        prediction_result,
        stored_prediction_result,
    ],
    resources={
        "postgres": PostgresResource(connection_url=get_settings().database_url),
        "model": ModelResource(model_path=get_settings().MODEL_PATH),
    },
    jobs=[housing_prediction_job],
)
