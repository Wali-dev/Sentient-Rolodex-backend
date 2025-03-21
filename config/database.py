from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
# MongoDB Connection URL (Change it as per your setup)
MONGO_URI = os.getenv("DATABASE_URI")  # Default local MongoDB URL

# Create a connection
client = MongoClient(MONGO_URI)

# Select Database
db = client["hackathon"]  # Replace 'my_database' with your actual DB name

# Select Collection
users_collection = db["users"]
contract_spaces=db["contractSpace"]
contracts=db["contracts"]
