"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""
import csv
from io import StringIO

import pyproj
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.push.csv_converter import CsvConverter
from parkapi_sources.converters.vrn.validator import VrnBikeInput
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import SourceInfo, StaticParkingSiteInput, RealtimeParkingSiteInput


class VrnBikePushConverter(CsvConverter):
    vrnvalidator = DataclassValidator(VrnBikeInput)

    source_info = SourceInfo(
        uid='VRN',
        name='VRN : Fahradstellplätze',
        public_url='https://www.vrn.de/opendata/datasets/fahrradabstellanlagen',
        has_realtime_data=False,
    )

    header_mapping: dict[str, str] = {
        'id': 'uid',
        'address': 'name',
        'capacity': 'capacity',
        'X': 'lon',
        'Y': 'lat',
        'data_source': 'stadt',

    }

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
                print(input_dict)
                input = self.vrnvalidator.validate(input_dict)
                print(input)
            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=input_dict.get('name'),
                        message=f'validation error for {input_dict}: {e.to_dict()}',
                    ),
                )
                continue

            static_parking_site_inputs.append(input.to_parking_site_input())

        return static_parking_site_inputs, static_parking_site_errors
