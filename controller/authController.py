from passlib.context import CryptContext
from fastapi import HTTPException, Response
import os
from dotenv import load_dotenv
import jwt
import datetime
from ..config.database import users_collection
from ..models.Model import UserModel, LoginModel

from fastapi import Request
from ..middleware.authMiddleware import verify_access_token
from bson import ObjectId
from ..config.database import contract_spaces_collection, contracts_collection

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


async def get_user_details(request: Request):
    """
    Get authenticated user details including all contract spaces and their contracts
    
    :param request: FastAPI request object with access token
    :return: Aggregated user data with contract spaces and contracts
    """
    try:
        # Verify user authentication using access token
        user = await verify_access_token(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Create user info dict without sensitive data
        user_info = {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "contract_spaces": []
        }
        
        print(user_info)
        # Get all contract spaces for this user
        contract_space_ids = user.get("contractSpace", [])
        
        # Fetch each contract space and its contracts
        for space_id in contract_space_ids:
            try:
                # Convert string ID to ObjectId if needed
                space_obj_id = ObjectId(space_id) if not isinstance(space_id, ObjectId) else space_id
                
                # Find the contract space
                space =  contract_spaces_collection.find_one({"_id": space_obj_id})
                
                if space:
                    # Create contract space info without _id field
                    space_info = {
                        "space_id": str(space["_id"]),
                        "name": space["name"],
                        "contracts": []
                    }
                    
                    # Get all contracts for this space
                    contract_ids = space.get("contracts", [])
                    
                    # Fetch each contract
                    for contract_id in contract_ids:
                        try:
                            # Convert string ID to ObjectId if needed
                            contract_obj_id = ObjectId(contract_id) if not isinstance(contract_id, ObjectId) else contract_id
                            
                            # Find the contract
                            contract =  contracts_collection.find_one({"_id": contract_obj_id})
                            
                            if contract:
                                # Create contract info
                                contract_info = {
                                    "contract_id": str(contract["_id"]),
                                    "title": contract.get("title", "Untitled"),
                                    "parties": contract.get("parties", []),
                                    "status": contract.get("status", "Unknown"),
                                    "platform": contract.get("plartform", "")  # Note the misspelling in the model
                                }
                                
                                space_info["contracts"].append(contract_info)
                        except Exception as contract_err:
                            print(f"Error fetching contract {contract_id}: {str(contract_err)}")
                    
                    user_info["contract_spaces"].append(space_info)
            except Exception as space_err:
                print(f"Error fetching contract space {space_id}: {str(space_err)}")
        
        return user_info
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle other exceptions
        raise HTTPException(status_code=500, detail=f"Error retrieving user data: {str(e)}")