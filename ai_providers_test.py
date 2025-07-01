import sys
import logging
import traceback
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)
logger.info("Starting AI Providers API test")

try:
    # Create a minimal FastAPI application
    app = FastAPI(title="AI Providers API Test")
    
    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Set up mock database
    class SimpleMockDatabase:
        def __init__(self):
            self.ai_providers = MockCollection()
            
        def close(self):
            pass
    
    class MockCollection:
        def __init__(self):
            self.providers = [
                {
                    "name": "Stability AI",
                    "id": "stability",
                    "logo": "/ai-providers/stability.svg",
                    "isConfigured": True,
                    "selectedModel": "stable-diffusion-xl-1024-v1-0",
                    "maxTokens": 1000,
                    "temperature": 0.7,
                    "isActive": True,
                    "user_id": "1"
                },
                {
                    "name": "Hugging Face",
                    "id": "huggingface",
                    "logo": "/ai-providers/huggingface.svg",
                    "isConfigured": False,
                    "user_id": "1"
                }
            ]
        
        async def find(self, query):
            user_id = query.get("user_id")
            results = [p for p in self.providers if p.get("user_id") == user_id]
            return MockCursor(results)
            
        async def find_one(self, query):
            for provider in self.providers:
                matches = True
                for key, value in query.items():
                    if provider.get(key) != value:
                        matches = False
                        break
                if matches:
                    return provider
            return None
            
        async def insert_one(self, document):
            self.providers.append(document)
            return MockInsertResult()
            
        async def update_one(self, query, update):
            for i, provider in enumerate(self.providers):
                matches = True
                for key, value in query.items():
                    if provider.get(key) != value:
                        matches = False
                        break
                if matches:
                    # Apply updates
                    for key, value in update.get("$set", {}).items():
                        self.providers[i][key] = value
                    return MockUpdateResult(1)
            return MockUpdateResult(0)
            
        async def delete_one(self, query):
            for i, provider in enumerate(self.providers):
                matches = True
                for key, value in query.items():
                    if provider.get(key) != value:
                        matches = False
                        break
                if matches:
                    del self.providers[i]
                    return MockDeleteResult(1)
            return MockDeleteResult(0)
    
    class MockCursor:
        def __init__(self, results):
            self.results = results
            
        async def to_list(self, length):
            return self.results
    
    class MockInsertResult:
        pass
        
    class MockUpdateResult:
        def __init__(self, matched_count):
            self.matched_count = matched_count
            
    class MockDeleteResult:
        def __init__(self, deleted_count):
            self.deleted_count = deleted_count
    
    # Set up the mock database
    app.mongodb_client = SimpleMockDatabase()
    app.mongodb = app.mongodb_client

    # Define a simple mock get_current_user_id function
    def get_current_user_id():
        return "1"
        
    # Import the router directly and patch it
    from app.api.v1.ai_providers import router, AIProviderModel
    
    # Add the missing get_current_user_id function to the router's module
    import app.api.v1.ai_providers
    app.api.v1.ai_providers.get_current_user_id = get_current_user_id
    
    # Include the router in the app
    app.include_router(router, prefix="/api/v1/ai-providers", tags=["ai-providers"])
    
    # Add a simple root endpoint
    @app.get("/")
    async def root():
        return {"message": "AI Providers API Test"}
        
    @app.get("/ping")
    async def ping():
        return {"status": "ok"}
    
    # Run the application
    if __name__ == "__main__":
        import uvicorn
        logger.info("Starting server on port 8099...")
        uvicorn.run(app, host="127.0.0.1", port=8099)
        
except Exception as e:
    logger.error(f"Error: {e}")
    traceback.print_exc()
    sys.exit(1)
