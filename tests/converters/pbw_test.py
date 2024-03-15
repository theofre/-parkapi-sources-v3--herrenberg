"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
from parkapi_sources.converters.pbw import PbwPullConverter
from requests_mock import Mocker

from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs

if TYPE_CHECKING:
    from requests_mock.request import Request
    from requests_mock.response import Context


@pytest.fixture
def pbw_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_PBW_API_KEY': 'ffe455aa-7ca9-4281-b5c4-0c7561f9b514',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def pbw_pull_converter(pbw_config_helper: Mock) -> PbwPullConverter:
    return PbwPullConverter(config_helper=pbw_config_helper)


class PbwPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(pbw_pull_converter: PbwPullConverter, requests_mock: Mocker):
        def generate_response(request: 'Request', context: 'Context'):
            request_type = request.qs['type'][0]
            if request_type == 'catalog-city':
                filename = 'catalog-city.json'
            elif request_type == 'object-by-city':
                filename = f'object-by-city-{request.qs["id"][0]}.json'
            else:
                return {}
            json_path = Path(Path(__file__).parent, 'data', 'pbw', filename)
            with json_path.open() as json_file:
                json_data = json_file.read()

            return json.loads(json_data)

        requests_mock.get(
            'https://www.mypbw.de/api/',
            json=generate_response,
        )

        static_parking_site_inputs, import_parking_site_exceptions = pbw_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 98
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(pbw_pull_converter: PbwPullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'pbw', 'object-dynamic-all.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://www.mypbw.de/api/',
            text=json_data,
        )

        realtime_parking_site_inputs, import_parking_site_exceptions = pbw_pull_converter.get_realtime_parking_sites()

        assert len(realtime_parking_site_inputs) == 98
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
