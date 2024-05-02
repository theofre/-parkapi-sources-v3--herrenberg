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

    def map_row_to_parking_site_dict(self, mapping: dict[str, int], row: list[Cell]) -> dict[str, Any]:
        parking_site_dict: dict[str, str] = {}

        for field in mapping.keys():
            parking_site_dict[field] = row[mapping[field]].value

        # TO DO: Maximale Parkdauer is in Minutes, which should be converted to seconds
        parking_site_dict['max_stay'] = parking_site_dict['max_stay'] * 60 if isinstance(parking_site_dict['max_stay'], int) else None

        parking_site_dict['type'] = self.type_mapping.get(parking_site_dict.get('type'))
        parking_site_dict['static_data_updated_at'] = datetime.now(tz=timezone.utc).isoformat()

        return parking_site_dict
