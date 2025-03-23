from fastapi import APIRouter, UploadFile, File, Request
from ..controller.contractController import (
    get_contracts_by_space_id,
    create_contract_space,
    upload_contracts,
    update_contract_space,
    update_contract_metadata,
    delete_contract
)
from ..models.Model import contractSpaceModel  # Fixed class name and added missing import

# Create contract router
contract_router = APIRouter()  # Fixed variable name

@contract_router.post("/contracts/create-space")
async def create_space(details: contractSpaceModel, request: Request):
    """
    Create a new contract space
    
    :param details: Contract space details
    :param request: FastAPI request object
    :return: Creation result
    """
    return await create_contract_space(details, request)

@contract_router.post("/contracts/add_contracts/{contract_space_id}")
async def add_contracts(contract_space_id: str, file: UploadFile = File(...)):
    """
    Upload and process a contract file
    
    :param file: Uploaded contract PDF
    :return: Processing result
    """
    return await upload_contracts(contract_space_id, file)

@contract_router.get("/contracts/{space_id}")
async def get_contracts(space_id: str):
    """
    Get contracts under a particular space
    
    :param space_id: Contract space ID
    :return: List of contracts
    """
    return await get_contracts_by_space_id(space_id)

@contract_router.put("/contracts/update/{space_id}")
async def update_space(space_id: str, details: dict):
    """
    Update a contract space
    
    :param space_id: Contract space ID
    :param details: Updated details
    :return: Update result
    """
    return await update_contract_space(space_id, details)

@contract_router.put("/contracts/override/{contract_id}")
async def override_contract(contract_id: str, metadata: dict):
    """
    Override a contract's metadata
    
    :param contract_id: Contract ID
    :param metadata: Updated metadata
    :return: Update result
    """
    return await update_contract_metadata(contract_id, metadata)

@contract_router.delete("/contracts/{contract_id}")
async def remove_contract(contract_id: str):
    """
    Delete a contract
    
    :param contract_id: Contract ID
    :return: Delete result
    """
    return await delete_contract(contract_id)