from typing import Union

from fastapi import APIRouter,Response
from ..controller.authController import read_root,user_registration,user_signin
from ..models.Model import UserModel,LoginModel

auth=APIRouter()


@auth.get("/")
async def func1():
    return await read_root()

@auth.post("/registration")
async def func2(user: UserModel):
    return await user_registration(user)

@auth.post("/sign-in")
async def func3(response: Response, user: LoginModel):
    return  await user_signin(response,user)

