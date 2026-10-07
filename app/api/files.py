import json
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.file_model import FileRecord
from app.models.feature_model import FeatureRecord
from app.services.file_service import (
    save_uploaded_file,
    save_file_and_features
)

from app.services.geospatial_service import read_geospatial_file


router = APIRouter(
    prefix="/api/files",
    tags=["Files"]
)


@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    try:

        # 1. Save uploaded file
        file_id, extension, file_path = save_uploaded_file(file)

        # 2. Read geospatial file
        gdf = read_geospatial_file(
            file_path,
            file_id,
            extension
        )

        # 3. Save file and features
        file_record = save_file_and_features(
            db=db,
            file_id=file_id,
            filename=file.filename,
            file_type=extension,
            gdf=gdf
        )

        return {
            "id": file_record.id,
            "filename": file_record.filename,
            "file_type": file_record.file_type,
            "feature_count": file_record.feature_count,
            "crs": file_record.crs,
            "status": file_record.status
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        db.rollback()

        print(f"Processing error: {error}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the geospatial file."
        )


@router.get("/{file_id}/measurements")
def get_measurements(
    file_id: str,
    db: Session = Depends(get_db)
):

    file_record = (
        db.query(FileRecord)
        .filter(FileRecord.id == file_id)
        .first()
    )

    if not file_record:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    features = (
        db.query(FeatureRecord)
        .filter(FeatureRecord.file_id == file_id)
        .order_by(FeatureRecord.feature_index)
        .all()
    )

    results = []

    for feature in features:

        properties = {}

        if feature.properties:
            properties = json.loads(feature.properties)

        results.append({
            "feature_id": feature.feature_index,
            "geometry_type": feature.geometry_type,
            "geometry": feature.geometry,
            "crs": file_record.crs,
            "properties": properties,
            "measurement_type": feature.measurement_type,
            "measurement_value": feature.measurement_value,
            "measurement_unit": feature.measurement_unit
        })

    return {
        "file_id": file_id,
        "filename": file_record.filename,
        "crs": file_record.crs,
        "features": results
    }