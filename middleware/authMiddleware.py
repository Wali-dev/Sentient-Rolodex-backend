from fastapi import Request, HTTPException, Depends
import jwt
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv("JWT_KEY")  # Change this in production
ALGORITHM = os.getenv("JWT_ALGORITHM")

# MongoDB Setup
MONGO_URI = os.getenv("DATABASE_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["hackathon"]
users_collection = db["users"]

# Function to verify JWT token
async def verify_access_token(request: Request):
    token = request.cookies.get("access_token")  # Get JWT from cookies
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Check if user exists in the database
        user = await users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user  # Return user data if token is valid
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")
