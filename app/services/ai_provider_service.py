"""
Database-driven AI Provider Service
Replaces MOCK_PROVIDERS with proper database seeding and fallback
"""

from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class AIProviderService:
    """
    Database-driven AI Provider service with automatic seeding
    and graceful fallback mechanisms
    """
    
    def __init__(self, database_client=None):
        self.db = database_client
        self.default_providers = self._get_default_provider_templates()
    
    def _get_default_provider_templates(self) -> List[Dict[str, Any]]:
        """
        Provider templates for database seeding
        These are NOT mock data - they're templates for database initialization
        """
        return [
            # FREE PROVIDERS
            {
                "id": "ollama",
                "name": "Ollama (Local)",
                "type": "text",
                "status": "active",
                "description": "Completely free - runs locally on your machine. Supports Llama 2, Code Llama, Mistral, and other open-source models",
                "configured": False,
                "available": True,
                "model": "llama-2",
                "logo": "/ai-providers/ollama.svg",
                "features": ["text-generation", "local"],
                "pricing": {"tier": "free", "description": "Completely free - runs locally on your machine"},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": "lmstudio",
                "name": "LM Studio",
                "type": "text",
                "status": "active",
                "description": "Free local LLM runtime. Run any open-source model on your hardware",
                "configured": False,
                "available": True,
                "model": "local-llm",
                "logo": "/ai-providers/lmstudio.svg",
                "features": ["text-generation", "local"],
                "pricing": {"tier": "free", "description": "Free local LLM runtime"},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            # FREEMIUM PROVIDERS
            {
                "id": "huggingface",
                "name": "Hugging Face",
                "type": "both",
                "status": "active",
                "description": "1,000 requests/month free for Inference API",
                "configured": False,
                "available": True,
                "model": "text-to-image",
                "logo": "/ai-providers/huggingface.svg",
                "features": ["text-generation", "text-to-image"],
                "pricing": {"tier": "freemium", "free_requests": 1000, "per_request": 0.001},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": "colab",
                "name": "Google Colab",
                "type": "compute",
                "status": "active",
                "description": "Free GPU/TPU access with usage limits. Run Gemini, open-source models",
                "configured": False,
                "available": True,
                "model": "custom",
                "logo": "/ai-providers/colab.svg",
                "features": ["compute", "gpu", "tpu"],
                "pricing": {"tier": "freemium", "monthly_fee": 9.99},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": "replicate",
                "name": "Replicate",
                "type": "both",
                "status": "active",
                "description": "Free tier with limited usage. Pay-per-use for additional requests",
                "configured": False,
                "available": True,
                "model": "various",
                "logo": "/ai-providers/replicate.svg",
                "features": ["text-generation", "text-to-image"],
                "pricing": {"tier": "freemium", "per_request": 0.0023},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            # PAID PROVIDERS
            {
                "id": "openai",
                "name": "OpenAI",
                "type": "both",
                "status": "active",
                "description": "GPT-4o, GPT-4 Turbo, DALL-E 3 for text and image generation",
                "configured": False,
                "available": True,
                "model": "gpt-4o",
                "logo": "/ai-providers/openai.svg",
                "features": ["text-generation", "text-to-image"],
                "pricing": {"tier": "paid", "per_token": 0.000005, "per_image": 0.04},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": "anthropic",
                "name": "Anthropic Claude",
                "type": "text",
                "status": "active", 
                "description": "Claude 3 Haiku, Sonnet, and Opus for advanced text generation",
                "configured": False,
                "available": True,
                "model": "claude-3-sonnet",
                "logo": "/ai-providers/anthropic.svg",
                "features": ["text-generation", "analysis"],
                "pricing": {"tier": "paid", "per_token": 0.000003},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": "stability",
                "name": "Stability AI",
                "type": "image", 
                "status": "active",
                "description": "Stable Diffusion for professional image generation",
                "configured": False,
                "available": True,
                "model": "stable-diffusion-xl",
                "logo": "/ai-providers/stability.svg",
                "features": ["text-to-image"],
                "pricing": {"tier": "paid", "per_image": 0.04, "monthly_fee": 20},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": "midjourney",
                "name": "Midjourney",
                "type": "image",
                "status": "active",
                "description": "Premium AI image generation with artistic styles",
                "configured": False,
                "available": True,
                "model": "midjourney-v6",
                "logo": "/ai-providers/midjourney.svg",
                "features": ["text-to-image", "artistic"],
                "pricing": {"tier": "paid", "monthly_fee": 10},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]
    
    async def ensure_providers_exist(self, user_id: str = "1") -> bool:
        """
        Ensure the database has provider templates
        This seeds the database if empty
        """
        try:
            if self.db is None:
                logger.warning("No database connection - cannot seed providers")
                return False
                
            providers_collection = self.db.ai_providers
            
            # Check if any providers exist for this user
            existing_count = len(await providers_collection.find({"user_id": user_id}).to_list(1000))
            
            if existing_count == 0:
                logger.info(f"Seeding database with {len(self.default_providers)} provider templates")
                
                # Add user_id to each provider template
                providers_to_insert = []
                for provider in self.default_providers:
                    provider_with_user = {**provider, "user_id": user_id}
                    providers_to_insert.append(provider_with_user)
                
                # Insert all providers
                for provider in providers_to_insert:
                    await providers_collection.insert_one(provider)
                
                logger.info(f"Successfully seeded {len(providers_to_insert)} providers")
                return True
            else:
                logger.debug(f"Database already has {existing_count} providers for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to seed providers: {e}")
            return False
    
    async def get_providers(self, user_id: str = "1") -> List[Dict[str, Any]]:
        """
        Get providers from database with automatic seeding
        NO fallback to hardcoded mock data
        """
        try:
            # First, ensure providers exist in database
            await self.ensure_providers_exist(user_id)
            
            if self.db is None:
                logger.error("No database connection available")
                return []
            
            providers_collection = self.db.ai_providers
            providers = await providers_collection.find({"user_id": user_id}).to_list(1000)
            
            # Clean up and transform provider data for frontend
            cleaned_providers = []
            for provider in providers:
                # Remove MongoDB _id
                if "_id" in provider:
                    del provider["_id"]
                
                # Transform database fields to frontend expected structure
                # Mask API key if it exists
                api_key_display = None
                if "api_key" in provider and provider["api_key"]:
                    api_key_display = "••••••••••••••••"
                
                transformed_provider = {
                    "id": str(provider["id"]),
                    "name": provider["name"],
                    "logo": provider.get("logo"),
                    "apiKey": api_key_display,
                    "isConfigured": provider.get("configured", False) or bool(api_key_display),
                    "isActive": provider.get("status") == "active" or provider.get("active", False),
                    "modelOptions": provider.get("features", []),
                    "selectedModel": provider.get("model"),
                    "maxTokens": provider.get("maxTokens", provider.get("max_tokens", 1000)),
                    "temperature": provider.get("temperature", 0.7),
                    "baseUrl": provider.get("baseUrl", provider.get("base_url")),
                    "pricing": provider.get("pricing", {"tier": "unknown"})
                }
                
                cleaned_providers.append(transformed_provider)
            
            logger.info(f"Retrieved and transformed {len(cleaned_providers)} providers from database")
            return cleaned_providers
            
        except Exception as e:
            logger.error(f"Failed to get providers from database: {e}")
            return []
    
    async def get_provider(self, provider_id: str, user_id: str = "1") -> Optional[Dict[str, Any]]:
        """
        Get a specific provider from database
        """
        try:
            if self.db is None:
                logger.error("No database connection available")
                return None
                
            providers_collection = self.db.ai_providers
            
            # Try multiple query patterns to work with different database structures
            queries_to_try = [
                {"_id": provider_id, "user_id": user_id},  # Mock DB pattern
                {"id": provider_id, "user_id": user_id},   # Real MongoDB pattern
                {"_id": provider_id},                      # Mock DB fallback
            ]
            
            provider = None
            for query in queries_to_try:
                logger.debug(f"Trying query: {query}")
                provider = await providers_collection.find_one(query)
                if provider:
                    logger.debug(f"Found provider with query: {query}")
                    break
            
            if not provider:
                logger.warning(f"Provider {provider_id} not found with any query pattern")
                return None

            # Clean up the provider data and transform fields to frontend format
            if "_id" in provider:
                # Store the _id as id for the response
                provider["id"] = str(provider["_id"])
                del provider["_id"]

            # Transform database fields to frontend expected structure
            # Mask API key if it exists
            api_key_display = None
            if "api_key" in provider and provider["api_key"]:
                api_key_display = "••••••••••••••••"
            
            transformed_provider = {
                "id": str(provider["id"]),
                "name": provider["name"],
                "logo": provider.get("logo"),
                "apiKey": api_key_display,
                "isConfigured": provider.get("configured", False) or bool(api_key_display),
                "isActive": provider.get("status") == "active" or provider.get("active", False),
                "modelOptions": provider.get("features", []),
                "selectedModel": provider.get("model"),
                "maxTokens": provider.get("maxTokens", provider.get("max_tokens", 1000)),
                "temperature": provider.get("temperature", 0.7),
                "baseUrl": provider.get("baseUrl", provider.get("base_url")),
                "pricing": provider.get("pricing", {"tier": "unknown"})
            }
            
            logger.debug(f"Returning transformed provider: {transformed_provider}")
            return transformed_provider
            
        except Exception as e:
            logger.error(f"Failed to get provider {provider_id}: {e}")
            return None
    
    async def update_provider(self, provider_id: str, updates: Dict[str, Any], user_id: str = "1") -> Optional[Dict[str, Any]]:
        """
        Update a specific provider in the database
        """
        try:
            if self.db is None:
                logger.error("No database connection available")
                return None
                
            providers_collection = self.db.ai_providers
            
            # Map frontend field names to backend field names
            backend_updates = {}
            for key, value in updates.items():
                if key == "isConfigured":
                    backend_updates["configured"] = value
                elif key == "isActive":
                    backend_updates["status"] = "active" if value else "inactive"
                elif key == "apiKey":
                    # Only update API key if it's not a masked value
                    if value and not value.startswith("•"):
                        backend_updates["api_key"] = value
                elif key == "selectedModel":
                    backend_updates["model"] = value
                else:
                    # Pass through other fields as-is
                    backend_updates[key] = value
            
            # Add update timestamp
            backend_updates["updated_at"] = datetime.utcnow().isoformat()
            
            logger.debug(f"Updating provider {provider_id} with backend updates: {backend_updates}")
            
            # Try multiple update patterns to work with different database structures
            update_queries = [
                {"_id": provider_id, "user_id": user_id},  # Mock DB pattern
                {"id": provider_id, "user_id": user_id},   # Real MongoDB pattern
                {"_id": provider_id},                      # Mock DB fallback
            ]
            
            result = None
            for query in update_queries:
                logger.debug(f"Trying update query: {query}")
                try:
                    result = await providers_collection.update_one(query, {"$set": backend_updates})
                    logger.debug(f"Update result: matched={result.matched_count}, modified={result.modified_count}")
                    if result.matched_count > 0:
                        logger.debug(f"Successfully updated with query: {query}")
                        break
                except Exception as e:
                    logger.error(f"Update failed with query {query}: {e}")
            
            if not result or result.matched_count == 0:
                logger.warning(f"Provider {provider_id} not found for user {user_id}")
                return None
            
            logger.info(f"Updated provider {provider_id} with fields: {list(backend_updates.keys())}")
            
            # Return the updated provider
            return await self.get_provider(provider_id, user_id)
            
        except Exception as e:
            logger.error(f"Failed to update provider {provider_id}: {e}")
            return None

# Global service instance
provider_service = None

def get_provider_service(database_client=None):
    """
    Get or create the global provider service instance
    """
    global provider_service
    if provider_service is None:
        provider_service = AIProviderService(database_client)
    elif database_client is not None:
        # Always update the database connection to ensure we're using the current one
        provider_service.db = database_client
    
    return provider_service