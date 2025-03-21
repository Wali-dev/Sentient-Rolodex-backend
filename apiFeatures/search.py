from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("DATABASE_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["hackathon"]
contract_spaces_collection = db["contract_spaces"]

async def search_contract_spaces(keyword: str):
    """
    Searches for contract spaces where the keyword matches either the name or contracts.
    
    :param keyword: The search term to match contract space names or contracts.
    :return: List of matching contract spaces.
    """
    search_results = await contract_spaces_collection.find(
        {
            "$or": [
                {"name": {"$regex": keyword, "$options": "i"}},  # Case-insensitive search in name
                {"contracts": {"$regex": keyword, "$options": "i"}}  # Case-insensitive search in contracts list
            ]
        }
    ).to_list(length=10)  # Limit results

    return search_results
