from pydantic import BaseModel, EmailStr
from typing import List

class UserModel(BaseModel):
    email: EmailStr
    password: str
    contractSpace: List[str] = []

class LoginModel(BaseModel):
    email: EmailStr
    password: str

class contractSpaceModel(BaseModel):
    name:str
    contracts:List[str]=[]


class contactMetadataModel(BaseModel):
    id: str
    