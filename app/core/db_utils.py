from typing import Any
import inspect
from app.core.config import settings

def get_db_collection(mongodb: Any, collection_name: str) -> Any:
    """
    Helper function to get a collection from either MongoDB or SimpleMockDatabase.
    Handles: (1) app passes database (request.app.mongodb = mongodb.db), (2) client, (3) SimpleMockDatabase.

    Args:
        mongodb: The database instance (Motor database, Motor client, or SimpleMockDatabase)
        collection_name: Name of the collection to access

    Returns:
        The collection object
    """
    # When app passes the database (e.g. request.app.mongodb = mongodb.db), use direct collection access
    try:
        collection = getattr(mongodb, collection_name, None)
        if collection is not None and not inspect.iscoroutine(collection):
            return collection
    except (TypeError, AttributeError):
        pass
    try:
        return mongodb[collection_name]
    except (TypeError, KeyError, AttributeError):
        pass
    # Client pattern: client[db_name][collection_name]
    try:
        return mongodb[settings.MONGODB_DB][collection_name]
    except (TypeError, KeyError, AttributeError):
        pass
    raise ValueError(
        f"Could not access collection '{collection_name}'. "
        "Tried database attribute, database[collection], and client[db][collection]."
    )
