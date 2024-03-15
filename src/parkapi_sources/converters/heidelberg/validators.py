"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from enum import Enum

from validataclass.dataclasses import validataclass
from validataclass.validators import AnythingValidator, DataclassValidator, EnumValidator, IntegerValidator, ListValidator

from parkapi_sources.models import RealtimeParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus
from parkapi_sources.validators import Rfc1123DateTimeValidator


class HeidelbergParkingSiteStatus(Enum):
    available = 'available'
    occupied = 'occupied'
    none = 'none'

    def to_opening_status(self) -> OpeningStatus:
        return {
            self.available: OpeningStatus.OPEN,
            # For some reason, occupied in API means closed
            self.occupied: OpeningStatus.CLOSED,
            self.none: OpeningStatus.UNKNOWN,
        }.get(self)


@validataclass
class HeidelbergRealtimeUpdateInput:
    parkinglocation: int = IntegerValidator()
    total: int = IntegerValidator()
    current: int = IntegerValidator()
    status: HeidelbergParkingSiteStatus = EnumValidator(HeidelbergParkingSiteStatus)

    def to_realtime_parking_site_input(self, realtime_data_updated_at: datetime) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=str(self.parkinglocation),
            realtime_capacity=self.total,
            realtime_free_capacity=self.current,
            realtime_opening_status=self.status.to_opening_status(),
            realtime_data_updated_at=realtime_data_updated_at,
        )


@validataclass
class HeidelbergRealtimeDataInput:
    parkingupdates: list[dict] = ListValidator(AnythingValidator(allowed_types=dict))
    updated: datetime = Rfc1123DateTimeValidator()


@validataclass
class HeidelbergRealtimeInput:
    data: HeidelbergRealtimeDataInput = DataclassValidator(HeidelbergRealtimeDataInput)
