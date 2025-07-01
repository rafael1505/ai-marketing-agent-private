from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from app.main import app

def get_db():
    """
    Dependency that provides the MongoDB client.
    """
    return app.mongodb_client
