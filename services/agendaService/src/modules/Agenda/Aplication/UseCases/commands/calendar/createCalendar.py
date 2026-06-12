from dataclasses import dataclass
from src.modules.agenda.aplication.dtos.exceptions import CreateUseCaseException
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.events.CalendarEvent import CreateCalendarEvent
from src.modules.agenda.aplication.ports.externServices.CalendarDataPort import CalendarDataPort
from src.modules.agenda.aplication.ports.repository import RuleRepositoryPoty
from src.modules.agenda.aplication.ports.repository.CalendarRepositoryPort import CalendarRepositoryPort
from src.modules.agenda.domain.entities.Day import Day
from src.modules.agenda.domain.rules.BaseRule import BaseRule


@dataclass(frozen=True)
class CreateCalendarCommand:
    mes: int
    ano: int
    triggered_by_id: str | None = None


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


    async def execute(self, command: CreateCalendarCommand) -> UseCaseOutputDTO:
        try:
            data = await self._baseData.mont(command.mes, command.ano)
            rules = await self._repositoryRule.getDayRules()
            
            if data:
                
                print("\n\n\n antes",data, "\n\n\n\n")
                moths = []
                
                for month_days in data:
                    days = []
                    for d in month_days:
                        try:
                            day = Day(**d)
                            day.addRules(
                                [
                                    rule
                                    for rule in rules
                                    if isinstance(rule, BaseRule)
                                    and (
                                        (rule.date is not None and rule.date.compare(day.date))
                                        or (
                                            rule.weekday is not None
                                            and int(day.weekday) == int(rule.weekday)
                                        )
                                    )
                                ]
                            )
                            days.append(day)
                        except Exception as exc:
                            await self._repositoryCalendar.delete(command.ano)
                            raise CreateUseCaseException(
                                code="CREATE_CALENDAR_DAY_ERROR",
                                message="Error creating calendar day",
                                use_case=self.__class__.__name__,
                                context={"day": str(d)},
                                original=exc,
                            ) from exc
                   
                    moths.append(days)
                    
                await self._repositoryCalendar.saveMany(moths)

                event = CreateCalendarEvent.from_days(
                    days=days,
                    year=str(command.ano),
                    triggered_by_id=command.triggered_by_id,
                )
                await self._bus.emit(event)
                return UseCaseOutputDTO.ok(
                    use_case=self.__class__.__name__,
                    action="created",
                    resource="calendar",
                    resource_id=str(command.ano),
                    triggered_by_id=command.triggered_by_id,
                    event_name=event.EVENT_NAME,
                    
                )
                
            return UseCaseOutputDTO.fail(
                use_case=self.__class__.__name__,
                action="create",
                resource="calendar",
                resource_id=str(command.ano),
                triggered_by_id=command.triggered_by_id,
                message="Calendar source data was not available",
            )
            
        except CreateUseCaseException:
            raise
        except Exception as e:
            await self._repositoryCalendar.delete(command.ano)
            raise CreateUseCaseException(
                code="CREATE_CALENDAR_ERROR",
                message="Error creating calendar",
                use_case=self.__class__.__name__,
                context={"command": str(command)},
                original=e,
            ) from e
      
   
       
    
