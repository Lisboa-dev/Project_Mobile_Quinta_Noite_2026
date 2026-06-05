from dataclasses import dataclass
from src.modules.agenda.aplication.dtos.exceptions import CreateUseCaseException
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.events.CalendarEvent import CreateCalendarEvent
from src.modules.agenda.aplication.ports.externServices.CalendarDataPort import CalendarDataPort
from src.modules.agenda.aplication.ports.repository import RuleRepositoryPoty
from src.modules.agenda.aplication.ports.repository.CalendarRepositoryPort import CalendarRepositoryPort
from src.modules.agenda.domain.entities import Day


@dataclass(frozen=True)
class CreateCalendarCommand:
    day: int
    ano: int


class CreateCalendarUseCase:
    
    def __init__(
        self, 
        repositoryCalendar: CalendarRepositoryPort, 
        repositoryRule: RuleRepositoryPoty,
        baseData: CalendarDataPort, 
        bus: BusPort
):
        
        self._repositoryCalendar = repositoryCalendar
        self._repositoryRule = repositoryRule
        self._baseData = baseData
        self._bus = bus


    async def execute(self, command: CreateCalendarCommand):
        try:
            data = await self._baseData.mont(command.day, command.ano)
            rules = await self._repositoryRule.getDayRules()
            
            if data:
                
                days = []
                for d in data:
                    
                    try:
                        day = Day(**d)
                        day.addRules(rules)
                        await self._repositoryCalendar.save(day)
                        days.append(day)
                    except:
                        await self._repositoryCalendar.delete(d['ano'])
                        raise CreateUseCaseException(
                            code="CREATE_CALENDAR_DAY_ERROR",
                            message="Error creating calendar day",
                            use_case=self.__class__.__name__,
                            context={"day": str(d)},
                        )
                self._bus.emit(CreateCalendarEvent(days=days, year=str(command.ano)))
                return days
            
        except Exception as e:
            await self._repositoryCalendar.delete(command.ano)
            raise CreateUseCaseException(
                code="CREATE_CALENDAR_ERROR",
                message="Error creating calendar",
                use_case=self.__class__.__name__,
                context={"command": str(command)},
                original=e,
            ) from e
      
   
       
    
