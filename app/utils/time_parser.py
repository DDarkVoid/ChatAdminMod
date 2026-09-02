import re


class TimeParser:
    UNITS = {
        "s": 1,
        "m": 60,
        "h": 3600,
    }

    @classmethod
    def parse(cls, value: str) -> int:
        value = value.strip().lower()

        match = re.fullmatch(r"(\d+)([smh])", value)

        if not match:
            raise ValueError("Неверный формат времени")

        amount = int(match.group(1))
        unit = match.group(2)

        if amount <= 0:
            raise ValueError("Время должно быть больше нуля")

        return amount * cls.UNITS[unit]
