"""MongoDB connection helper."""
import os
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()

_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_client() -> MongoClient:
    """Get or create MongoDB client."""
    global _client
    if _client is None:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        _client = MongoClient(uri)
    return _client


def get_db() -> Database:
    """Get or create database instance."""
    global _db
    if _db is None:
        db_name = os.getenv("MONGODB_DB_NAME", "quietlystated")
        _db = get_client()[db_name]
    return _db


def close_connection() -> None:
    """Close MongoDB connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None

