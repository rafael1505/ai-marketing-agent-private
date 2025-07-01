from typing import Any, Dict, List, Optional, Type, TypeVar, TYPE_CHECKING
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorCollection

ModelType = TypeVar("ModelType")

class BaseDB:
    collection: Any  # Using Any to avoid type issues

    def __init__(self, collection: Any):  # Using Any to avoid type issues
        self.collection = collection

    async def get(self, id: str) -> Optional[Dict[str, Any]]:
        # Print debug info
        print(f"BaseDB.get: Looking for document with ID: {id}")
        
        # Try to use ObjectId if it's a valid ObjectId format
        if ObjectId.is_valid(id):
            result = await self.collection.find_one({"_id": ObjectId(id)})
            if result is not None:
                return result
        
        # Try a string ID (for MockDB)
        result = await self.collection.find_one({"_id": id})
        if result is not None:
            return result
            
        # Try with an int ID (for MockDB when IDs are numbers stored as strings)
        try:
            numeric_id = int(id)
            return await self.collection.find_one({"_id": numeric_id})
        except (ValueError, TypeError):
            pass
            
        # If we still haven't found it, return None
        print(f"BaseDB.get: No document found with ID: {id}")
        return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        # Get cursor and apply pagination
        cursor = self.collection.find()
        
        # Check if it's a real MongoDB cursor (with skip method) or our mock cursor
        if hasattr(cursor, 'skip'):
            cursor = cursor.skip(skip).limit(limit)
            if hasattr(cursor, 'to_list'):
                return await cursor.to_list(length=limit)
            else:
                # Handle case where cursor is already a list (SimpleMockDatabase)
                return cursor
        else:
            # Handle case where cursor might be a list or other iterable
            # This handles our MockCursor implementation
            if hasattr(cursor, 'skip'):
                cursor = cursor.skip(skip).limit(limit)
                if hasattr(cursor, 'to_list'):
                    return await cursor.to_list(length=limit)
                else:
                    return cursor
            else:
                # For other types, just return what we have (already a list or other iterable)
                return cursor

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = data["created_at"]
        result = await self.collection.insert_one(data)
        
        # Debug info
        print(f"BaseDB.create: inserted_id = {result.inserted_id}")
        
        # Try to get the created document using the inserted_id
        created_doc = await self.get(str(result.inserted_id))
        
        # If we couldn't retrieve the document, create a minimal response with the ID
        if created_doc is None:
            # For testing, return at least a document with the ID
            print(f"BaseDB.create: Warning - Could not retrieve inserted document with ID {result.inserted_id}")
            created_doc = {
                "_id": str(result.inserted_id),
                "id": str(result.inserted_id),
                **data
            }
            
        return created_doc

    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["updated_at"] = datetime.utcnow()
        
        # Try to use ObjectId if it's a valid ObjectId format
        if ObjectId.is_valid(id):
            await self.collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": data}
            )
        else:
            # For non-ObjectId IDs (like simple string/int IDs in mock database)
            await self.collection.update_one(
                {"_id": id},
                {"$set": data}
            )
        
        return await self.get(id)

    async def delete(self, id: str) -> bool:
        # Try to use ObjectId if it's a valid ObjectId format
        if ObjectId.is_valid(id):
            result = await self.collection.delete_one({"_id": ObjectId(id)})
        else:
            # For non-ObjectId IDs (like simple string/int IDs in mock database)
            result = await self.collection.delete_one({"_id": id})
        
        return result.deleted_count > 0
