"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import Any

from openpyxl.cell import Cell

from parkapi_sources.converters.base_converter.push import NormalizedXlsxConverter
from parkapi_sources.models import SourceInfo


class EllwangenPushConverter(NormalizedXlsxConverter):

    source_info = SourceInfo(
        uid='ellwangen',
        name='Ellwangen Parkdaten',
        public_url='https://www.ellwangen.de',
        has_realtime_data=False,
    )

    # If there are more tables with our defined format, it would make sense to move header_row to XlsxConverter
    header_row: dict[str, str] = {
        'ID': 'uid',
        'Name': 'name',
        'Art der Anlage': 'type',
        'Betreiber Name': 'operator_name',
        'Längengrad': 'lat',
        'Breitengrad': 'lon',
        'Adresse mit PLZ und Stadt': 'address',
        'Maximale Parkdauer / min': 'max_stay',
        'Anzahl Stellplätze': 'capacity',
        'Anzahl Carsharing-Parkplätze': 'capacity_carsharing',
        'Anzahl Ladeplätze': 'capacity_charging',
        'Anzahl Frauen-parkplätze': 'capacity_woman',
        'Anzahl Behinderten-parkplätze': 'capacity_disabled',
        'Anlage beleuchtet': 'has_lighting',
        'gebührenpflichtig': 'has_fee',
        'Existieren Live-Daten': 'has_realtime_data',
        'Gebühren-Informationen': 'fee_description',
        'Webseite': 'public_url',
        'Park&Ride': 'is_park_and_ride',
        '24/7 geöffnet': 'opening_hours_is_24_7',
        'Öffnungszeiten Mo-Fr Beginn': 'opening_hours_weekday_begin',
        'Öffnungszeiten Mo-Fr Ende': 'opening_hours_weekday_end',
        'Öffnungszeiten Sa Beginn': 'opening_hours_saturday_begin',
        'Öffnungszeiten Sa Ende': 'opening_hours_saturday_end',
        'Öffnungszeiten So Beginn': 'opening_hours_sunday_begin',
        'Öffnungszeiten So Ende': 'opening_hours_sunday_end',
        'Weitere öffentliche Informationen': 'description',
    }

    def map_row_to_parking_site_dict(self, mapping: dict[str, int], row: list[Cell]) -> dict[str, Any]:
        parking_site_dict: dict[str, str] = {}

        for field in mapping.keys():
            parking_site_dict[field] = row[mapping[field]].value

        # TO DO: Maximale Parkdauer is in Minutes, which should be converted to seconds
        parking_site_dict['max_stay'] = parking_site_dict['max_stay'] * 60 if isinstance(parking_site_dict['max_stay'], int) else None

        parking_site_dict['type'] = self.type_mapping.get(parking_site_dict.get('type'))
        parking_site_dict['static_data_updated_at'] = datetime.now(tz=timezone.utc).isoformat()

        return parking_site_dict
