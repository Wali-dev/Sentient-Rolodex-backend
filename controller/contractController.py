from fastapi import File, UploadFile, HTTPException, Request
from pathlib import Path
from tempfile import NamedTemporaryFile
import pdfplumber
import os
from dotenv import load_dotenv
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

async def upload_contracts(file: UploadFile = File(...)):
    """
    Uploads a contract PDF file and processes it with Gemini
    
    :param file: Uploaded PDF file
    :return: Processed contract data
    """
    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())  # Write file content
            temp_path = temp_file.name  # Get the temporary file path
            
            # Extract text from PDF
            extracted_text = extract_text_from_pdf(temp_path)
            
            # Process text with Gemini API
            gemini_response = process_with_gemini(extracted_text)
            
            # TODO: Parse response and store in database
            # contract_data = json.loads(gemini_response)
            # new_contract = await contracts_collection.insert_one(contract_data)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return {"gemini_response": gemini_response}
    except Exception as e:
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
        new_space = await contract_spaces_collection.insert_one(contract_space_data)  # Fixed variable name
        new_space_id = str(new_space.inserted_id)
        
        # Update user document to include contract space ID
        await users_collection.update_one(
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
        # Find the contract space
        space = await contract_spaces_collection.find_one({"_id": space_id})
        if not space:
            raise HTTPException(status_code=404, detail="Contract space not found")
            
        # Get contracts for this space
        contract_ids = space.get("contracts", [])
        contracts = []
        
        for contract_id in contract_ids:
            contract = await contracts_collection.find_one({"_id": contract_id})
            if contract:
                contracts.append(contract)
                
        return {"message": "Contracts retrieved successfully", "contracts": contracts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def update_contract_space(space_id: str, details: dict):
    """
    Updates a contract space's details
    
    :param space_id: Contract space ID
    :param details: Updated details
    :return: Success message
    """
    try:
        result = await contract_spaces_collection.update_one(
            {"_id": space_id},
            {"$set": details}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contract space not found")
            
        return {"message": "Contract space updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def update_contract_metadata(contract_id: str, metadata: dict):
    """
    Updates a contract's metadata
    
    :param contract_id: Contract ID
    :param metadata: Updated metadata
    :return: Success message
    """
    try:
        result = await contracts_collection.update_one(
            {"_id": contract_id},
            {"$set": metadata}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contract not found")
            
        return {"message": "Contract metadata updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_contract(contract_id: str):
    """
    Deletes a contract
    
    :param contract_id: Contract ID
    :return: Success message
    """
    try:
        result = await contracts_collection.delete_one({"_id": contract_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Contract not found")
            
        return {"message": "Contract deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))