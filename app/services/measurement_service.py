import geopandas as gpd


def get_projected_gdf(gdf):
    """
    Convert geographic coordinates to a suitable
    projected CRS for accurate measurements.
    """

    if gdf.crs is None:
        raise ValueError(
            "CRS is missing. Cannot calculate measurements safely."
        )

    # Already projected
    if not gdf.crs.is_geographic:
        return gdf

    # Geographic CRS such as EPSG:4326
    projected_crs = gdf.estimate_utm_crs()

    if projected_crs is None:
        raise ValueError(
            "Could not determine a suitable projected CRS."
        )

    return gdf.to_crs(projected_crs)


def calculate_measurements(gdf):

    projected_gdf = get_projected_gdf(gdf)

    results = []

    for index, row in projected_gdf.iterrows():

        geometry = row.geometry

        if geometry is None:
            continue

        geometry_type = geometry.geom_type

        if geometry_type == "Polygon":
            measurement_type = "area"
            measurement_value = geometry.area
            measurement_unit = "square meters"

        elif geometry_type == "MultiPolygon":
            measurement_type = "area"
            measurement_value = geometry.area
            measurement_unit = "square meters"

        elif geometry_type == "LineString":
            measurement_type = "length"
            measurement_value = geometry.length
            measurement_unit = "meters"

        elif geometry_type == "MultiLineString":
            measurement_type = "length"
            measurement_value = geometry.length
            measurement_unit = "meters"

        elif geometry_type == "Point":
            measurement_type = None
            measurement_value = None
            measurement_unit = None

        else:
            measurement_type = None
            measurement_value = None
            measurement_unit = None

        results.append({
            "feature_index": int(index),
            "geometry_type": geometry_type,
            "measurement_type": measurement_type,
            "measurement_value": measurement_value,
            "measurement_unit": measurement_unit
        })

    return results