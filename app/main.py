from fastapi import FastAPI

from app.models.database import Base, engine
from app.models import FileRecord, FeatureRecord
from app.api.files import router as files_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Geospatial File Measurement API",
    description="API for processing Shapefile and KML files and calculating measurements.",
    version="1.0.0"
)


app.include_router(files_router)


@app.get("/")
def root():
    return {
        "message": "Geospatial File Measurement API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }