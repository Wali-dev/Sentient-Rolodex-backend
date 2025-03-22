from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Connection URL from environment variables
MONGO_URI = os.getenv("DATABASE_URI")

try:
    # Create a connection
    client = MongoClient(MONGO_URI)
    
    # Select Database
    db = client["hackathon"]
    
    # Select Collections
    users_collection = db["users"]
    contract_spaces_collection = db["contract_spaces"]  # Fixed variable name
    contracts_collection = db["contracts"]  # Fixed variable name
except Exception as e:
    print(f"Database connection error: {str(e)}")
    # Re-raise to ensure app doesn't start with broken DB connection
    raise