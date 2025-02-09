import math

import pytest

from wkz.gis.geo import (
    add_elevation_data_to_coordinates,
    calculate_distance_between_points,
    get_list_of_coordinates,
    get_location_name,
    get_total_distance_of_trace,
)


def test_calculate_distance_between_points__same_points():
    coordinate_1 = (48.0, 9.0)
    coordinate_2 = (48.0, 9.0)
    assert calculate_distance_between_points(coordinate_1, coordinate_2) == 0.0


def test_calculate_distance_between_points__different_points():
    coordinate_1 = (48.123, 9.456)
    coordinate_2 = (49.678, 9.567)
    distance = calculate_distance_between_points(coordinate_1, coordinate_2)
    assert math.isclose(distance, 173291.21920642233, abs_tol=0.01)


def test_calculate_distance_between_points__other_points():
    coordinate_1 = (48.0, 8.0)
    coordinate_2 = (48.0, 8.1)
    distance = calculate_distance_between_points(coordinate_1, coordinate_2)
    assert math.isclose(distance, 7448.684105664539, abs_tol=0.01)


def test_get_total_distance_of_trace__basic():
    with pytest.raises(ValueError):
        get_total_distance_of_trace(longitude_list=[0], latitude_list=[0])
    with pytest.raises(ValueError):
        get_total_distance_of_trace(longitude_list=[0], latitude_list=[0, 1])
    with pytest.raises(ValueError):
        get_total_distance_of_trace(longitude_list=[0, 1], latitude_list=[0])
    assert get_total_distance_of_trace(longitude_list=[48, 48], latitude_list=[8, 9]) == 111.32
    assert get_total_distance_of_trace(longitude_list=[48, 48], latitude_list=[-8, -9]) == 111.32
    assert get_total_distance_of_trace(longitude_list=[-48, -48], latitude_list=[-8, -9]) == 111.32
    assert get_total_distance_of_trace(longitude_list=[-48, -48], latitude_list=[8, 9]) == 111.32


def test_get_total_distance_of_trace__reversed_points():
    assert get_total_distance_of_trace(longitude_list=[99, 98], latitude_list=[16, 16]) == 107.01


def test_add_elevation_data_to_coordinates():
    assert (
        add_elevation_data_to_coordinates(
            coordinates=[(8, 49), (9, 50), (10, 51)],
            altitude=[248, 249, 250],
        )
        == [(8, 49, 248), (9, 50, 249), (10, 51, 250)]
    )


def test__get_location_name():
    coordinate = (48.1234, 8.9123)
    location_name = get_location_name(coordinate=coordinate)
    assert location_name == "Heidenstadt"

    coordinate = (49.47950, 8.47102)
    location_name = get_location_name(coordinate=coordinate)
    assert location_name == "Mannheim"

    # this would raise an exception in geopy so we expect to get None
    coordinate = (-90, 90)
    location_name = get_location_name(coordinate=coordinate)
    assert location_name is None


def test_get_other_location_names():
    coordinate = (49.46278064511717, 8.160513974726202)
    location_name = get_location_name(coordinate=coordinate)
    assert location_name == "Bad Dürkheim"


def test_get_list_of_coordinates__empty_data():
    lon = []
    lat = []
    coordinates = get_list_of_coordinates(lon, lat)

    assert coordinates == []


def test_get_list_of_coordinates__dummy_data():
    lon = [48.1, 48.2, 48.3, 48.4, 48.5, 48.6, 48.7, 48.8, 48.9, 49.0, 49.1]
    lat = [9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 10.0, 10.1, 10.2, 10.3]
    coordinates = get_list_of_coordinates(lon, lat)

    # note that because of configuration.every_nth_value only every nth value will be used
    assert coordinates == [(48.1, 9.3), (48.6, 9.8), (49.1, 10.3)]


def test_get_list_of_coordinates__data_with_gaps():
    lon = [None, 48.1234, None, 49.2345, None, 49.2345]
    lat = [None, 9.4567, None, 10.5678, None, 11.2345]
    coordinates = get_list_of_coordinates(lon, lat)

    # note that because of configuration.every_nth_value only every nth value will be used
    assert coordinates == [(49.2345, 11.2345), (49.2345, 11.2345)]
