"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from validataclass.exceptions import ValidationError
from validataclass.validators import AnythingValidator, DataclassValidator, ListValidator

from parkapi_sources.converters.base_converter.push import JsonConverter
from parkapi_sources.converters.mannheim_buchen.models import MannheimBuchenInput
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput


class MannheimBuchenBaseConverter(JsonConverter, ABC):
    mannheim_buchen_list_validator = ListValidator(AnythingValidator(allowed_types=[dict]))
    mannheim_buchen_validator = DataclassValidator(MannheimBuchenInput)

    def handle_json(
        self,
        data: dict | list,
    ) -> tuple[list[StaticParkingSiteInput | RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        parking_site_inputs: list[StaticParkingSiteInput | RealtimeParkingSiteInput] = []
        parking_site_errors: list[ImportParkingSiteException] = []

        try:
            parking_site_dicts = self.mannheim_buchen_list_validator.validate(data)
        except ValidationError as e:
            raise ImportSourceException(source_uid=self.source_info.uid, message=f'Invalid data {e.to_dict()}') from e

        for parking_site_dict in parking_site_dicts:
            try:
                parking_site_input: MannheimBuchenInput = self.mannheim_buchen_validator.validate(parking_site_dict)

                parking_site_inputs.append(parking_site_input.to_static_parking_site(city=self.source_info.name))
                parking_site_inputs.append(parking_site_input.to_realtime_parking_site())

            except ValidationError as e:
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('uid'),
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )
        return parking_site_inputs, parking_site_errors


class MannheimPushConverter(MannheimBuchenBaseConverter):
    source_info = SourceInfo(
        uid='mannheim',
        name='Stadt Mannheim',
        public_url='https://www.parken-mannheim.de',
        timezone='Europe/Berlin',
        has_realtime_data=True,
    )


class BuchenPushConverter(MannheimBuchenBaseConverter):
    source_info = SourceInfo(
        uid='buchen',
        name='Stadt Buchen',
        public_url='https://www.buchen.de/ueber-buchen/kostenlos-parken.html',
        timezone='Europe/Berlin',
        has_realtime_data=True,
    )
