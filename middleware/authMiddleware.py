from fastapi import Request, HTTPException
import jwt
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


# Load environment variables
load_dotenv()

# JWT configuration
SECRET_KEY = os.getenv("JWT_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")



# MongoDB Setup
MONGO_URI = os.getenv("DATABASE_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["hackathon"]
users_collection = db["users"]

async def verify_access_token(request: Request):
    """
    Verifies JWT token from cookies and returns user data
    
    :param request: FastAPI request object
    :return: User data if authenticated
    :raises: HTTPException if not authenticated
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Decode JWT token
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")