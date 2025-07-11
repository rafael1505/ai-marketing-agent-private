import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class MockCursor:
    """
    A simple class that mimics MongoDB cursor methods like skip() and limit()
    """
    def __init__(self, results: List[Dict[str, Any]]):
        self.results = results
        self.skip_count = 0
        self.limit_count = None
    
    def skip(self, count: int):
        """Skip the first n results"""
        self.skip_count = count
        return self
    
    def limit(self, count: int):
        """Limit the results to n items"""
        self.limit_count = count
        return self
    
    async def to_list(self, length: int = None) -> List[Dict[str, Any]]:
        """Convert results to a list with the applied skip and limit"""
        if length is not None and (self.limit_count is None or length < self.limit_count):
            self.limit_count = length
        
        results = self.results[self.skip_count:]
        
        if self.limit_count is not None:
            results = results[:self.limit_count]
            
        return results
    
    # Make the cursor also directly usable as a list
    def __iter__(self):
        """Allow the cursor to be used as an iterator"""
        start = self.skip_count
        end = len(self.results) if self.limit_count is None else min(self.skip_count + self.limit_count, len(self.results))
        for i in range(start, end):
            yield self.results[i]
    
    def __getitem__(self, index):
        """Allow the cursor to be indexed"""
        if isinstance(index, slice):
            start = index.start or 0
            if start < self.skip_count:
                start = self.skip_count
                
            stop = index.stop
            if self.limit_count is not None:
                if stop is None or stop > self.skip_count + self.limit_count:
                    stop = self.skip_count + self.limit_count
                    
            return self.results[start:stop:index.step]
        else:
            actual_index = index + self.skip_count
            if self.limit_count is not None and index >= self.limit_count:
                raise IndexError("List index out of range")
            return self.results[actual_index]
            
    # Allow using len() on the cursor
    def __len__(self):
        """Return the effective length after applying skip and limit"""
        if self.limit_count is not None:
            return min(len(self.results) - self.skip_count, self.limit_count)
        return max(0, len(self.results) - self.skip_count)
        
    # Add support for await on the cursor
    def __await__(self):
        """Support awaiting on the cursor directly"""
        # When awaited, return the filtered results as a list
        filtered_results = self.results[self.skip_count:]
        if self.limit_count is not None:
            filtered_results = filtered_results[:self.limit_count]
            
        # Create a coroutine that returns the filtered results
        async def get_results():
            return filtered_results
            
        return get_results().__await__()

class SimpleMockDatabase:
    def __init__(self):
        # Use simple dictionaries instead of SQLite
        self._data = {
            "users": {},
            "companies": {},
            "materials": {},
            "ai_providers": {}
        }
        self._next_id = 1
        
    @property
    def users(self):
        return SimpleMockCollection(self._data["users"], self)
    
    @property
    def companies(self):
        return SimpleMockCollection(self._data["companies"], self)
        
    @property
    def materials(self):
        return SimpleMockCollection(self._data["materials"], self)
        
    @property
    def ai_providers(self):
        return SimpleMockCollection(self._data["ai_providers"], self)

    def close(self):
        # No-op for simple mock
        pass

class SimpleMockCollection:
    def __init__(self, data_dict, db):
        self.data = data_dict
        self.db = db
    
    async def find_one(self, query=None):
        if query is None:
            query = {}
        
        # Print query for debugging
        print(f"MockDB find_one query: {query}")
        
        # Handle MongoDB ObjectId conversion if needed
        if "_id" in query and hasattr(query["_id"], "__str__"):
            query = query.copy()
            query["_id"] = str(query["_id"])
        
        # Special handling for test_company ID
        if "_id" in query and query["_id"] == "test_company":
            # If test_company doesn't exist in the database, create it
            if "test_company" not in self.data:
                # Create a default test company
                self.data["test_company"] = {
                    "name": "Test Company",
                    "description": "Auto-created test company",
                    "email": "contact@testcompany.com",
                    "phone": "+1 (555) 123-4567",
                    "address": "123 Test Street, Test City, TC 12345",
                    "brand_colors": ["#FF0000", "#00FF00", "#0000FF"],
                    "active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                print(f"Auto-created test_company in find_one query: {query}")
            
            # Return the test_company
            doc = self.data["test_company"].copy()
            doc["_id"] = "test_company"
            doc["id"] = "test_company"
            return doc
        
        # Check for active company query - always return test_company if it exists
        if query.get("active") is True and "test_company" in self.data:
            doc = self.data["test_company"].copy()
            doc["_id"] = "test_company"
            doc["id"] = "test_company"
            doc["active"] = True  # Ensure it's active
            return doc
        
        # Handle regular _id queries
        if "_id" in query:
            # First try exact match
            id_val = query["_id"]
            if id_val in self.data:
                doc = self.data[id_val].copy()
                doc["_id"] = id_val
                doc["id"] = str(id_val)  # Add id field for Pydantic models
                # Convert ISO strings back to datetime objects
                if "created_at" in doc and isinstance(doc["created_at"], str):
                    doc["created_at"] = datetime.fromisoformat(doc["created_at"])
                if "updated_at" in doc and isinstance(doc["updated_at"], str):
                    doc["updated_at"] = datetime.fromisoformat(doc["updated_at"])
                # Check other query fields
                for key, value in query.items():
                    if key != "_id" and doc.get(key) != value:
                        return None
                print(f"MockDB found document with exact match: {doc}")
                return doc
            
            # If not found by exact match, try string conversion
            str_id = str(id_val)
            if str_id in self.data:
                doc = self.data[str_id].copy()
                doc["_id"] = str_id
                doc["id"] = str_id
                # Convert ISO strings back to datetime objects
                if "created_at" in doc and isinstance(doc["created_at"], str):
                    doc["created_at"] = datetime.fromisoformat(doc["created_at"])
                if "updated_at" in doc and isinstance(doc["updated_at"], str):
                    doc["updated_at"] = datetime.fromisoformat(doc["updated_at"])
                # Check other query fields
                for key, value in query.items():
                    if key != "_id" and doc.get(key) != value:
                        return None
                print(f"MockDB found document with string ID: {doc}")
                return doc
                
            # If the ID is a string that represents an integer, try numeric lookup
            if isinstance(id_val, str) and id_val.isdigit():
                num_id = int(id_val)
                if num_id in self.data:
                    doc = self.data[num_id].copy()
                    doc["_id"] = num_id
                    doc["id"] = str(num_id)
                    # Convert ISO strings back to datetime objects
                    if "created_at" in doc and isinstance(doc["created_at"], str):
                        doc["created_at"] = datetime.fromisoformat(doc["created_at"])
                    if "updated_at" in doc and isinstance(doc["updated_at"], str):
                        doc["updated_at"] = datetime.fromisoformat(doc["updated_at"])
                    # Check other query fields
                    for key, value in query.items():
                        if key != "_id" and doc.get(key) != value:
                            return None
                    print(f"MockDB found document with numeric ID: {doc}")
                    return doc
                    
            # If ID is a number, try string version
            if isinstance(id_val, int) or (isinstance(id_val, str) and id_val.isdigit()):
                # Try lookup with ID as a string
                str_id = str(id_val)
                if str_id in self.data:
                    doc = self.data[str_id].copy()
                    doc["_id"] = str_id
                    doc["id"] = str_id
                    # Convert ISO strings back to datetime objects
                    if "created_at" in doc and isinstance(doc["created_at"], str):
                        doc["created_at"] = datetime.fromisoformat(doc["created_at"])
                    if "updated_at" in doc and isinstance(doc["updated_at"], str):
                        doc["updated_at"] = datetime.fromisoformat(doc["updated_at"])
                    # Check other query fields
                    for key, value in query.items():
                        if key != "_id" and doc.get(key) != value:
                            return None
                    print(f"MockDB found document with string version of numeric ID: {doc}")
                    return doc
            
            print(f"MockDB: No document found with _id: {id_val}")
            print(f"Available IDs: {list(self.data.keys())}")
            return None
        
        # Handle other queries
        for doc_id, doc in self.data.items():
            match = True
            for key, value in query.items():
                if doc.get(key) != value:
                    match = False
                    break
            if match:
                result = doc.copy()
                result["_id"] = doc_id
                result["id"] = str(doc_id)  # Add id field for Pydantic models
                # Convert ISO strings back to datetime objects
                if "created_at" in result and isinstance(result["created_at"], str):
                    result["created_at"] = datetime.fromisoformat(result["created_at"])
                if "updated_at" in result and isinstance(result["updated_at"], str):
                    result["updated_at"] = datetime.fromisoformat(result["updated_at"])
                return result
        return None
    
    def _find_internal(self, query=None):
        """
        Internal helper method to find documents matching the query.
        Returns a list of matching documents.
        """
        results = []
        if query is None:
            query = {}
        
        print(f"MockDB _find_internal query: {query}")
        print(f"Available docs: {len(self.data)} with keys: {list(self.data.keys())}")
        
        # Special handling for company_id query to be safer
        if "company_id" in query:
            print(f"Company ID query: {query['company_id']}")
        
        # Debugging: print all documents
        for doc_id, doc_data in self.data.items():
            print(f"Document ID: {doc_id}, contents: {doc_data}")
            if "company_id" in doc_data:
                print(f"  Has company_id: {doc_data['company_id']}")
        
        for doc_id, doc in self.data.items():
            match = True
            for key, value in query.items():
                # Special handling for case-insensitive string matching
                if isinstance(doc.get(key), str) and isinstance(value, str):
                    if doc.get(key).lower() != value.lower():
                        match = False
                        break
                # Special handling for exact object match (useful for Enum comparisons)
                elif doc.get(key) != value:
                    match = False
                    break
            
            if match:
                result = doc.copy()
                result["_id"] = doc_id
                result["id"] = str(doc_id)  # Add id field for Pydantic models
                # Convert ISO strings back to datetime objects
                if "created_at" in result and isinstance(result["created_at"], str):
                    try:
                        result["created_at"] = datetime.fromisoformat(result["created_at"])
                    except ValueError:
                        pass  # Keep as string if parsing fails
                if "updated_at" in result and isinstance(result["updated_at"], str):
                    try:
                        result["updated_at"] = datetime.fromisoformat(result["updated_at"])
                    except ValueError:
                        pass  # Keep as string if parsing fails
                results.append(result)
        
        print(f"Found {len(results)} matching documents")
        return results
    
    def find(self, query=None):
        """
        Synchronous find method that returns a MockCursor.
        The MongoDB driver returns a cursor object synchronously, but the actual data fetching happens asynchronously.
        """
        results = self._find_internal(query)
        # Return a MockCursor object that mimics MongoDB's cursor
        return MockCursor(results)
    
    async def find_async(self, query=None):
        """
        Async version of find that returns an awaitable MockCursor.
        This ensures both await collection.find() and collection.find().skip().limit() patterns work.
        """
        # Use the synchronous version to get the mock cursor but with a different name to avoid recursion
        results = self._find_internal(query)
        return MockCursor(results)
    
    async def insert_one(self, data):
        # Use the provided ID if it exists, otherwise generate one
        if "_id" in data:
            doc_id = data["_id"]
            data = data.copy()
        elif "id" in data:
            doc_id = data["id"]
            # Remove the id from data since we'll add _id
            data = data.copy()
            del data["id"]
        else:
            doc_id = self.db._next_id
            self.db._next_id += 1
        
        # Always store IDs as strings for consistency
        doc_id = str(doc_id)
        
        # Store a copy of the data without the _id field
        doc = data.copy()
        if "_id" in doc:
            del doc["_id"]  # Don't store _id in the document itself
            
        doc["created_at"] = datetime.utcnow().isoformat()
        doc["updated_at"] = datetime.utcnow().isoformat()
        
        # Print debug info
        print(f"MockDB insert_one: Adding document with ID {doc_id}")
        print(f"Document contents: {doc}")
        
        self.data[doc_id] = doc
        return SimpleMockInsertResult(doc_id)
    
    async def update_one(self, query, update_data):
        # Special handling for $or queries
        if "$or" in query:
            # Try each condition in the $or array
            matched = False
            for condition in query["$or"]:
                # If any condition matches a document, update it
                if "_id" in condition and condition["_id"] in self.data:
                    doc_id = condition["_id"]
                    matched = True
                    break
                # Special case for "active": True condition
                if condition.get("active") is True:
                    # Find any active company
                    for doc_id, doc in self.data.items():
                        if doc.get("active") is True:
                            matched = True
                            break
                    if matched:
                        break
                    
                    # If no active company found but test_company is special
                    if "test_company" in self.data:
                        doc_id = "test_company"
                        matched = True
                        break
            
            if not matched:
                return SimpleMockUpdateResult(0, 0)
                
        # Special handling for test_company ID
        elif "_id" in query and query["_id"] == "test_company":
            doc_id = "test_company"
            # If test_company doesn't exist, create it
            if doc_id not in self.data:
                self.data[doc_id] = {
                    "name": "Test Company",
                    "description": "Auto-created test company in update_one",
                    "email": "contact@testcompany.com",
                    "phone": "+1 (555) 123-4567",
                    "address": "123 Test Street, Test City, TC 12345",
                    "brand_colors": ["#FF0000", "#00FF00", "#0000FF"],
                    "active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                print(f"Auto-created test_company in update_one query: {query}")
        # Regular _id query
        elif "_id" in query:
            doc_id = query["_id"]
            if doc_id not in self.data:
                return SimpleMockUpdateResult(0, 0)
        # Active company query
        elif query.get("active") is True:
            # Try to find an active company
            active_found = False
            for potential_id, doc in self.data.items():
                if doc.get("active") is True:
                    doc_id = potential_id
                    active_found = True
                    break
            
            # If no active company found but test_company exists
            if not active_found:
                if "test_company" in self.data:
                    doc_id = "test_company"
                else:
                    return SimpleMockUpdateResult(0, 0)
        else:
            # No _id, $or, or active query provided
            return SimpleMockUpdateResult(0, 0)
        
        doc = self.data[doc_id]
        
        # Make a deep copy of the document to avoid reference issues
        doc = doc.copy()
        
        if "$set" in update_data:
            # Print the update for debugging
            print(f"MockDB update for {doc_id}: {update_data['$set']}")
            
            for key, value in update_data["$set"].items():
                # Special handling for brand_colors to ensure it's stored as a new list
                if key == "brand_colors":
                    if value is None:
                        doc[key] = []
                    else:
                        # Create a new list from the input value to avoid reference issues
                        doc[key] = list(value)
                        # Filter out None values
                        doc[key] = [color for color in doc[key] if color]
                        print(f"MockDB setting brand_colors to: {doc[key]}")
                else:
                    doc[key] = value
            
            # Ensure doc has required fields
            if "name" not in doc and "name" in update_data["$set"]:
                doc["name"] = update_data["$set"]["name"]
                
            # Always ensure brand_colors exists
            if "brand_colors" not in doc:
                doc["brand_colors"] = []
                
            # Always make sure some fields exist
            doc["active"] = doc.get("active", True)
            doc["id"] = str(doc_id)
            
            # Store the updated document back in the data store
            self.data[doc_id] = doc
        
        doc["updated_at"] = datetime.utcnow().isoformat()
        return SimpleMockUpdateResult(1, 1)
    
    async def delete_one(self, query):
        if "_id" not in query:
            return SimpleMockDeleteResult(0)
        
        doc_id = query["_id"]
        if doc_id in self.data:
            del self.data[doc_id]
            return SimpleMockDeleteResult(1)
        return SimpleMockDeleteResult(0)
    
    async def delete_many(self, query):
        to_delete = []
        for doc_id, doc in self.data.items():
            match = True
            for key, value in query.items():
                if doc.get(key) != value:
                    match = False
                    break
            if match:
                to_delete.append(doc_id)
        
        for doc_id in to_delete:
            del self.data[doc_id]
        
        return SimpleMockDeleteResult(len(to_delete))

class SimpleMockInsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

class SimpleMockUpdateResult:
    def __init__(self, matched_count, modified_count):
        self.matched_count = matched_count
        self.modified_count = modified_count

class SimpleMockDeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count
