from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.authRoute import auth
from .routes.contractRoute import contract_router  # Fixed variable name

# Initialize FastAPI app
app = FastAPI(title="SentientRolodex API", 
              description="API for contract management and analysis",
              version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(contract_router, prefix="/api/v1", tags=["Contracts"])

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to SentientRolodex API", "status": "running"}

# User endpoints
@app.get("/api/v1/user/{user_id}")
async def get_user(user_id: str):
    """
    Gets user details including their contract spaces
    
    :param user_id: User ID
    :return: User data
    """
    # TODO: Implement user retrieval logic
    return {"message": "User retrieval endpoint", "user_id": user_id}

# Agent endpoints
@app.get("/api/v1/agents/{contact_id}")
async def initiate_agent(contact_id: str):
    """
    Initiates an agent to process a contract
    
    :param contact_id: Contract ID
    :return: Agent status
    """
    # TODO: Implement agent initiation logic
    return {"message": "Agent initiated", "contact_id": contact_id}

@app.get("/api/v1/agents/status/{agent_id}")
async def get_agent_status(agent_id: str):
    """
    Gets the status of a running agent
    
    :param agent_id: Agent ID
    :return: Agent status
    """
    # TODO: Implement agent status retrieval logic
    return {"message": "Agent status retrieval endpoint", "agent_id": agent_id}