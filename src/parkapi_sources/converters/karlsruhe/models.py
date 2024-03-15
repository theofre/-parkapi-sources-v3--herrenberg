"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date, datetime, time, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional

import pyproj
from validataclass.dataclasses import validataclass
from validataclass.validators import (
    DataclassValidator,
    DateTimeValidator,
    EmailValidator,
    EnumValidator,
    IntegerValidator,
    Noneable,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.converters.base_converter.pull import GeojsonFeatureGeometryInput
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus
from parkapi_sources.validators import ParsedDateValidator


class KarlsruheOpeningStatus(Enum):
    OPEN = 'Geöffnet'
    CLOSED = 'Geschlossen'

    def to_opening_status(self) -> OpeningStatus:
        return {
            self.OPEN: OpeningStatus.OPEN,
            self.CLOSED: OpeningStatus.CLOSED,
        }.get(self, OpeningStatus.UNKNOWN)


@validataclass
class KarlsruhePropertiesInput:
    id: int = IntegerValidator()
    ph_name: str = StringValidator()
    gesamte_parkplaetze: int = IntegerValidator()
    freie_parkplaetze: Optional[int] = Noneable(IntegerValidator())
    max_durchfahrtshoehe: Optional[Decimal] = Noneable(NumericValidator())
    stand_freieparkplaetze: Optional[datetime] = Noneable(DateTimeValidator())
    parkhaus_strasse: str = StringValidator()
    parkhaus_plz: str = StringValidator()
    parkhaus_gemeinde: str = StringValidator()
    oeffnungsstatus: Optional[KarlsruheOpeningStatus] = Noneable(EnumValidator(KarlsruheOpeningStatus))
    bemerkung: Optional[str] = Noneable(StringValidator())
    parkhaus_internet: Optional[str] = Noneable(UrlValidator())
    parkhaus_telefon: Optional[str] = Noneable(StringValidator())
    parkhaus_email: Optional[str] = Noneable(EmailValidator())
    betreiber_internet: Optional[str] = Noneable(UrlValidator())
    betreiber_email: Optional[str] = Noneable(EmailValidator())
    betreiber_telefon: Optional[str] = Noneable(StringValidator())
    stand_parkhausdaten: date = ParsedDateValidator(date_format='%d.%m.%Y')

    def __post_init__(self):
        if self.max_durchfahrtshoehe == 0:  # 0 is used as None
            self.max_durchfahrtshoehe = None


@validataclass
class KarlsruheFeatureInput:
    id: str = StringValidator()
    geometry: GeojsonFeatureGeometryInput = DataclassValidator(GeojsonFeatureGeometryInput)
    properties: KarlsruhePropertiesInput = DataclassValidator(KarlsruhePropertiesInput)

    def to_static_parking_site_input(self, proj: pyproj.Proj) -> StaticParkingSiteInput:
        coordinates = proj(float(self.geometry.coordinates[1]), float(self.geometry.coordinates[0]), inverse=True)

        return StaticParkingSiteInput(
            uid=str(self.properties.id),
            name=self.properties.ph_name,
            lat=coordinates[1],
            lon=coordinates[0],
            address=f'{self.properties.parkhaus_strasse}, {self.properties.parkhaus_plz} {self.properties.parkhaus_gemeinde}',
            max_height=None if self.properties.max_durchfahrtshoehe is None else int(self.properties.max_durchfahrtshoehe * 100),
            public_url=self.properties.parkhaus_internet,
            static_data_updated_at=datetime.combine(self.properties.stand_parkhausdaten, time(), tzinfo=timezone.utc),
        )

    def to_realtime_parking_site_input(self) -> Optional[RealtimeParkingSiteInput]:
        if self.properties.stand_freieparkplaetze is None:
            return None

        if self.properties.oeffnungsstatus is None:
            opening_status = OpeningStatus.UNKNOWN
        else:
            opening_status = self.properties.oeffnungsstatus.to_opening_status()

        return RealtimeParkingSiteInput(
            uid=str(self.properties.id),
            realtime_capacity=self.properties.gesamte_parkplaetze,
            realtime_free_capacity=self.properties.freie_parkplaetze,
            realtime_opening_status=opening_status,
            realtime_data_updated_at=self.properties.stand_freieparkplaetze,
        )
