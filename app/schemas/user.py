from app.models.user import *
from sqlmodel import SQLModel
from pydantic import EmailStr
from pydantic import ConfigDict
from typing import Optional


class UserUpdate(SQLModel):
    username: Optional[str]
    email: Optional[EmailStr]
 
class AdminCreate(UserBase):
    role:str = "admin"

class RegularUserCreate(UserBase):
    role:str = "regular_user"

class UserResponse(SQLModel):
    user_id: int
    username:str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class SignupRequest(SQLModel):
    username: str
    email: EmailStr
    password: str
