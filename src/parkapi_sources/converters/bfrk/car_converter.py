"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.validators import DataclassValidator

from parkapi_sources.models import SourceInfo

from .base_converter import BfrkBasePushConverter
from .car_models import BfrkCarRowInput


class BfrkCarPushConverter(BfrkBasePushConverter):
    bfrk_row_validator = DataclassValidator(BfrkCarRowInput)

    source_info = SourceInfo(
        uid='bfrk_car',
        name='Barrierefreie Reisekette: PKW-Parkplätze am Bahnhof',
        public_url='https://www.mobidata-bw.de/dataset/bfrk-barrierefreiheit-an-bw-bahnhoefen',
        has_realtime_data=False,
    )

    header_mapping: dict[str, str] = {
        'ID': 'uid',
        'HST_Name': 'name',
        'Art': 'type',
        'Latitude': 'lat',
        'Longitude': 'lon',
        'Stellplatzanzahl_insgesamt': 'capacity',
        'Stellplatzanzahl_Behinderte': 'capacity_disabled',
        'Nutzungsbedingungen': 'description',
        'HST_DHID': 'identifier_dhid',
        'OSM_ID': 'identifier_osm',
        'Parkplatz_Foto': 'photo_url',
    }
