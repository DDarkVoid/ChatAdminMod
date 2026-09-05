"""Time interval parser."""

import re


class TimeParser(object):
    """Time string parser."""

    _units = {
        's': 1,
        'm': 60,
        'h': 3600,
    }

    @classmethod
    def parse(cls, time_str: str) -> int:
        """Convert string to seconds."""
        cleaned = time_str.strip().lower()
        match = re.fullmatch(r'(\d+)([smh])', cleaned)
        if not match:
            raise ValueError('Invalid time format')
        amount = int(match.group(1))
        unit = match.group(2)
        if amount <= 0:
            raise ValueError('Time must be greater than zero')
        return amount * cls._units[unit]
