import sys

from . import agenda as _agenda
from .agenda import aplication as _aplication
from .agenda import domain as _domain
from .agenda.aplication import dtos as _dtos
from .agenda.aplication import events as _events
from .agenda.aplication import ports as _ports
from .agenda.aplication import useCases as _use_cases
from .agenda.domain import entities as _entities
from .agenda.domain import exceptions as _exceptions
from .agenda.domain import rules as _rules
from .agenda.domain import services as _services
from .agenda.domain import valueObjects as _value_objects

sys.modules[f"{__name__}.Agenda"] = _agenda
sys.modules[f"{__name__}.Agenda.Aplication"] = _aplication
sys.modules[f"{__name__}.Agenda.Aplication.DTOs"] = _dtos
sys.modules[f"{__name__}.Agenda.Aplication.Events"] = _events
sys.modules[f"{__name__}.Agenda.Aplication.Ports"] = _ports
sys.modules[f"{__name__}.Agenda.Aplication.UseCases"] = _use_cases
sys.modules[f"{__name__}.Agenda.Domain"] = _domain
sys.modules[f"{__name__}.Agenda.Domain.Entities"] = _entities
sys.modules[f"{__name__}.Agenda.Domain.Exceptions"] = _exceptions
sys.modules[f"{__name__}.Agenda.Domain.Rules"] = _rules
sys.modules[f"{__name__}.Agenda.Domain.Services"] = _services
sys.modules[f"{__name__}.Agenda.Domain.ValueObjects"] = _value_objects
