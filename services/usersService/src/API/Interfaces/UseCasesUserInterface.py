from typing import Protocol, TypeVar


CommandT = TypeVar("CommandT")
QueryT = TypeVar("QueryT")
OutputT = TypeVar("OutputT")


class IUseCasesCreateUser(Protocol[CommandT, OutputT]):
    async def execute(self, data: CommandT) -> OutputT: ...


class IUseCasesListUser(Protocol[QueryT, OutputT]):
    async def execute(self, query: QueryT | None = None) -> list[OutputT]: ...


class IUseCasesDeleteUser(Protocol[CommandT, OutputT]):
    async def execute(self, command: CommandT) -> OutputT: ...


class IUseCasesUpdateUser(Protocol[CommandT, OutputT]):
    async def execute(self, data: CommandT) -> OutputT: ...


class IUseCasesDetailUser(Protocol[QueryT, OutputT]):
    async def execute(self, query: QueryT) -> OutputT: ...
