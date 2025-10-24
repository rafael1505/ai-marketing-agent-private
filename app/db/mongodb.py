"""
MongoDB Database Connection and Management
Provides async connection to MongoDB using motor driver
"""
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.core.config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager with connection pooling"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        
    async def connect(self):
        """
        Connect to MongoDB database
        Raises ConnectionFailure if connection fails
        """
        try:
            logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
            
            # Create MongoDB client with connection pooling
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=10,
                minPoolSize=1,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
            )
            
            # Get database
            self.db = self.client[settings.MONGODB_DB]
            
            # Test connection
            await self.client.admin.command('ping')
            
            logger.info(f"✅ Successfully connected to MongoDB database: {settings.MONGODB_DB}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise ConnectionFailure(f"Could not connect to MongoDB at {settings.MONGODB_URL}")
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
            raise
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    async def create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            logger.info("Creating MongoDB indexes...")
            
            # Users collection indexes
            await self.db.users.create_index("email", unique=True)
            await self.db.users.create_index("company_id")
            
            # Companies collection indexes
            await self.db.companies.create_index("active")
            
            # Materials collection indexes
            await self.db.materials.create_index("company_id")
            await self.db.materials.create_index("status")
            await self.db.materials.create_index([("company_id", 1), ("status", 1)])
            
            # AI Providers collection indexes
            await self.db.ai_providers.create_index("user_id")
            await self.db.ai_providers.create_index("id")
            await self.db.ai_providers.create_index([("user_id", 1), ("id", 1)], unique=True)
            await self.db.ai_providers.create_index("isActive")
            
            logger.info("✅ MongoDB indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            # Don't raise - indexes are performance optimization, not critical for functionality
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get MongoDB database instance"""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return self.db
    
    # Collection accessors for convenience
    @property
    def users(self):
        """Get users collection"""
        return self.db.users
    
    @property
    def companies(self):
        """Get companies collection"""
        return self.db.companies
    
    @property
    def materials(self):
        """Get materials collection"""
        return self.db.materials
    
    @property
    def ai_providers(self):
        """Get ai_providers collection"""
        return self.db.ai_providers


# Global MongoDB instance
mongodb = MongoDB()


async def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency function to get MongoDB database
    Use with FastAPI Depends()
    """
    return mongodb.get_database()
