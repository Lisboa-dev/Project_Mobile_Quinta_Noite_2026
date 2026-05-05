from fastapi import FastAPI
from pydantic import BaseModel
from services.usersService.src.API.Controllers.MedicController import routerUsers


app = FastAPI()

#middleware global aki
'''
@app.middleware("http")
async def add_process_time_header(request, call_next):
    
   
    print("ANTES DA ROTA")

    response = await call_next(request)

    print("DEPOIS DA ROTA")

    return response
'''


app.include_router(routerUsers)



def main():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3004)