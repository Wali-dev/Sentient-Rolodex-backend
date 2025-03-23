from passlib.context import CryptContext
from fastapi import HTTPException, Response
import os
from dotenv import load_dotenv
import jwt
import datetime
from ..config.database import users_collection
from ..models.Model import UserModel, LoginModel

# Load environment variables
load_dotenv()

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("JWT_KEY")  # Fixed variable name to match middleware
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*7  # 7 days

def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    """
    Creates a JWT token with expiration time
    
    :param data: Data to encode in the token
    :param expires_delta: Minutes until token expiration
    :return: Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def read_root():
    """Simple route to verify API is running"""
    return {"message": "Auth API is running"}

async def user_registration(user: UserModel):
    """
    Registers a new user
    
    :param user: User data including email and password
    :return: Success message and user ID
    """
    try:
        # Check if user already exists
        existing_user = users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")

        # Hash password before storing
        hashed_password = pwd_context.hash(user.password)
        
        # Convert Pydantic model to dict and update password
        user_data = {**user.dict(), "password": hashed_password}
        
        # Insert user into MongoDB
        new_user = users_collection.insert_one(user_data)
        
        return {"message": "User registered successfully", "user_id": str(new_user.inserted_id)}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle other exceptions
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

async def user_signin(response: Response, user: LoginModel):
    """
    Authenticates a user and sets JWT cookie
    
    :param response: FastAPI response object for setting cookies
    :param user: Login credentials (email and password)
    :return: Success message
    """
    try:
        # Find user by email
        existing_user = users_collection.find_one({"email": user.email})
        if not existing_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        verify_password = pwd_context.verify(user.password, existing_user["password"])
        if not verify_password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        # Create JWT token
        access_token = create_access_token({"sub": user.email})

        print(access_token)
        # Store token in HTTP-only cookie
        response.set_cookie(key="access_token", value=access_token, httponly=True)

        return {"message": "Login successful",
                "token":access_token}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle other exceptions
        print (e)
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

async def user_signout(response: Response):
    """
    Logs out a user by clearing the JWT cookie
    
    :param response: FastAPI response object
    :return: Success message
    """
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}