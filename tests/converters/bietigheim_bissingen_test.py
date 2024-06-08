"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import Mock

import pytest

from parkapi_sources.converters import BietigheimBissingenPullConverter
from tests.converters.helper import validate_static_parking_site_inputs, validate_realtime_parking_site_inputs


@pytest.fixture
def bietigheim_bissingen_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_BIETIGHEIM_BISSINGEN_USER': '0152d634-9e16-46c0-bfef-20c0b623eaa3',
        'PARK_API_BIETIGHEIM_BISSINGEN_PASSWORD': 'eaf7a00c-d0e1-4464-a9dc-f8ef4d01f2cc',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def bietigheim_bissingen_pull_converter(bietigheim_bissingen_config_helper: Mock) -> BietigheimBissingenPullConverter:
    return BietigheimBissingenPullConverter(config_helper=bietigheim_bissingen_config_helper)


class BietigheimBissingenPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(bietigheim_bissingen_pull_converter: BietigheimBissingenPullConverter):

        static_parking_site_inputs, import_parking_site_exceptions = bietigheim_bissingen_pull_converter.get_static_parking_sites()

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(bietigheim_bissingen_pull_converter: BietigheimBissingenPullConverter):

        realtime_parking_site_inputs, import_parking_site_exceptions = bietigheim_bissingen_pull_converter.get_realtime_parking_sites()

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
