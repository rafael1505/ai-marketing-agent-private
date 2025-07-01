import sys
import traceback
import logging
from fastapi import FastAPI, Request
import uvicorn

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # Create a minimal FastAPI application
    app = FastAPI(title="Minimal API Test")
    
    # Add a simple root endpoint
    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/ping")
    async def ping():
        return {"status": "ok", "message": "pong"}
    
    # Try to import the AI providers router
    try:
        logger.info("Importing AI providers router...")
        from app.api.v1.ai_providers import router as ai_providers_router
        logger.info("AI providers router imported successfully")
        
        # Include the AI providers router
        app.include_router(ai_providers_router, prefix="/api/v1/ai-providers", tags=["ai-providers"])
        logger.info("AI providers router included in app")
    except Exception as router_err:
        logger.error(f"Error importing AI providers router: {router_err}")
        traceback.print_exc()
    
    # Add a simple mock endpoint for AI providers for testing
    @app.get("/api/v1/ai-providers-mock")
    async def mock_ai_providers():
        return [{"name": "Mock Provider", "id": "mock", "isConfigured": True}]
    
    if __name__ == "__main__":
        logger.info("Starting minimal API test server on port 8090...")
        uvicorn.run(app, host="127.0.0.1", port=8090)
except Exception as e:
    logger.error(f"Error in minimal API test: {e}")
    traceback.print_exc()
    sys.exit(1)
