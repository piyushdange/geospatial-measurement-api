# Geospatial File Measurement API

A FastAPI-based backend service that accepts geospatial files such as **KML** and **Shapefile ZIP archives**, extracts their features, handles coordinate reference systems (CRS), and calculates geometry measurements.

## Features

* Upload `.kml` files
* Upload Shapefile as `.zip`
* Validate uploaded file types
* Validate required Shapefile components
* Extract geospatial features
* Store file and feature information in SQLite
* Return:

  * Feature ID
  * Geometry type
  * Geometry
  * CRS
  * Properties
* Calculate:

  * Polygon / MultiPolygon → Area
  * LineString / MultiLineString → Length
  * Point → No measurement
* Automatically transform geographic coordinates to a suitable projected CRS before measurement
* REST APIs using FastAPI
* Interactive Swagger API documentation
* Automated tests using pytest

---

## Tech Stack

| Technology | Purpose                    |
| ---------- | -------------------------- |
| Python     | Programming language       |
| FastAPI    | REST API framework         |
| GeoPandas  | Geospatial file processing |
| Shapely    | Geometry operations        |
| PyProj     | CRS transformation         |
| Pyogrio    | Geospatial file I/O        |
| SQLAlchemy | Database ORM               |
| SQLite     | Database                   |
| Pytest     | Automated testing          |
| HTTPX      | API testing                |

---

## Project Structure

```text
geospatial-measurement-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── files.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── file_model.py
│   │   └── feature_model.py
│   │
│   ├── schemas/
│   │   └── __init__.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── file_service.py
│       ├── geospatial_service.py
│       └── measurement_service.py
│
├── data/
│   ├── uploads/
│   ├── extracted/
│   └── test.kml
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_measurements.py
│
├── .gitignore
├── geospatial.db
├── requirements.txt
└── README.md
```

---

# Requirements

* Python 3.11 or newer
* pip
* Windows, Linux, or macOS

The project was developed and tested using Python 3.14.

---

# Installation

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd geospatial-measurement-api
```

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

# Running the Application

Start the FastAPI development server:

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

Open:

```text
http://127.0.0.1:8000/docs
```

### ReDoc

Open:

```text
http://127.0.0.1:8000/redoc
```

---

# API Endpoints

## 1. Upload Geospatial File

### Request

```http
POST /api/files/
```

Upload either:

* `.kml`
* `.zip` containing a Shapefile

### Example using cURL

```bash
curl -X POST "http://127.0.0.1:8000/api/files/" \
  -F "file=@data/test.kml"
```

### Example response

```json
{
  "id": "generated-file-id",
  "filename": "test.kml",
  "file_type": ".kml",
  "feature_count": 3,
  "crs": "EPSG:4326",
  "status": "PROCESSED"
}
```

---

# 2. Get File Information

### Request

```http
GET /api/files/{file_id}
```

### Example

```text
GET /api/files/123456
```

### Response

```json
{
  "id": "123456",
  "filename": "test.kml",
  "file_type": ".kml",
  "feature_count": 3,
  "crs": "EPSG:4326",
  "status": "PROCESSED",
  "created_at": "2026-10-07T10:30:00"
}
```

---

# 3. Get Measurements

### Request

```http
GET /api/files/{file_id}/measurements
```

### Response

```json
{
  "file_id": "123456",
  "filename": "test.kml",
  "crs": "EPSG:4326",
  "features": [
    {
      "feature_id": 0,
      "geometry_type": "Point",
      "geometry": "POINT (73.7898 19.9975)",
      "crs": "EPSG:4326",
      "properties": {},
      "measurement_type": null,
      "measurement_value": null,
      "measurement_unit": null
    },
    {
      "feature_id": 1,
      "geometry_type": "LineString",
      "geometry": "LINESTRING (...)",
      "crs": "EPSG:4326",
      "properties": {},
      "measurement_type": "length",
      "measurement_value": 105.2,
      "measurement_unit": "meters"
    },
    {
      "feature_id": 2,
      "geometry_type": "Polygon",
      "geometry": "POLYGON (...)",
      "crs": "EPSG:4326",
      "properties": {},
      "measurement_type": "area",
      "measurement_value": 11200.5,
      "measurement_unit": "square meters"
    }
  ]
}
```

The exact measurement values depend on the uploaded geometry.

---

# Architecture

The application follows a simple layered architecture.

```text
Client
  │
  ▼
FastAPI Routes
  │
  ▼
File Service
  │
  ├── Save uploaded file
  │
  ▼
Geospatial Service
  │
  ├── Validate ZIP
  ├── Extract Shapefile
  ├── Read KML/Shapefile
  └── Extract features
  │
  ▼
Measurement Service
  │
  ├── Check CRS
  ├── Transform geographic CRS
  └── Calculate measurements
  │
  ▼
Database Service
  │
  ├── FileRecord
  └── FeatureRecord
  │
  ▼
API Response
```

---

# Processing Flow

## Step 1: Upload

The client sends a KML or ZIP file using the upload endpoint.

## Step 2: Validation

The application checks the file extension.

Supported extensions:

```text
.kml
.zip
```

For ZIP files, the application checks whether the archive contains the required Shapefile components:

```text
.shp
.shx
.dbf
```

## Step 3: Extraction

If the uploaded file is a ZIP archive, it is safely extracted into:

```text
data/extracted/
```

The application also checks ZIP paths to prevent unsafe path traversal.

## Step 4: Reading

GeoPandas reads the geospatial data and creates a `GeoDataFrame`.

The application supports:

```text
KML
Shapefile
```

## Step 5: Feature Extraction

For every feature, the application extracts:

* Feature index
* Geometry type
* Geometry
* Properties

## Step 6: Measurement

The geometry is passed to the measurement service.

The service determines the appropriate measurement based on geometry type.

## Step 7: Database Storage

File metadata and feature information are stored in SQLite using SQLAlchemy.

## Step 8: Response

The API returns the processed file information and measurement results.

---

# Measurement Logic

The measurement service follows these rules:

| Geometry        | Measurement |
| --------------- | ----------- |
| Point           | None        |
| LineString      | Length      |
| MultiLineString | Length      |
| Polygon         | Area        |
| MultiPolygon    | Area        |

### Polygon

```python
geometry.area
```

Result:

```text
square meters
```

### LineString

```python
geometry.length
```

Result:

```text
meters
```

### Point

No measurement is calculated.

---

# CRS Handling

Coordinate Reference System handling is an important part of the application.

Geographic CRS such as:

```text
EPSG:4326
```

uses latitude and longitude in degrees.

Calculating area or length directly from geographic coordinates would produce incorrect units and inaccurate measurements.

Therefore, the application checks the CRS before measurement.

### Geographic CRS

If the CRS is geographic:

```text
EPSG:4326
```

the application estimates a suitable UTM projected CRS.

The geometry is then transformed using:

```python
gdf.to_crs(projected_crs)
```

Measurements are calculated only after this transformation.

### Already Projected CRS

If the input data already uses a projected CRS, the application uses that CRS directly.

### Missing CRS

If CRS information is missing, the application raises an error instead of silently producing potentially incorrect measurements.

---

# Database Design

The application uses SQLite with SQLAlchemy.

## Files Table

Stores information about uploaded files.

Main fields:

```text
id
filename
file_type
feature_count
crs
status
error_message
created_at
```

## Features Table

Stores individual geospatial features.

Main fields:

```text
id
file_id
feature_index
geometry_type
geometry
properties
measurement_type
measurement_value
measurement_unit
```

A file can contain multiple features.

Relationship:

```text
Files
  │
  └───< Features
```

---

# Testing

The project uses `pytest`.

Run the tests with:

```powershell
python -m pytest
```

Current test coverage includes:

* Health endpoint
* Invalid file type
* File not found
* Geospatial measurement calculation

Expected result:

```text
4 passed
```

---

# Design Decisions

## FastAPI

FastAPI was selected because it provides:

* Simple API development
* Automatic OpenAPI documentation
* Swagger UI
* Type validation
* Good support for asynchronous APIs

## GeoPandas

GeoPandas provides convenient support for reading and processing geospatial datasets.

## Shapely

Shapely is used for geometry operations such as:

* Area
* Length
* Geometry type

## SQLAlchemy + SQLite

SQLite keeps the project lightweight and easy to run locally.

SQLAlchemy provides a clean database abstraction.

## Service-Based Structure

Geospatial processing and measurement calculations are separated from API routes.

This makes the application easier to:

* Test
* Maintain
* Extend
* Debug

---

# Error Handling

The API handles common errors such as:

* Unsupported file types
* Missing files
* Invalid Shapefile ZIP archives
* Missing CRS
* Invalid geospatial data

Example:

```json
{
  "detail": "Unsupported file type. Only .kml and .zip files are allowed."
}
```

---

# Security Considerations

The application includes basic security measures for uploaded ZIP files.

ZIP archive paths are checked before extraction to prevent path traversal attacks.

The original uploaded filename is also reduced to its filename component before saving.

Future versions could add:

* Maximum upload size
* Authentication
* Rate limiting
* Malware scanning
* Stronger archive validation

---

# Learning

Through this project, I learned:

* FastAPI REST API development
* GeoPandas and geospatial data processing
* KML and Shapefile handling
* CRS concepts and coordinate transformation
* UTM projection selection
* Shapely geometry measurements
* SQLAlchemy database integration
* File upload handling
* Automated API and service testing
* Basic ZIP security validation
* Structuring a backend application into services and models

---

# Future Improvements

Possible future improvements include:

1. Support for GeoJSON and other geospatial formats
2. Return geometry as GeoJSON instead of WKT
3. Add asynchronous/background processing for large files
4. Add upload size limits
5. Add authentication and authorization
6. Add pagination for large feature collections
7. Store measurement CRS separately from source CRS
8. Add more comprehensive test datasets
9. Add Docker support
10. Deploy the API to a cloud platform
11. Add frontend visualization using React and maps
12. Add more geometry types such as MultiPoint and GeometryCollection

---

# Example Test Dataset

The project includes:

```text
data/test.kml
```

The sample contains:

* Point
* LineString
* Polygon

This makes it possible to test all three measurement cases.

---

# License

This project was developed as part of a geospatial backend take-home assignment.
