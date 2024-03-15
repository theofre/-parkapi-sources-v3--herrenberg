"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from tests.converters.helper import static_geojson_callback


@pytest.fixture
def mocked_static_geojson_config_helper(mocked_config_helper: Mock) -> Mock:
    config = {'STATIC_GEOJSON_BASE_URL': 'mock://static-geojson'}
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def static_geojson_requests_mock(requests_mock: Mocker) -> Mocker:
    matcher = re.compile('mock://static-geojson/([0-9a-z-]*).geojson')
    requests_mock.get(matcher, json=static_geojson_callback)
    return requests_mock
