from fastapi import APIRouter, Response, Request
from ..controller.authController import read_root, user_registration, user_signin, user_signout,get_user_details
from ..models.Model import UserModel, LoginModel

from ..middleware.authMiddleware import verify_access_token
from bson import ObjectId

# Create auth router
auth = APIRouter()

@auth.get("/")
async def auth_root():
    """Root endpoint for auth API"""
    return await read_root()

@auth.get("/get-user")
async def get_user_data(request: Request):
    """
    Get authenticated user details including all contract spaces and their contracts
    
    :param request: FastAPI request object with access token
    :return: Aggregated user data with contract spaces and contracts
    """
    return await get_user_details(request)
    

@auth.post("/registration")
async def register_user(user: UserModel):
    """
    Register a new user
    
    :param user: User registration data
    :return: Registration result
    """
    return await user_registration(user)

@auth.post("/sign-in")
async def signin_user(response: Response, user: LoginModel):
    """
    Sign in a user
    
    :param response: FastAPI response object
    :param user: User login credentials
    :return: Login result
    """
    return await user_signin(response, user)

@auth.post("/sign-out")
async def signout_user(response: Response):
    """
    Sign out a user
    
    :param response: FastAPI response object
    :return: Logout result
    """
    return await user_signout(response)