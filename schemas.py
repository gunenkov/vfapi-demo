from pydantic import BaseModel


class User(BaseModel):
    name: str
    username: str
    address: str
    email: str
    password: str
    contact: str

class UserAuthSchema(BaseModel):
    username: str
    password: str