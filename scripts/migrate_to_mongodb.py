"""
Migration Script: JSON Data → MongoDB
Transfers all data from app/db/data/*.json to real MongoDB collections
"""
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_json_to_mongodb():
    """Migrate all JSON data files to MongoDB"""
    
    # Connect to MongoDB
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    
    try:
        # Test connection
        await client.admin.command('ping')
        logger.info(f"✅ Connected to MongoDB database: {settings.MONGODB_DB}")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        return
    
    data_dir = Path("app/db/data")
    
    # Collections to migrate
    collections = {
        "users": "users.json",
        "companies": "companies.json",
        "materials": "materials.json",
        "ai_providers": "ai_providers.json"
    }
    
    for collection_name, filename in collections.items():
        file_path = data_dir / filename
        
        if not file_path.exists():
            logger.warning(f"⚠️  File not found: {file_path}, skipping {collection_name}")
            continue
        
        logger.info(f"\n📦 Migrating {collection_name} from {filename}...")
        
        try:
            # Load JSON data
            with open(file_path, 'r') as f:
                json_data = json.load(f)
            
            if not json_data:
                logger.info(f"   Empty file, skipping {collection_name}")
                continue
            
            # Clear existing collection
            result = await db[collection_name].delete_many({})
            logger.info(f"   Cleared {result.deleted_count} existing documents")
            
            # Prepare documents for insertion
            documents = []
            
            # Handle different JSON structures
            if isinstance(json_data, dict):
                # JSON is a dictionary with IDs as keys
                for doc_id, doc_data in json_data.items():
                    doc = doc_data.copy() if isinstance(doc_data, dict) else {"_id": doc_id, "data": doc_data}
                    
                    # Ensure _id field exists
                    if "_id" not in doc:
                        doc["_id"] = doc_id
                    
                    # Convert datetime strings to datetime objects
                    for field in ["created_at", "updated_at"]:
                        if field in doc and isinstance(doc[field], str):
                            try:
                                doc[field] = datetime.fromisoformat(doc[field])
                            except:
                                pass
                    
                    documents.append(doc)
                    
            elif isinstance(json_data, list):
                # JSON is already a list of documents
                documents = json_data
            
            # Insert documents
            if documents:
                result = await db[collection_name].insert_many(documents, ordered=False)
                logger.info(f"   ✅ Migrated {len(result.inserted_ids)} documents to {collection_name}")
                
                # Show sample document
                sample = documents[0]
                logger.info(f"   Sample document: {list(sample.keys())[:5]}...")
            else:
                logger.warning(f"   No documents to migrate for {collection_name}")
                
        except Exception as e:
            logger.error(f"   ❌ Error migrating {collection_name}: {e}")
            continue
    
    # Create indexes
    logger.info("\n🔧 Creating indexes...")
    try:
        await db.users.create_index("email", unique=True)
        await db.users.create_index("company_id")
        await db.companies.create_index("active")
        await db.materials.create_index("company_id")
        await db.ai_providers.create_index("user_id")
        await db.ai_providers.create_index([("user_id", 1), ("id", 1)], unique=True)
        logger.info("✅ Indexes created successfully")
    except Exception as e:
        logger.warning(f"⚠️  Error creating indexes (may already exist): {e}")
    
    # Verify migration
    logger.info("\n📊 Migration Summary:")
    for collection_name in collections.keys():
        count = await db[collection_name].count_documents({})
        logger.info(f"   {collection_name}: {count} documents")
    
    # Close connection
    client.close()
    logger.info("\n✅ Migration complete!")


if __name__ == "__main__":
    asyncio.run(migrate_json_to_mongodb())
