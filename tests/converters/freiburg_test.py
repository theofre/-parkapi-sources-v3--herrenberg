"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from parkapi_sources.converters import FreiburgPullConverter
from requests_mock import Mocker

from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def freiburg_pull_converter(mocked_static_geojson_config_helper: Mock) -> FreiburgPullConverter:
    return FreiburgPullConverter(config_helper=mocked_static_geojson_config_helper)


class FreiburgPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(freiburg_pull_converter: FreiburgPullConverter, requests_mock: Mocker):
        # We need to get GeoJSON data
        requests_mock.real_http = True

        json_path = Path(Path(__file__).parent, 'data', 'freiburg.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get('https://geoportal.freiburg.de/wfs/gdm_pls/gdm_plslive', text=json_data)

        static_parking_site_inputs, import_parking_site_exceptions = freiburg_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 20
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(freiburg_pull_converter: FreiburgPullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'freiburg.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get('https://geoportal.freiburg.de/wfs/gdm_pls/gdm_plslive', text=json_data)

        realtime_parking_site_inputs, import_parking_site_exceptions = freiburg_pull_converter.get_realtime_parking_sites()

        assert len(realtime_parking_site_inputs) == 19
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
