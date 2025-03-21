from fastapi import File, UploadFile ,HTTPException,Request
from pathlib import Path
from tempfile import NamedTemporaryFile
import pdfplumber
import os
from dotenv import load_dotenv
import google.generativeai as genai
from ..config.database import contract_spaces,users_collection,contracts
from ..models.Model import contractSpaceModel
from ..middleware.authMiddleware import verify_access_token
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip() if text else "No text found in PDF."

# Function to process extracted text using Gemini API
def process_with_gemini(text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(text)
    return response.text

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists



async def upload_contacts(file: UploadFile = File(...)):
    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())  # Write file content
            temp_path = temp_file.name  # Get the temporary file path
            extracted_text = extract_text_from_pdf(temp_path)
            gemini_response = process_with_gemini(f"give the detail exactly in json format {extracted_text}")
            # contract_data = gemini_response.dict() 
            # new_contract = await contracts.insert_one(contract_data)
        return {"Gemini API Response:\n": gemini_response}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

async def create_contact_space(details: contractSpaceModel, request: Request):
    user = await verify_access_token(request) 
    if not user:
        raise HTTPException(status_code=401, detail="Not Authenticated")
    
    contractSpace_data = details.dict()
    new_space = await contract_spaces.insert_one(contractSpace_data)  # Await MongoDB operation
    new_space_id = str(new_space.inserted_id)  # Get inserted contract space ID
    
    # Update user document to include contract space ID
    await users_collection.update_one(
        {"_id": user["_id"]}, 
        {"$push": {"contractspace": new_space_id}}
    )

    return {"message": "Contract space created successfully", "contract_space_id": new_space_id}

async def get_contact_parsed_metadata_under_a_particular_space():
    #Uploading contacts and feeding that contact to the gemini api logics goes here
    #parsed contact details will be saved in the database and that saving logic will also goes here probably
    return({"message:": "This is the contact uploading post route"})

async def update_contact():
        #If we want to update the contacts spaces data, then the logic goes here.
        return({"message:": "This is the update contact space data put route"})

async def update_contact():
        #If we want to explicitly override the contacts metadata, then the logic goes here. Like for if our gemini misses of or fails to obtain certain attributes of the contacts then we will be able to manually update it,
        #that logics goes here
        return({"message:": "This is the update individual contact metadata put route"})

async def update_contact():
        #If we want to delete contacts, that logic goes here
        return({"message:": "This is the delete individual contact delete route"})