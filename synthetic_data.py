from datetime import date, timedelta

from database import session
from model import LightingSample


def main() -> None:
    with session() as sess:
        day = date(2024, 1, 1)
        while day.year < 2025:
            day = day + timedelta(days=1)


if __name__ == "__main__":
    main()
