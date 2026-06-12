from pydantic import BaseModel

class LoginBody(BaseModel):
    name: str
    email: str
    password: str