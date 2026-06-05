from datetime import date, timedelta

from src.modules.agenda.domain.valueObjects import Date, DayStatus


class CalendarDataClient:
    def pullData(self):
        return []

    async def mont(self, mes: int | str, ano: int | str) -> list[dict]:
        year = int(ano)
        current = date(year, 1, 1)
        days = []
        for _ in range(365):
            month = current.month
            day = current.day
            days.append(
            {
                "rooms": [],
                "date": Date(day=day, month=month, year=year),
                    "weekday": current.weekday(),
                "availability": True,
                "status": DayStatus.AVAILABLE,
                "rules": [],
            }
            )
            current += timedelta(days=1)
        return days
