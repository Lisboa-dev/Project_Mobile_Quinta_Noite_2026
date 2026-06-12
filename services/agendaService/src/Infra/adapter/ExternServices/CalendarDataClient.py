from calendar import monthrange
from datetime import date, timedelta
from typing import Any

from src.modules.agenda.domain.valueObjects import Date, DayStatus
from calendar import monthrange
from datetime import date, timedelta
from typing import Any
    

class CalendarDataClient:
    def pullData(self):
        return []

    from calendar import monthrange
    from datetime import date, timedelta
    from typing import Any
    

    async def mont(
            self,
            mes: int | str,
            ano: int | str,
        ) -> list[list[dict[str, Any]]]:

            last_month = int(mes)
            year = int(ano)

            if not 1 <= last_month <= 12:
                raise ValueError("O mês deve estar entre 1 e 12")

            hoje = date.today()
            calendar: list[list[dict[str, Any]]] = []

            for month in range(1, last_month + 1):
                days: list[dict[str, Any]] = []

                total_days = monthrange(year, month)[1]
                current = date(year, month, 1)

                for _ in range(total_days):
                    days.append(
                        {
                            "date": Date(
                                day=current.day,
                                month=current.month,
                                year=current.year,
                            ),
                            "weekday": current.weekday(),
                            "availability": current >= hoje,
                            "status": (
                                DayStatus.UNAVAILABLE
                                if current < hoje
                                else DayStatus.AVAILABLE
                            ),
                            "rules": [],
                        }
                    )

                    current += timedelta(days=1)

                calendar.append(days)

            return calendar

        