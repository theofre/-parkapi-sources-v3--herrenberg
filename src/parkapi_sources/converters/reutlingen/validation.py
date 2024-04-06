"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
from enum import Enum
from typing import Any

from validataclass.dataclasses import validataclass
from validataclass.exceptions import ValidationError
from validataclass.validators import DecimalValidator, EnumValidator, IntegerValidator, ListValidator, StringValidator

from parkapi_sources.models.enums import ParkingSiteType
from parkapi_sources.validators import ExcelNoneable


class ReutlingenParkingSiteType(Enum):
    PARKHAUS = 'parkhaus'
    TIEFGARAGE = 'tiefgarage'
    PARKFLAECHE = 'parkfläche'
    P_R = 'p+r'

    def to_parking_site_type_input(self) -> ParkingSiteType:
        return {
            self.PARKHAUS: ParkingSiteType.CAR_PARK,
            self.TIEFGARAGE: ParkingSiteType.UNDERGROUND,
            self.PARKFLAECHE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self, ParkingSiteType.OTHER)


class PointCoordinateTupleValidator(ListValidator):
    PATTERN = re.compile(r'POINT \(([-+]?\d+\.\d+) ([-+]?\d+\.\d+)\)')

    def validate(self, input_data: Any, **kwargs) -> list:
        self._ensure_type(input_data, str)
        input_match = re.match(self.PATTERN, input_data)

        if input_match is None:
            raise ValidationError(code='invalid_tuple_input', reason='invalid point coordinate tuple input')

        input_data = [input_match.group(1), input_match.group(2)]

        return super().validate(input_data, **kwargs)


@validataclass
class ReutlingenRowInput:
    uid: int = IntegerValidator(allow_strings=True)
    type: ReutlingenParkingSiteType = EnumValidator(ReutlingenParkingSiteType)
    coordinates: list = PointCoordinateTupleValidator(DecimalValidator())
    capacity: str = ExcelNoneable(IntegerValidator(allow_strings=True))
    name: str = StringValidator(max_length=255)
