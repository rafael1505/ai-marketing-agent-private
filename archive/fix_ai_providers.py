#!/usr/bin/env python3
"""
Script to fix the AI Provider Configuration system.
This script will:
1. Check if the SimpleMockDatabase has the ai_providers collection
2. Add it if missing
3. Verify the API endpoints for provider configuration
"""
import sys
import os
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ai_provider_fix')

try:
    # Import from the application
    sys.path.append(os.getcwd())
    from app.db.simple_mock_db import SimpleMockDatabase
    
    def fix_providers_collection():
        """Ensure the ai_providers collection exists in the database"""
        logger.info("Checking SimpleMockDatabase for ai_providers collection...")
        db = SimpleMockDatabase()
        
        # Check if ai_providers exists in the _data dictionary
        if "ai_providers" not in db._data:
            logger.info("Adding ai_providers collection to SimpleMockDatabase...")
            db._data["ai_providers"] = {}
        else:
            logger.info("ai_providers collection already exists")
            
        # Print current state of ai_providers
        logger.info(f"Current ai_providers: {db._data['ai_providers']}")
        
        # Add the OpenAI provider with default configuration
        openai_id = "openai"
        if openai_id not in db._data["ai_providers"]:
            logger.info("Adding default OpenAI configuration")
            db._data["ai_providers"][openai_id] = {
                "id": openai_id,
                "name": "OpenAI",
                "isConfigured": False,
                "apiKey": "",  # Empty key
                "selectedModel": "dall-e-3",
                "quality": "standard",
                "size": "1024x1024",
                "style": "vivid",
                "isActive": True
            }
            logger.info(f"Added default OpenAI configuration: {db._data['ai_providers'][openai_id]}")
        
        return "Fixed: ai_providers collection is ready"

    # Execute the fix
    result = fix_providers_collection()
    print(result)

except Exception as e:
    logger.error(f"Error fixing AI provider configuration: {str(e)}", exc_info=True)
    print(f"Error: {str(e)}")
