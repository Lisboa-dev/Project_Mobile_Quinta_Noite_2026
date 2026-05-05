from fastapi import FastAPI
from pydantic import BaseModel
from services.notificacaoService.src.API.Controllers import AgendaController
from services.notificacaoService.src.API.provider import  router_factory
from services.notificacaoService.src.API.Controllers import AgendaController

app = FastAPI()

app.include_router(router_factory())

def main():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)