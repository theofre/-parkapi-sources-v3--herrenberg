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

from .models import FreiburgFeatureInput


class FreiburgPullConverter(PullConverter, StaticGeojsonDataMixin):
    freiburg_realtime_feature_validator = DataclassValidator(FreiburgFeatureInput)
    source_info = SourceInfo(
        uid='freiburg',
        name='Freiburg',
        public_url='https://www.freiburg.de/pb/,Lde/231355.html',
        source_url='https://geoportal.freiburg.de/wfs/gdm_pls/gdm_plslive?request=getfeature&service=wfs&version=1.1.0&typename=pls'
        '&outputformat=geojson&srsname=epsg:4326',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Freiburg',
        attribution_license='dl-de/by-2-0',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        return self._get_static_parking_site_inputs_and_exceptions(source_uid=self.source_info.uid)

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = requests.get(self.source_info.source_url, timeout=30)
        response_data = response.json()

        try:
            realtime_input = self.geojson_validator.validate(response_data)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'Invalid Input at source {self.source_info.uid}: {e.to_dict()}, data: {response_data}',
            ) from e

        for update_dict in realtime_input.features:
            try:
                update_input = self.freiburg_realtime_feature_validator.validate(update_dict)
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=update_dict.get('properties').get('obs_parkid'),
                        message=f'Invalid data at uid {update_dict.get("properties").get("obs_parkid")}: '
                        f'{e.to_dict()}, data: {update_dict}',
                    ),
                )
                continue

            realtime_parking_site_inputs.append(update_input.to_realtime_parking_site_input())

        return realtime_parking_site_inputs, import_parking_site_exceptions
