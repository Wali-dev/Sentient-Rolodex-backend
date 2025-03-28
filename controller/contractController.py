from fastapi import File, UploadFile, HTTPException, Request
from pathlib import Path
from tempfile import NamedTemporaryFile
import pdfplumber
import shutil
import os
from dotenv import load_dotenv
from bson import ObjectId
import asyncio
import google.generativeai as genai
from ..config.database import contract_spaces_collection, users_collection, contracts_collection  # Fixed variable names
from ..models.Model import contractSpaceModel
from ..middleware.authMiddleware import verify_access_token

# Load environment variables
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# Set upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

def extract_text_from_pdf(pdf_path):
    """
    Extracts text content from a PDF file
    
    :param pdf_path: Path to the PDF file
    :return: Extracted text as a string
    """
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip() if text else "No text found in PDF."
    except Exception as e:
        print(f"PDF extraction error: {str(e)}")
        return f"Error extracting PDF: {str(e)}"

def process_with_gemini(text):
    """
    Processes text with Google's Gemini API
    
    :param text: Text to process
    :return: Gemini API response
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"Give the detail exactly in JSON format: {text}")
        return response.text
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        return f"Error processing with Gemini: {str(e)}"



async def upload_contracts(contract_space_id: str, file: UploadFile = File(...)):
    """
    Uploads a contract PDF file and processes it with Gemini
    
    :param contract_space_id: ID of the contract space to add the contract to
    :param file: Uploaded PDF file
    :return: Processed contract data
    """
    try:
        # Create a temporary file path
        temp_file_path = UPLOAD_DIR / f"temp_{file.filename}"
        
        # Save the upload file to the temporary location
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Make sure the file is closed before processing
        file.file.close()
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(temp_file_path)
        
        # Process text with Gemini API
        gemini_response = process_with_gemini(extracted_text)
        
        # Create dummy contract data
        dummy_contract = {
            "id": "contract_12345",
            "title": "Service Agreement",
            "parties": ["Company A", "Company B"],
            "effective_date": "2025-01-01",
            "expiration_date": "2026-01-01",
            "terms": [
                {
                    "clause": "Payment Terms",
                    "description": "Payment must be made within 30 days of invoice."
                },
                {
                    "clause": "Confidentiality",
                    "description": "Both parties agree to keep all shared information confidential."
                }
            ],
            "status": "Active",
            "plartform": "www.youtube.com"
        }
        
        # Convert to ContractMetadataModel instance and then to dict for DB storage
        from ..models.Model import ContractMetadataModel
        from bson import ObjectId
        
        contract_model = ContractMetadataModel(**dummy_contract)
        
        # Save to database
        contract_dict = contract_model.dict()
        new_contract = contracts_collection.insert_one(contract_dict)
        contract_id = str(new_contract.inserted_id)
        
        # Print for debugging
        print(f"Contract ID: {contract_id}")
        print(f"Contract Space ID: {contract_space_id}")
        
        # Convert string ID to ObjectId for MongoDB query
        try:
            space_id = ObjectId(contract_space_id)
        except:
            space_id = contract_space_id  # Keep as string if it's not a valid ObjectId
        
        # Update the contract space to include this contract
        update_result = contract_spaces_collection.update_one(
            {"_id": space_id},
            {"$push": {"contracts": contract_id}}
        )
        
        print(f"Update result: {update_result.modified_count} document(s) modified")
        
        # Clean up temp file after processing
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        return {
            "message": "Contract uploaded successfully",
            "contract_id": contract_id,
            "contract_space_id": contract_space_id,
            "update_result": {
                "acknowledged": update_result.acknowledged,
                "modified_count": update_result.modified_count
            }
        }
        
    except Exception as e:
        # Ensure file cleanup in case of error
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass  # Ignore errors during cleanup
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
async def create_contract_space(details: contractSpaceModel, request: Request):
    """
    Creates a new contract space
    
    :param details: Contract space details
    :param request: FastAPI request object for auth
    :return: Success message and contract space ID
    """
    try:
        # Verify user authentication
        user = await verify_access_token(request) 
        if not user:
            raise HTTPException(status_code=401, detail="Not Authenticated")
        
        # Create contract space
        contract_space_data = details.dict()
        new_space = contract_spaces_collection.insert_one(contract_space_data)# Fixed variable name
        new_space_id = str(new_space.inserted_id)
        
        # Update user document to include contract space ID
        users_collection.update_one(
    {"_id": user["_id"]}, 
    {"$push": {"contractSpace": new_space_id}}
)

        return {"message": "Contract space created successfully", "contract_space_id": new_space_id}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle other exceptions
        raise HTTPException(status_code=500, detail=f"Error creating contract space: {str(e)}")

async def get_contracts_by_space_id(space_id: str):
    """
    Gets contracts under a particular space
    
    :param space_id: Contract space ID
    :return: List of contracts
    """
    try:
        print(f"Looking for space with ID: {space_id}")
        
        # Convert string ID to ObjectId for MongoDB query
        try:
            # Try to convert to ObjectId if it's in the correct format
            space_obj_id = ObjectId(space_id)
        except:
            # If conversion fails, keep as string
            space_obj_id = space_id
            
        # Find the contract space
        space = contract_spaces_collection.find_one({"_id": space_obj_id})
        
        if not space:
            raise HTTPException(status_code=404, detail="Contract space not found")
            
        # Get contracts for this space
        contract_ids = space.get("contracts", [])
        contracts = []
        
        for contract_id in contract_ids:
            try:
                # Try to convert to ObjectId if it's in the correct format
                contract_obj_id = ObjectId(contract_id) if not isinstance(contract_id, ObjectId) else contract_id
                
                # Find the contract
                contract = contracts_collection.find_one({"_id": contract_obj_id})
                if contract:
                    # Convert ObjectId to string for JSON serialization
                    contract["_id"] = str(contract["_id"])
                    contracts.append(contract)
            except Exception as contract_err:
                print(f"Error fetching contract {contract_id}: {str(contract_err)}")
                
        return {"message": "Contracts retrieved successfully", "contracts": contracts}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Error in get_contracts_by_space_id: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

async def update_contract_space(space_id: str, details: dict):
    """
    Updates a contract space's details
    
    :param space_id: Contract space ID
    :param details: Updated details
    :return: Success message
    """
    try:
        # Convert string ID to ObjectId for MongoDB query
        from bson import ObjectId
        try:
            # Try to convert to ObjectId if it's in the correct format
            space_obj_id = ObjectId(space_id)
        except:
            # If conversion fails, keep as string
            space_obj_id = space_id
            
        print(f"Updating space with ID: {space_obj_id}")
        print(f"Update details: {details}")
        
        # Remove await since contract_spaces_collection.update_one is synchronous
        result = contract_spaces_collection.update_one(
            {"_id": space_obj_id},
            {"$set": details}
        )
        
        print(f"Update result: {result.matched_count} document(s) matched, {result.modified_count} document(s) modified")
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contract space not found")
            
        return {"message": "Contract space updated successfully"}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Error in update_contract_space: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    


async def update_contract_metadata(contract_id: str, metadata: dict):
    """
    Updates a contract's metadata
    
    :param contract_id: Contract ID
    :param metadata: Updated metadata
    :return: Success message
    """
    try:
        # Convert string ID to ObjectId for MongoDB query
        try:
            contract_obj_id = ObjectId(contract_id)
        except:
            contract_obj_id = contract_id
        
        print(f"Updating contract with ID: {contract_obj_id}")
        print(f"Update metadata: {metadata}")

        result = contracts_collection.update_one(
            {"_id": contract_obj_id},
            {"$set": metadata}
        )
        
        print(f"Update result: {result.matched_count} document(s) matched, {result.modified_count} document(s) modified")

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contract not found")
            
        return {"message": "Contract metadata updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_contract_metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def delete_contract(contract_id: str):
    """
    Deletes a contract
    
    :param contract_id: Contract ID
    :return: Success message
    """
    try:
       
        
        # Try to convert to ObjectId if it's a valid ID format
        try:
            obj_id = ObjectId(contract_id)
        except:
            # If conversion fails, use the string as is
            obj_id = contract_id
            
        # Use the converted ID in the query
        result = contracts_collection.delete_one({"_id": obj_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Contract not found")
            
        return {"message": "Contract deleted successfully"}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))