"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from io import StringIO
from unittest.mock import Mock

import pytest
from parkapi_sources.converters.bfrk import BfrkBikePushConverter, BfrkCarPushConverter

from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def bfrk_car_push_converter(mocked_config_helper: Mock) -> BfrkCarPushConverter:
    return BfrkCarPushConverter(config_helper=mocked_config_helper)


class BfrkCarPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(bfrk_car_push_converter: BfrkCarPushConverter):
        with get_data_path('bfrk_car.csv').open() as bfrk_car_file:
            bfrk_car_data = StringIO(bfrk_car_file.read())

        static_parking_site_inputs, import_parking_site_exceptions = bfrk_car_push_converter.handle_csv_string(bfrk_car_data)

        assert len(static_parking_site_inputs) > len(
            import_parking_site_exceptions
        ), 'There should be more valid then invalid parking sites'

        validate_static_parking_site_inputs(static_parking_site_inputs)


@pytest.fixture
def bfrk_bike_push_converter(mocked_config_helper: Mock) -> BfrkBikePushConverter:
    return BfrkBikePushConverter(config_helper=mocked_config_helper)


class BfrkBikePullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(bfrk_bike_push_converter: BfrkBikePushConverter):
        with get_data_path('bfrk_bike.csv').open() as bfrk_bike_file:
            bfrk_bike_data = StringIO(bfrk_bike_file.read())

        static_parking_site_inputs, import_parking_site_exceptions = bfrk_bike_push_converter.handle_csv_string(bfrk_bike_data)

        assert len(static_parking_site_inputs) > len(
            import_parking_site_exceptions
        ), 'There should be more valid then invalid parking sites'

        validate_static_parking_site_inputs(static_parking_site_inputs)
