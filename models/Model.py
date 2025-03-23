from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class UserModel(BaseModel):
    """User registration model"""
    email: EmailStr
    password: str
    contractSpace: List[str] = []

class LoginModel(BaseModel):
    """User login model"""
    email: EmailStr
    password: str

class contractSpaceModel(BaseModel):
    """Contract space model"""
    name: str
    contracts: List[str] = []

class ContractMetadataModel(BaseModel):
    """Contract metadata model"""
    id: str
    title: Optional[str] = None
    parties: Optional[List[str]] = None
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    terms: Optional[List[dict]] = None
    status: Optional[str] = None
    plartform: str
    
class AgentStatusModel(BaseModel):
    """Agent status model"""
    id: str
    status: str
    progress: float = 0.0
    messages: List[str] = []