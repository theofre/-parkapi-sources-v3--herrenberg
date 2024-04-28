"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import requests
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import PullConverter, StaticGeojsonDataMixin
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .validators import HeidelbergRealtimeInput, HeidelbergRealtimeUpdateInput


class HeidelbergPullConverter(PullConverter, StaticGeojsonDataMixin):
    required_config_keys = ['PARK_API_HEIDELBERG_API_KEY']
    heidelberg_realtime_validator = DataclassValidator(HeidelbergRealtimeInput)
    heidelberg_realtime_update_validator = DataclassValidator(HeidelbergRealtimeUpdateInput)
    source_info = SourceInfo(
        uid='heidelberg',
        name='Stadt Heidelberg',
        public_url='https://parken.heidelberg.de',
        source_url='https://parken.heidelberg.de/v1',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Heidelberg',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        return self._get_static_parking_site_inputs_and_exceptions(source_uid=self.source_info.uid)

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = requests.get(
            f'{self.source_info.source_url}/parking-update',
            params={'key': self.config_helper.get('PARK_API_HEIDELBERG_API_KEY')},
            headers={
                'Accept': 'application/json; charset=utf-8',
                'Referer': 'https://parken.heidelberg.de',
            },
            timeout=30,
        )
        response_data = response.json()
        try:
            realtime_input = self.heidelberg_realtime_validator.validate(response_data)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'Invalid Input at source {self.source_info.uid}: {e.to_dict()}, data: {response_data}',
            ) from e

        for update_dict in realtime_input.data.parkingupdates:
            try:
                update_input = self.heidelberg_realtime_update_validator.validate(update_dict)
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=update_dict.get('parkinglocation'),
                        message=f'Invallid data at uid {update_dict.get("parkinglocation")}: {e.to_dict()}, ' f'data: {update_dict}',
                    ),
                )
                continue

            realtime_parking_site_inputs.append(
                update_input.to_realtime_parking_site_input(
                    realtime_data_updated_at=realtime_input.data.updated,
                ),
            )

        return realtime_parking_site_inputs, import_parking_site_exceptions
