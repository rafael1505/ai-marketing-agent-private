from typing import Any
import inspect
from app.core.config import settings

def get_db_collection(mongodb: Any, collection_name: str) -> Any:
    """
    Helper function to get a collection from either MongoDB or SimpleMockDatabase.
    This handles the difference in access patterns between the two database types.
    
    Args:
        mongodb: The database instance (could be either MongoDB client or SimpleMockDatabase)
        collection_name: Name of the collection to access
        
    Returns:
        The collection object
    """
    try:
        # First try the standard MongoDB access pattern
        return mongodb[settings.MONGODB_DB][collection_name]
    except (TypeError, KeyError, AttributeError):
        # If that fails, try SimpleMockDatabase direct property access
        # We assume the collection is available as a property on the db object
        try:
            collection = getattr(mongodb, collection_name)
            # Check if it's a coroutine function/object and not already awaited
            if inspect.iscoroutine(collection):
                raise ValueError(
                    f"Collection '{collection_name}' is a coroutine and must be awaited. "
                    "Use 'await get_db_collection(...)' instead."
                )
            return collection
        except (AttributeError):
            # If that also fails, raise a descriptive error
            raise ValueError(
                f"Could not access collection '{collection_name}'. "
                "Neither MongoDB nor SimpleMockDatabase patterns worked."
            )
