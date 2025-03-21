from passlib.context import CryptContext
from fastapi import HTTPException,Response
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import jwt
import datetime
from ..config.database import users_collection
from ..models.Model import UserModel,LoginModel
load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_TOKEN")  # Change this in production
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*7

def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES): #store the time in env file
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # store the jwt token and algo in env

async def read_root():
    return ("This is the homee")


async def user_registration(user: UserModel):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password=pwd_context.hash(user.password)  # Hash the password before storing
    user_data = {**user.dict(), "password": hashed_password}
    
    # Insert user into MongoDB
    new_user =  users_collection.insert_one(user_data)
    
    return {"message": "User registered successfully", "user_id": str(new_user.inserted_id)}

async def user_signin(response: Response, user: LoginModel):
    existing_user = users_collection.find_one({"email": user.email})
    verify_password =pwd_context.verify(user.password, existing_user["password"])
    if not existing_user or not verify_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email})

    # Store token in HTTP-only cookie
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return {"message": "Login successful"}

async def user_signout(response: Response):
        response.delete_cookie("access_token")
        return {"message": "Logged out successfully"}
