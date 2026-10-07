import geopandas as gpd

from app.services.measurement_service import calculate_measurements


def test_kml_measurements():

    gdf = gpd.read_file(
        "data/test.kml",
        driver="KML"
    )

    results = calculate_measurements(gdf)

    assert len(results) == 3


    assert results[0]["geometry_type"] == "Point"
    assert results[0]["measurement_value"] is None

    
    assert results[1]["geometry_type"] == "LineString"
    assert results[1]["measurement_type"] == "length"
    assert results[1]["measurement_value"] is not None

    
    assert results[2]["geometry_type"] == "Polygon"
    assert results[2]["measurement_type"] == "area"
    assert results[2]["measurement_value"] is not None