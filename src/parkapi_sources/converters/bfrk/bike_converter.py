"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.validators import DataclassValidator

from parkapi_sources.models import SourceInfo

from .base_converter import BfrkBasePushConverter
from .bike_models import BfrkBikeRowInput


class BfrkBikePushConverter(BfrkBasePushConverter):
    bfrk_row_validator = DataclassValidator(BfrkBikeRowInput)

    source_info = SourceInfo(
        uid='bfrk_bike',
        name='Barrierefreie Reisekette: Fahrrad-Parkplätze am Bahnhof',
        public_url='https://www.mobidata-bw.de/dataset/bfrk-barrierefreiheit-an-bw-bahnhoefen',
        has_realtime_data=False,
    )

    header_mapping: dict[str, str] = {
        'ID': 'uid',
        'HST_Name': 'name',
        'Anlagentyp': 'type',
        'Latitude': 'lat',
        'Longitude': 'lon',
        'Stellplatzanzahl': 'capacity',
        'beleuchtet': 'has_lighting',
        'kostenpflichtig': 'has_fee',
        'ueberdacht': 'has_roof',
        'HST_DHID': 'identifier_dhid',
        'OSM_ID': 'identifier_osm',
        'Anlage_Foto': 'photo_url',
    }
