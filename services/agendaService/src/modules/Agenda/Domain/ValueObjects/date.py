from dataclasses import dataclass
from datetime import datetime


@dataclass
class Date:
    day: int
    month: int
    year: int
    
    def __str__(self):
        return f"{self.day}/{self.month}/{self.year}"
    
    @staticmethod
    def stringToObject(date):
        value = str(date).split("T", 1)[0].strip()
        for date_format in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                parsed = datetime.strptime(value, date_format)
                return Date(day=parsed.day, month=parsed.month, year=parsed.year)
            except ValueError:
                continue
        raise ValueError(f"invalid date format: {date}")
    
    def compare(self, date):
        return self.day == date.day and self.month == date.month and self.year == date.year
    
    def inRange(self, start, end):
        return self.day >= start.day and self.month >= start.month and self.year >= start.year and self.day <= end.day and self.month <= end.month and self.year <= end.year
    
    def isBefore(self, date: "Date"):
        return self.year < date.year or (self.year == date.year and self.month < date.month) or (self.year == date.year and self.month == date.month and self.day < date.day)
    
    @staticmethod
    def toDay():
       import datetime

       current_date = datetime.date.today()

       return Date(
            day=current_date.day,
            month=current_date.month,
            year=current_date.year,
        )
       
    
    @property
    def getDay(self):
        return self.day
