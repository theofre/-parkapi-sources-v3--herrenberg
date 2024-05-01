"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
from typing import Any

from validataclass.exceptions import ValidationError
from validataclass.validators import ListValidator


class PointCoordinateTupleValidator(ListValidator):
    PATTERN = re.compile(r'POINT \(([-+]?\d+\.\d+) ([-+]?\d+\.\d+)\)')

    def validate(self, input_data: Any, **kwargs) -> list:
        self._ensure_type(input_data, str)
        input_match = re.match(self.PATTERN, input_data)

        if input_match is None:
            raise ValidationError(code='invalid_tuple_input', reason='invalid point coordinate tuple input')

        input_data = [input_match.group(1), input_match.group(2)]

        return super().validate(input_data, **kwargs)
