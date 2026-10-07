import json

from sqlalchemy.orm import Session

from app.models.file_model import FileRecord
from app.models.feature_model import FeatureRecord
from app.services.measurement_service import calculate_measurements
from pathlib import Path
import shutil
import uuid

from fastapi import UploadFile


UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_EXTENSIONS = {".kml", ".zip"}


def validate_file(file: UploadFile):
    if not file.filename:
        raise ValueError("Filename is missing")

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. Only .kml and .zip files are allowed."
        )

    return extension


def save_uploaded_file(file: UploadFile) -> tuple[str, str, Path]:
    extension = validate_file(file)

    file_id = str(uuid.uuid4())

    safe_filename = Path(file.filename).name

    file_path = UPLOAD_DIR / f"{file_id}_{safe_filename}"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_id, extension, file_path

def save_file_and_features(
    db: Session,
    file_id: str,
    filename: str,
    file_type: str,
    gdf
):
    measurements = calculate_measurements(gdf)

    measurement_map = {
        item["feature_index"]: item
        for item in measurements
    }

    file_record = FileRecord(
        id=file_id,
        filename=filename,
        file_type=file_type,
        feature_count=len(gdf),
        crs=str(gdf.crs) if gdf.crs else None,
        status="PROCESSED"
    )

    db.add(file_record)

    features = []

    for index, row in gdf.iterrows():

        geometry = row.geometry

        properties = {}

        for column in gdf.columns:
            if column != "geometry":
                value = row[column]

                if value is not None:
                    properties[column] = str(value)

        measurement = measurement_map.get(int(index))

        feature = FeatureRecord(
            file_id=file_id,
            feature_index=int(index),
            geometry_type=geometry.geom_type,
            geometry=geometry.wkt if geometry else None,
            properties=json.dumps(properties),

            measurement_type=(
                measurement["measurement_type"]
                if measurement
                else None
            ),

            measurement_value=(
                measurement["measurement_value"]
                if measurement
                else None
            ),

            measurement_unit=(
                measurement["measurement_unit"]
                if measurement
                else None
            )
        )

        features.append(feature)

    db.add_all(features)

    db.commit()

    return file_record