from pathlib import Path
import zipfile

import geopandas as gpd


EXTRACTED_DIR = Path("data/extracted")
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)


def validate_shapefile_zip(zip_path: Path) -> bool:

    with zipfile.ZipFile(zip_path, "r") as zip_file:
        files = zip_file.namelist()

    file_names = [
        Path(file).name
        for file in files
        if not file.endswith("/")
    ]

    shapefiles = {
        Path(file).stem
        for file in file_names
        if Path(file).suffix.lower() == ".shp"
    }

    if not shapefiles:
        return False

    for shapefile_name in shapefiles:

        required_files = {
            f"{shapefile_name}.shp",
            f"{shapefile_name}.shx",
            f"{shapefile_name}.dbf"
        }

        available_files = set(file_names)

        if required_files.issubset(available_files):
            return True

    return False
def extract_shapefile(zip_path: Path, file_id: str) -> Path:
    extract_directory = EXTRACTED_DIR / file_id
    extract_directory.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_file:

        for member in zip_file.infolist():

            member_path = Path(member.filename)

            if member_path.is_absolute() or ".." in member_path.parts:
                raise ValueError(
                    "Unsafe ZIP file: invalid file path detected."
                )

        zip_file.extractall(extract_directory)

    shapefiles = list(extract_directory.rglob("*.shp"))

    if not shapefiles:
        raise ValueError(
            "No .shp file found inside the ZIP file."
        )

    return shapefiles[0]


def read_kml(file_path: Path) -> gpd.GeoDataFrame:

    gdf = gpd.read_file(
        file_path,
        driver="KML"
    )

    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")

    return gdf


def read_shapefile(file_path: Path) -> gpd.GeoDataFrame:
    return gpd.read_file(file_path)


def read_geospatial_file(
    file_path: Path,
    file_id: str,
    extension: str
) -> gpd.GeoDataFrame:

    if extension == ".kml":
        return read_kml(file_path)

    if extension == ".zip":

        if not validate_shapefile_zip(file_path):
            raise ValueError(
                "ZIP file does not contain a valid Shapefile. "
                "Required files: .shp, .shx and .dbf."
            )

        shapefile_path = extract_shapefile(
            file_path,
            file_id
        )

        return read_shapefile(shapefile_path)

    raise ValueError(
        "Unsupported geospatial file type."
    )

def extract_features(gdf):
    features = []

    for index, row in gdf.iterrows():

        geometry = row.geometry

        properties = {}

        for column in gdf.columns:
            if column != "geometry":
                value = row[column]

                if value is not None:
                    properties[column] = str(value)

        features.append({
            "feature_index": int(index),
            "geometry_type": geometry.geom_type,
            "geometry": geometry.wkt if geometry else None,
            "properties": properties
        })

    return features