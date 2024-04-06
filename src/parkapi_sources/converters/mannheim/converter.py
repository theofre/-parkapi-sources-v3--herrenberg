"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from typing import Optional

from bs4.element import Tag

from parkapi_sources.converters.base_converter.pull import PullConverter, PullScraperMixin, StaticGeojsonDataMixin
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput


class MannheimPullConverter(PullConverter, StaticGeojsonDataMixin, PullScraperMixin):
    source_info = SourceInfo(
        uid='mannheim',
        name='Stadt Mannheim',
        public_url='https://www.parken-mannheim.de',
        timezone='Europe/Berlin',
        attribution_contributor='Mannheimer Parkhausbetriebe GmbH',
        attribution_url='https://www.parken-mannheim.de/impressum',
        has_realtime_data=True,
    )
    _parking_site_uids_to_ignore: list[str] = ['b8874acd-39d9-424c-9405-1fc3307b7df8']

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        return self._get_static_parking_site_inputs_and_exceptions(source_uid=self.source_info.uid)

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return self._get_scraped_realtime_parking_site_inputs_and_exceptions()

    def get_realtime_tags_and_params(self) -> tuple[list[Tag], dict]:
        root = self.load_url_in_soup()

        realtime_data_updated_at_text = root.find_all('div', id='parkhausliste-ct')[-1].find('p').text
        realtime_data_updated_at = datetime.strptime(realtime_data_updated_at_text, 'zuletzt aktualisiert am %d.%m.%Y, %H:%M Uhr')

        tags = root.find_all(class_='parkhaus-lnk')

        return tags, {'realtime_data_updated_at': realtime_data_updated_at}

    def realtime_tag_to_dict(self, tag: Tag, realtime_data_updated_at: Optional[datetime] = None, **kwargs) -> Optional[dict]:
        realtime_parking_site_dict = {'realtime_data_updated_at': realtime_data_updated_at.isoformat()}
        parking_site_uid = tag.attrs.get('href').split('/')[-1]

        if parking_site_uid in self._parking_site_uids_to_ignore:
            return None

        realtime_parking_site_dict['uid'] = parking_site_uid
        realtime_parking_site_dict['realtime_free_capacity'] = int(tag.parent.find_next_sibling().text)

        return realtime_parking_site_dict
