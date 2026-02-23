"""
Fix AI Providers Data Quality
Some providers have null 'id' field which causes index errors
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def fix_ai_providers_data():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    collection = db.ai_providers
    
    print("Checking AI providers for data quality issues...")
    
    # Find all providers
    providers = await collection.find({}).to_list(None)
    
    print(f"Found {len(providers)} providers")
    
    fixed_count = 0
    for provider in providers:
        needs_fix = False
        updates = {}
        
        # Fix missing 'id' field
        if 'id' not in provider or provider.get('id') is None:
            # Use _id as the id
            updates['id'] = str(provider['_id'])
            needs_fix = True
            print(f"  Fixing provider {provider.get('name', 'unknown')}: adding id={updates['id']}")
        
        # Apply fixes
        if needs_fix:
            await collection.update_one(
                {'_id': provider['_id']},
                {'$set': updates}
            )
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} providers")
    
    # Now try to create the unique index
    try:
        await collection.drop_index("user_id_1_id_1")
        print("Dropped old index")
    except:
        pass
    
    try:
        await collection.create_index([("user_id", 1), ("id", 1)], unique=True)
        print("✅ Created unique index on (user_id, id)")
    except Exception as e:
        print(f"⚠️  Could not create index: {e}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_ai_providers_data())
