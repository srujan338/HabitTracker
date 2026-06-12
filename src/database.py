import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "studytracker"

_client = None

def get_db():
    global _client
    if _client is None:
        if not MONGO_URI:
            # Fallback for local development if URI is missing
            _client = MongoClient("mongodb://localhost:27017/")
        else:
            # Reverting to secure connection as TLS=False did not resolve the network block
            _client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    return _client[DB_NAME]

def get_collection(name):
    return get_db()[name]
