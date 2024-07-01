"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""
from datetime import datetime, timezone

import pyproj
from validataclass.dataclasses import validataclass, DefaultUnset
from validataclass.helpers import OptionalUnsetNone
from validataclass.validators import IntegerValidator, DecimalValidator, StringValidator, Noneable, BooleanValidator

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import PurposeType


@validataclass
class VrnBikeInput:
    uid: int = IntegerValidator(allow_strings=True)
    lat: str = DecimalValidator()
    lon: str = DecimalValidator()
    stadt: str = StringValidator(max_length=255)
    capacity: int = IntegerValidator(allow_strings=True)
    name: str = StringValidator(min_length=2, max_length=255)
    is_covered: OptionalUnsetNone[bool] = Noneable(BooleanValidator()), DefaultUnset,


    def to_parking_site_input(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=self.uid,
            name=self.name,
            address=f'{self.name}+ {self.stadt}',
            capacity=self.capacity,
            lat=self.lat,
            lon=self.lon,
            static_data_updated_at=datetime.now(tz=timezone.utc),
            purpose=PurposeType.BIKE,
            has_fee=True,
            fee_description='https://www.vrnradbox.de/order/booking#',
            is_covered=self.is_covered,


        )
