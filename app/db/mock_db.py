import sqlite3
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class MockDatabase:
    def __init__(self):
        # Use in-memory SQLite as a mock for MongoDB
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.setup_tables()
        
    def setup_tables(self):
        # Create basic tables for your collections
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        self.conn.commit()
    
    @property
    def users(self):
        return MockCollection(self.conn, "users")
    
    @property
    def companies(self):
        return MockCollection(self.conn, "companies")
        
    @property
    def materials(self):
        return MockCollection(self.conn, "materials")

    def close(self):
        # Add a close method to mimic AsyncIOMotorClient
        if self.conn:
            self.conn.close()
            import logging
            logging.debug("MockDatabase connection closed.")

class MockCollection:
    def __init__(self, conn, collection_name):
        self.conn = conn
        self.cursor = conn.cursor()
        self.collection_name = collection_name
    
    async def find_one(self, query):
        import logging
        logging.debug(f"Mock DB finding one with query: {query} in collection {self.collection_name}")
        try:
            if "_id" in query and isinstance(query["_id"], int): # Check if _id is an int (likely from SQLite PK)
                id_val = query["_id"]
                self.cursor.execute(f"SELECT data FROM {self.collection_name} WHERE id = ?", (id_val,))
                row = self.cursor.fetchone()
                if row:
                    result = json.loads(row[0])
                    result["_id"] = id_val # Add SQLite id as _id
                    # Additional check to ensure all query parameters match for ID-based finds too
                    all_match = True
                    for key, value in query.items():
                        # if key == "_id": # Already checked by DB query and added to result
                        #     if result.get(key) != value: # Ensure the _id in result matches query if it was part of query
                        #         all_match = False
                        #         break
                        #     continue
                        # The above lines are commented out as _id is now part of the result, 
                        # so the generic check below will handle it.
                        if isinstance(result.get(key), bool) and isinstance(value, str): # Handle boolean string comparison
                             if str(result.get(key)).lower() != value.lower():
                                all_match = False
                                break
                        elif result.get(key) != value:
                            all_match = False
                            break
                    if all_match:
                        logging.debug(f"Found document by ID with all fields matching: {result}")
                        return result
                    else:
                        logging.debug(f"Found document by ID but other fields did not match: {query} vs {result}")
                        return None # ID matched but other fields didn't
                logging.debug(f"No document found matching ID: {id_val}")
                return None
            else:
                # General case: fetch all and filter in Python
                self.cursor.execute(f"SELECT id, data FROM {self.collection_name}") # Select id and data
                for row_data in self.cursor.fetchall(): # Renamed row to row_data to avoid confusion
                    sqlite_id, json_data = row_data # Unpack id and data
                    doc = json.loads(json_data)
                    match = True
                    for key, value in query.items():
                        # Handle potential type mismatches, e.g., bool vs str
                        doc_value = doc.get(key)
                        if isinstance(doc_value, bool) and isinstance(value, str):
                            if str(doc_value).lower() != value.lower():
                                match = False
                                break
                        elif isinstance(doc_value, bool) and isinstance(value, int): # "active": 1 in some DBs
                            if doc_value != bool(value):
                                match = False
                                break
                        elif doc_value != value:
                            match = False
                            break
                    if match:
                        doc["_id"] = sqlite_id # Add SQLite id as _id
                        logging.debug(f"Found document by filtering: {doc}")
                        return doc
                
                logging.debug(f"No document found matching query by filtering: {query}")
                return None
        except Exception as e:
            logging.error(f"Error in find_one: {e}")
            return None
    
    def find(self, query=None):
        return MockCursor(self.conn, self.collection_name, query)
    
    async def insert_one(self, data):
        import logging
        logging.debug(f"Mock DB inserting: {data} into {self.collection_name}")
        try:
            now = datetime.utcnow().isoformat()
            data_json = json.dumps(data)
            self.cursor.execute(
                f"INSERT INTO {self.collection_name} (data, created_at, updated_at) VALUES (?, ?, ?)",
                (data_json, now, now)
            )
            self.conn.commit()
            
            # Verify insertion was successful 
            last_id = self.cursor.lastrowid
            logging.debug(f"Inserted document with ID: {last_id}")
            
            # Double check by retrieving it
            self.cursor.execute(f"SELECT data FROM {self.collection_name} WHERE id = ?", (last_id,))
            row = self.cursor.fetchone()
            if row:
                logging.debug(f"Insert verification successful: {json.loads(row[0])}")
            else:
                logging.warning(f"Could not verify inserted document with id: {last_id}")
            
            return MockInsertResult(last_id)
        except Exception as e:
            logging.error(f"Error in insert_one: {e}")
            raise e
    
    async def delete_one(self, query):
        if "_id" not in query:
            return MockDeleteResult(0)
        
        id_val = query["_id"]
        self.cursor.execute(f"DELETE FROM {self.collection_name} WHERE id = ?", (id_val,))
        self.conn.commit()
        return MockDeleteResult(self.cursor.rowcount)
    
    async def delete_many(self, query):
        # Simple implementation for a specific field
        if len(query) == 0:
            return MockDeleteResult(0)
        
        field = list(query.keys())[0]
        value = query[field]
        self.cursor.execute(f"DELETE FROM {self.collection_name} WHERE data LIKE ?", (f'%\\\"{field}\\\": \\\"{value}\\\"%',)) # Added space after colon
        self.conn.commit()
        return MockDeleteResult(self.cursor.rowcount)
    
    async def update_one(self, query, update_data):
        if "_id" not in query:
            return MockUpdateResult(0, 0)
        
        id_val = query["_id"]
        self.cursor.execute(f"SELECT data FROM {self.collection_name} WHERE id = ?", (id_val,))
        row = self.cursor.fetchone()
        if not row:
            return MockUpdateResult(0, 0)
        
        existing_data = json.loads(row[0])
        
        # Handle $set operations
        if "$set" in update_data:
            for key, value in update_data["$set"].items():
                existing_data[key] = value
        
        # Handle $push operations (add to array)
        if "$push" in update_data:
            for key, value in update_data["$push"].items():
                if key not in existing_data:
                    existing_data[key] = []
                elif not isinstance(existing_data[key], list):
                    existing_data[key] = [existing_data[key]]
                existing_data[key].append(value)
        
        existing_data["updated_at"] = datetime.utcnow().isoformat()
        updated_json = json.dumps(existing_data)
        
        self.cursor.execute(
            f"UPDATE {self.collection_name} SET data = ?, updated_at = ? WHERE id = ?",
            (updated_json, existing_data["updated_at"], id_val)
        )
        self.conn.commit()
        return MockUpdateResult(1, 1)

class MockCursor:
    def __init__(self, conn, collection_name, query=None):
        self.conn = conn
        self.cursor = conn.cursor()
        self.collection_name = collection_name
        self.query = query if query else {}
        self._skip = 0
        self._limit = 100
    
    def skip(self, n):
        self._skip = n
        return self
    
    def limit(self, n):
        self._limit = n
        return self
    
    async def to_list(self, length=None):
        if length is not None:
            self._limit = length
        
        if self.query:
            # Simple filter for demo - only handle basic equality filter
            field = list(self.query.keys())[0]
            value = self.query[field]
            self.cursor.execute(
                f"SELECT data FROM {self.collection_name} WHERE data LIKE ? LIMIT ? OFFSET ?", 
                (f'%\\\"{field}\\\": \\\"{value}\\\"%', self._limit, self._skip) # Added space after colon
            )
        else:    
            self.cursor.execute(
                f"SELECT data FROM {self.collection_name} LIMIT ? OFFSET ?", 
                (self._limit, self._skip)
            )
        
        results = []
        for row in self.cursor.fetchall():
            results.append(json.loads(row[0]))
        return results

class MockInsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

class MockUpdateResult:
    def __init__(self, matched_count, modified_count):
        self.matched_count = matched_count
        self.modified_count = modified_count

class MockDeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count

class AsyncIOMotorClientMock:
    def __init__(self, *args, **kwargs):
        self._db = MockDatabase()
    
    def __getitem__(self, db_name):
        return self._db
    
    async def admin(self):
        class MockAdmin:
            async def command(self, cmd):
                return {"ok": 1}  # Always return success
        return MockAdmin()
    
    def close(self):
        pass
