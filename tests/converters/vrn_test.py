"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from io import StringIO
from unittest.mock import Mock

import pytest
from parkapi_sources.converters import VrnBikePushConverter

from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def vrn_converter(mocked_config_helper: Mock) -> VrnBikePushConverter:
    return VrnBikePushConverter(config_helper=mocked_config_helper)


class VrnPushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(vrn_converter: VrnBikePushConverter):
        with get_data_path('vrn.csv').open() as vrn_input:
            vrn_data = StringIO(vrn_input.read())

        static_parking_site_inputs, import_parking_site_exceptions = vrn_converter.handle_csv_string(vrn_data)
        print(len(import_parking_site_exceptions))
        print(len(static_parking_site_inputs))

        assert len(static_parking_site_inputs) > len(
            import_parking_site_exceptions
        ), 'There should be more valid then invalid parking sites'

        #validate_static_parking_site_inputs(static_parking_site_inputs)
