"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from zoneinfo import ZoneInfo

from validataclass.dataclasses import DefaultUnset, validataclass
from validataclass.helpers import OptionalUnset
from validataclass.validators import (
    AnyOfValidator,
    DataclassValidator,
    DateTimeValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    NumericValidator,
    StringValidator,
)

from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType


class MannheimParkingSiteType(Enum):
    CAR_PARK = 'carPark'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.CAR_PARK: ParkingSiteType.CAR_PARK,
        }.get(self)


@validataclass
class MannheimBuchenLocationInput:
    coordinates: list[Decimal] = ListValidator(NumericValidator())
    type: str = AnyOfValidator(allowed_values=['Point'])


@validataclass
class MannheimBuchenAddressInput:
    street: OptionalUnset[str] = StringValidator(), DefaultUnset
    houseNo: OptionalUnset[str] = StringValidator(), DefaultUnset
    postalCode: OptionalUnset[str] = StringValidator(), DefaultUnset
    city: OptionalUnset[str] = StringValidator(), DefaultUnset


@validataclass
class MannheimBuchenInput:
    id: str = StringValidator()
    name: str = StringValidator()
    operatorId: str = StringValidator()
    dataType: str = AnyOfValidator(allowed_values=['parkingCar'])
    location: MannheimBuchenLocationInput = DataclassValidator(MannheimBuchenLocationInput)
    address: MannheimBuchenAddressInput = DataclassValidator(MannheimBuchenAddressInput)
    description: str = StringValidator()
    trafficType: str = AnyOfValidator(allowed_values=['car'])
    type: MannheimParkingSiteType = EnumValidator(MannheimParkingSiteType)
    capacity: int = IntegerValidator(min_value=0)
    free: int = IntegerValidator(min_value=0)
    timestamp: datetime = DateTimeValidator(local_timezone=ZoneInfo('Europe/Berlin'), target_timezone=timezone.utc)

    def to_static_parking_site(self, city: str) -> StaticParkingSiteInput:
        address = ''
        if self.address.street:
            address = self.address.street
            if self.address.houseNo:
                address += f' {self.address.houseNo}'
            address += ', '
        if self.address.postalCode:
            address += f' {self.address.postalCode}'
        if self.address.city:
            address += f' {self.address.city}'
        else:
            address += f' {city}'

        return StaticParkingSiteInput(
            uid=self.id,
            name=self.name,
            address=address,
            description=self.description,
            lat=self.location.coordinates[1],
            lon=self.location.coordinates[0],
            has_realtime_data=True,
            capacity=self.capacity,
            type=self.type.to_parking_site_type(),
            static_data_updated_at=self.timestamp,
        )

    def to_realtime_parking_site(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.id,
            realtime_data_updated_at=self.timestamp,
            realtime_capacity=self.capacity,
            realtime_free_capacity=self.free,
        )
