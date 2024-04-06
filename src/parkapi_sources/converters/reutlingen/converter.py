"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import csv
from datetime import datetime, timezone
from io import StringIO

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.push import CsvConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .validation import ReutlingenRowInput


class ReutlingenPushConverter(CsvConverter):
    reutlingen_row_validator = DataclassValidator(ReutlingenRowInput)

    source_info = SourceInfo(
        uid='reutlingen',
        name='Stadt Reutlingen',
        public_url='https://www.reutlingen.de',
        has_realtime_data=False,
    )

    header_mapping: dict[str, str] = {'id': 'uid', 'ort': 'name', 'Kapazität': 'capacity', 'GEOM': 'coordinates', 'type': 'type'}

    def handle_csv_string(
        self,
        data: StringIO,
    ) -> tuple[list[StaticParkingSiteInput | RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return self.handle_csv(list(csv.reader(data, dialect='unix', delimiter=',')))

    def handle_csv(self, data: list[list]) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        mapping: dict[str, int] = self.get_mapping_by_header(self.header_mapping, data[0])

        # We start at row 2, as the first one is our header
        for row in data[1:]:
            input_dict: dict[str, str] = {}
            for field in self.header_mapping.values():
                input_dict[field] = row[mapping[field]]

            try:
                input_data: ReutlingenRowInput = self.reutlingen_row_validator.validate(input_dict)
            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        uid=input_dict.get('uid'),
                        message=f'validation error for {input_dict}: {e.to_dict()}',
                    ),
                )
                continue

            parking_site_input = StaticParkingSiteInput(
                uid=str(input_data.uid),
                name=input_data.name,
                address=f'{input_data.name}, Reutlingen',
                lat=input_data.coordinates[1],
                lon=input_data.coordinates[0],
                type=input_data.type.to_parking_site_type_input(),
                capacity=input_data.capacity,
                static_data_updated_at=datetime.now(tz=timezone.utc),
            )
            static_parking_site_inputs.append(parking_site_input)

        return static_parking_site_inputs, static_parking_site_errors
