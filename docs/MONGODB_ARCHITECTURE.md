# MongoDB Architecture Documentation

## Overview

The AI Marketing Agent uses **MongoDB** as its primary database for persistent data storage. This document describes the database architecture, connection patterns, collection schemas, indexing strategy, and development setup.

## Migration History

**Date:** January 2025  
**Migration:** SimpleMockDatabase (JSON file persistence) → Real MongoDB  
**Reason:** Previous mock database violated business rule requiring "database-driven" architecture  
**Result:** Successfully migrated 1 user, 1 company, and 9 AI providers to MongoDB

---

## Database Connection

### Configuration

**MongoDB Connection Module:** `app/db/mongodb.py`

```python
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None
    
    async def connect(self):
        """Establish connection to MongoDB with connection pooling"""
        self.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=10,
            minPoolSize=1,
            serverSelectionTimeoutMS=5000
        )
        self.db = self.client[settings.MONGODB_DB]
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
    
    @property
    def users(self):
        return self.db.users
    
    @property
    def companies(self):
        return self.db.companies
    
    @property
    def materials(self):
        return self.db.materials
    
    @property
    def ai_providers(self):
        return self.db.ai_providers

# Global instance
mongodb = MongoDB()
```

### Connection Settings

**Environment Variables:**
- `MONGODB_URL`: MongoDB connection string (default: `mongodb://localhost:27017`)
- `MONGODB_DB`: Database name (default: `ai_marketing_agent`)

**Connection Pool Configuration:**
- `maxPoolSize`: 10 connections
- `minPoolSize`: 1 connection
- `serverSelectionTimeoutMS`: 5000ms

### Application Lifecycle

**Startup (app/main.py):**
```python
@api_app.on_event("startup")
async def startup_db_client():
    from app.db.mongodb import mongodb
    await mongodb.connect()
    api_app.mongodb = mongodb.db
    api_app.mongodb_client = mongodb.client
    await mongodb.create_indexes()
    logger.info("✅ Successfully connected to MongoDB - using real database")
```

**Shutdown (app/main.py):**
```python
@api_app.on_event("shutdown")
async def shutdown_db_client():
    from app.db.mongodb import mongodb
    await mongodb.close()
    logger.info("🔌 MongoDB connection closed")
```

---

## Collection Schemas

### 1. Users Collection (`users`)

**Purpose:** Store user authentication and profile data

**Schema:**
```json
{
  "_id": "ObjectId",
  "id": "string (unique)",
  "email": "string (unique, required)",
  "name": "string (required)",
  "hashed_password": "string (bcrypt hash)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Indexes:**
- `email`: Unique index for authentication lookup
- `id`: Index for legacy ID compatibility

**Example Document:**
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "id": "1",
  "email": "demo@example.com",
  "name": "Demo User",
  "hashed_password": "$2b$12$...",
  "created_at": ISODate("2025-01-15T10:00:00Z"),
  "updated_at": ISODate("2025-01-15T10:00:00Z")
}
```

---

### 2. Companies Collection (`companies`)

**Purpose:** Store company profiles and branding information

**Schema:**
```json
{
  "_id": "ObjectId",
  "id": "string (unique)",
  "user_id": "string (indexed)",
  "name": "string (required)",
  "industry": "string",
  "description": "string",
  "target_audience": "string",
  "brand_values": "array of strings",
  "brand_colors": {
    "primary": "string (hex color)",
    "secondary": "string (hex color)",
    "accent": "string (hex color)"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Indexes:**
- `user_id`: Index for user-company relationship
- `id`: Index for legacy ID compatibility

**Example Document:**
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439012"),
  "id": "1",
  "user_id": "1",
  "name": "Philips Healthcare",
  "industry": "Healthcare Technology",
  "description": "Leading health technology company",
  "target_audience": "Healthcare professionals and patients",
  "brand_values": ["Innovation", "Care", "Quality"],
  "brand_colors": {
    "primary": "#00629B",
    "secondary": "#FFFFFF",
    "accent": "#FFB81C"
  },
  "created_at": ISODate("2025-01-15T10:00:00Z"),
  "updated_at": ISODate("2025-01-15T10:00:00Z")
}
```

---

### 3. AI Providers Collection (`ai_providers`)

**Purpose:** Store AI provider configurations and API credentials

**Schema:**
```json
{
  "_id": "ObjectId",
  "id": "string (required)",
  "user_id": "string (required)",
  "name": "string (required)",
  "type": "string (openai|anthropic|google)",
  "apiKey": "string (encrypted)",
  "isActive": "boolean",
  "models": ["array of model strings"],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Indexes:**
- `(user_id, id)`: Composite unique index to prevent duplicate provider IDs per user
- `user_id`: Index for user-provider relationship lookup
- `isActive`: Index for filtering active providers

**Example Document:**
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439013"),
  "id": "openai",
  "user_id": "1",
  "name": "OpenAI",
  "type": "openai",
  "apiKey": "sk-...",
  "isActive": true,
  "models": ["gpt-4", "gpt-3.5-turbo"],
  "created_at": ISODate("2025-01-15T10:00:00Z"),
  "updated_at": ISODate("2025-01-15T10:00:00Z")
}
```

---

### 4. Materials Collection (`materials`)

**Purpose:** Store marketing materials, campaigns, and generated content

**Schema:**
```json
{
  "_id": "ObjectId",
  "id": "string (unique)",
  "user_id": "string (indexed)",
  "company_id": "string (indexed)",
  "title": "string (required)",
  "content": "string",
  "material_type": "string (social_media|email|landing_page|...)",
  "status": "string (draft|published|archived)",
  "ai_provider": "string",
  "model_used": "string",
  "metadata": "object",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Indexes:**
- `user_id`: Index for user materials lookup
- `company_id`: Index for company materials lookup
- `status`: Index for filtering by status

---

## Indexing Strategy

### Performance Indexes

**Created on Startup:** `mongodb.create_indexes()`

```python
async def create_indexes(self):
    """Create database indexes for performance and data integrity"""
    
    # Users indexes
    await self.users.create_index("email", unique=True)
    await self.users.create_index("id")
    
    # Companies indexes
    await self.users.create_index("user_id")
    await self.companies.create_index("id")
    
    # AI Providers indexes
    await self.ai_providers.create_index([("user_id", 1), ("id", 1)], unique=True)
    await self.ai_providers.create_index("user_id")
    await self.ai_providers.create_index("isActive")
    
    # Materials indexes
    await self.materials.create_index("user_id")
    await self.materials.create_index("company_id")
    await self.materials.create_index("status")
```

### Index Rationale

| Index | Collection | Type | Purpose |
|-------|-----------|------|---------|
| `email` | users | Unique | Authentication lookup, prevent duplicate accounts |
| `user_id` | companies | Single | User-company relationship queries |
| `(user_id, id)` | ai_providers | Composite Unique | Prevent duplicate provider IDs per user |
| `isActive` | ai_providers | Single | Filter active providers efficiently |
| `company_id` | materials | Single | Company materials lookup |
| `status` | materials | Single | Filter materials by status |

---

## CRUD Operation Patterns

### Using Motor Async Driver

All database operations use **Motor** (async MongoDB driver for Python).

#### Read Operations

**Find One Document:**
```python
from app.db.mongodb import get_database

async def get_user_by_email(email: str):
    db = await get_database()
    user = await db.users.find_one({"email": email})
    return user
```

**Find Multiple Documents:**
```python
async def get_user_providers(user_id: str):
    db = await get_database()
    cursor = db.ai_providers.find({"user_id": user_id})
    providers = await cursor.to_list(length=None)
    return providers
```

**Find with Projection:**
```python
async def get_user_emails():
    db = await get_database()
    cursor = db.users.find({}, {"email": 1, "name": 1, "_id": 0})
    users = await cursor.to_list(length=None)
    return users
```

#### Create Operations

**Insert One Document:**
```python
async def create_company(company_data: dict):
    db = await get_database()
    result = await db.companies.insert_one(company_data)
    return result.inserted_id
```

**Insert Multiple Documents:**
```python
async def create_materials(materials: list):
    db = await get_database()
    result = await db.materials.insert_many(materials)
    return result.inserted_ids
```

#### Update Operations

**Update One Document:**
```python
async def update_provider_api_key(user_id: str, provider_id: str, api_key: str):
    db = await get_database()
    result = await db.ai_providers.update_one(
        {"user_id": user_id, "id": provider_id},
        {"$set": {"apiKey": api_key, "updated_at": datetime.utcnow()}}
    )
    return result.modified_count > 0
```

**Update with Operators:**
```python
async def add_brand_value(company_id: str, value: str):
    db = await get_database()
    result = await db.companies.update_one(
        {"id": company_id},
        {"$push": {"brand_values": value}}
    )
    return result.modified_count > 0
```

#### Delete Operations

**Delete One Document:**
```python
async def delete_provider(user_id: str, provider_id: str):
    db = await get_database()
    result = await db.ai_providers.delete_one(
        {"user_id": user_id, "id": provider_id}
    )
    return result.deleted_count > 0
```

**Delete Multiple Documents:**
```python
async def delete_user_materials(user_id: str):
    db = await get_database()
    result = await db.materials.delete_many({"user_id": user_id})
    return result.deleted_count
```

---

## Migration Process

### Initial Migration Script

**Location:** `scripts/migrate_to_mongodb.py`

**Purpose:** One-time migration from JSON files to MongoDB

**Usage:**
```bash
python scripts/migrate_to_mongodb.py
```

**What It Does:**
1. Connects to MongoDB
2. Clears existing collections (users, companies, ai_providers)
3. Loads JSON data from `app/db/data/*.json`
4. Converts datetime strings to datetime objects
5. Inserts documents into collections
6. Creates performance indexes
7. Reports migration summary

**Migration Results:**
```
✅ Migration complete!
users: 1 documents
companies: 1 documents
ai_providers: 9 documents
```

### Data Quality Fix Script

**Location:** `scripts/fix_ai_providers_data.py`

**Purpose:** Fix data quality issues in AI providers collection

**Usage:**
```bash
python scripts/fix_ai_providers_data.py
```

**What It Does:**
1. Fixes providers with null `id` field
2. Drops old unique index
3. Recreates unique composite index on `(user_id, id)`

---

## Local Development Setup

### Prerequisites

1. **Install MongoDB:**
   - Ubuntu/WSL: `sudo apt-get install -y mongodb`
   - macOS: `brew install mongodb-community`
   - Windows: Download from [mongodb.com](https://www.mongodb.com/try/download/community)

2. **Start MongoDB Service:**
   ```bash
   # Ubuntu/WSL
   sudo service mongodb start
   
   # macOS
   brew services start mongodb-community
   
   # Windows
   net start MongoDB
   ```

3. **Verify MongoDB is Running:**
   ```bash
   mongo --eval "db.version()"
   ```

### Environment Configuration

**Create `.env` file:**
```bash
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=ai_marketing_agent
```

### Initialize Database

**Run Migration Script:**
```bash
cd /path/to/ai-marketing-agent
python scripts/migrate_to_mongodb.py
```

**Verify Data:**
```bash
mongo ai_marketing_agent
> db.users.count()
1
> db.companies.count()
1
> db.ai_providers.count()
9
```

### Start Application

**Backend:**
```bash
uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload
```

**Expected Logs:**
```
✅ Successfully connected to MongoDB - using real database
📊 Database initialized: 1 users, 1 companies, 9 AI providers
✅ MongoDB indexes created successfully
```

---

## Troubleshooting

### Connection Issues

**Problem:** `ServerSelectionTimeoutError`

**Solution:**
1. Check MongoDB is running: `sudo service mongodb status`
2. Verify connection string in `.env`
3. Check firewall settings: `sudo ufw allow 27017`

### Index Issues

**Problem:** `DuplicateKeyError` on insert

**Solution:**
```python
# Drop and recreate indexes
await db.ai_providers.drop_index("user_id_1_id_1")
await db.ai_providers.create_index([("user_id", 1), ("id", 1)], unique=True)
```

### Performance Issues

**Problem:** Slow queries

**Solution:**
1. Check if indexes exist: `db.ai_providers.getIndexes()`
2. Use explain plan: `db.ai_providers.find({...}).explain("executionStats")`
3. Add missing indexes based on query patterns

---

## Best Practices

### 1. Always Use Async Methods
```python
# ✅ Good
providers = await db.ai_providers.find({"user_id": user_id}).to_list(length=None)

# ❌ Bad (blocking)
providers = list(db.ai_providers.find({"user_id": user_id}))
```

### 2. Use Projection to Reduce Data Transfer
```python
# ✅ Good - only fetch needed fields
user = await db.users.find_one({"email": email}, {"_id": 1, "email": 1, "name": 1})

# ❌ Bad - fetches all fields including large ones
user = await db.users.find_one({"email": email})
```

### 3. Handle ObjectId Serialization
```python
from bson import ObjectId

# Convert ObjectId to string for JSON responses
def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc
```

### 4. Use Indexes for Filtering
```python
# ✅ Good - uses index on isActive
active_providers = await db.ai_providers.find({"user_id": user_id, "isActive": True}).to_list(length=None)
```

### 5. Auto-Persist (No Manual Save)
```python
# ✅ MongoDB auto-persists after update_one/insert_one
await db.ai_providers.update_one({"id": provider_id}, {"$set": {"apiKey": new_key}})
# No need for db.save() or db.commit()

# ❌ Old mock database pattern (no longer needed)
# db.save_collection("ai_providers")
```

---

## References

- **MongoDB Documentation:** https://www.mongodb.com/docs/
- **Motor Documentation:** https://motor.readthedocs.io/
- **FastAPI + MongoDB:** https://www.mongodb.com/developer/languages/python/python-quickstart-fastapi/
- **Migration Script:** `scripts/migrate_to_mongodb.py`
- **Connection Module:** `app/db/mongodb.py`

---

**Last Updated:** January 2025  
**Migration Status:** ✅ Complete  
**Production Ready:** ✅ Yes
