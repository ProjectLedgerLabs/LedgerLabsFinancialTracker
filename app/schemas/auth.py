from sqlmodel import SQLModel
from app.models.user import *
from pydantic import EmailStr

class SigninRequest(SQLModel):
    username: str
    password: str

class SignupRequest(SQLModel):
    username: str
    email: str
    password: str