from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Body, Request, Depends
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Mock function for user ID - in a real app, this would come from authentication
def get_current_user_id():
    # For development/testing, return a fixed user ID
    return "1"

class PricingPlan(BaseModel):
    name: str
    pricePerToken: Optional[float] = None
    pricePerRequest: Optional[float] = None
    monthlyFee: Optional[float] = None
    currency: str = "USD"
    description: Optional[str] = None

class FreeQuota(BaseModel):
    requestsPerMonth: Optional[int] = None
    tokensPerMonth: Optional[int] = None
    description: Optional[str] = None

class Pricing(BaseModel):
    tier: str  # 'free', 'freemium', 'paid'
    freeQuota: Optional[FreeQuota] = None
    paidPlans: Optional[List[PricingPlan]] = None
    websiteUrl: Optional[str] = None

class AIProviderModel(BaseModel):
    name: str
    id: str
    logo: Optional[str] = None
    apiKey: Optional[str] = None
    isConfigured: Optional[bool] = False
    modelOptions: Optional[List[str]] = []
    selectedModel: Optional[str] = None
    maxTokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    isActive: Optional[bool] = True
    pricing: Optional[Pricing] = None

class ValidationRequest(BaseModel):
    providerId: str
    apiKey: str

# Mock data - Popular AI providers with realistic pricing tiers
MOCK_PROVIDERS = [
    # FREE PROVIDERS
    {
        "name": "Ollama (Local)",
        "id": "ollama",
        "logo": "/ai-providers/ollama.svg",
        "isConfigured": False,
        "maxTokens": 4096,
        "temperature": 0.7,
        "isActive": True,
        "user_id": "1",
        "pricing": {
            "tier": "free",
            "freeQuota": {
                "description": "Completely free - runs locally on your machine. Supports Llama 2, Code Llama, Mistral, and other open-source models"
            },
            "websiteUrl": "https://ollama.ai"
        }
    },
    {
        "name": "LM Studio",
        "id": "lmstudio",
        "logo": "/ai-providers/lmstudio.svg",
        "isConfigured": False,
        "maxTokens": 4096,
        "temperature": 0.7,
        "isActive": True,
        "user_id": "1",
        "pricing": {
            "tier": "free",
            "freeQuota": {
                "description": "Free local LLM runtime. Run any open-source model on your hardware"
            },
            "websiteUrl": "https://lmstudio.ai"
        }
    },
    
    # FREEMIUM PROVIDERS
    {
        "name": "Hugging Face",
        "id": "huggingface",
        "logo": "/ai-providers/huggingface.svg",
        "isConfigured": False,
        "selectedModel": "runwayml/stable-diffusion-v1-5",
        "maxTokens": 1000,
        "temperature": 0.7,
        "isActive": True,
        "user_id": "1",
        "pricing": {
            "tier": "freemium",
            "freeQuota": {
                "requestsPerMonth": 1000,
                "description": "1,000 requests/month free for Inference API"
            },
            "paidPlans": [
                {
                    "name": "Pro",
                    "monthlyFee": 9,
                    "currency": "USD",
                    "description": "$9/month for unlimited requests and priority access"
                }
            ],
            "websiteUrl": "https://huggingface.co/pricing"
        }
    },
    {
        "name": "Google Colab",
        "id": "colab",
        "logo": "/ai-providers/colab.svg",
        "isConfigured": False,
        "maxTokens": 2048,
        "temperature": 0.7,
        "isActive": True,
        "user_id": "1",
        "pricing": {
            "tier": "freemium",
            "freeQuota": {
                "description": "Free GPU/TPU access with usage limits. Run Gemini, open-source models"
            },
            "paidPlans": [
                {
                    "name": "Colab Pro",
                    "monthlyFee": 9.99,
                    "currency": "USD",
                    "description": "$9.99/month for faster GPUs and longer runtimes"
                },
                {
                    "name": "Colab Pro+",
                    "monthlyFee": 49.99,
                    "currency": "USD",
                    "description": "$49.99/month for premium GPUs and background execution"
                }
            ],
            "websiteUrl": "https://colab.research.google.com/signup"
        }
    },
    {
        "name": "Replicate",
        "id": "replicate",
        "logo": "/ai-providers/replicate.svg",
        "isConfigured": False,
        "selectedModel": "stability-ai/sdxl",
        "maxTokens": 1000,
        "temperature": 0.7,
        "isActive": True,
        "user_id": "1",
        "pricing": {
            "tier": "freemium",
            "freeQuota": {
                "description": "Free tier with limited usage. Pay-per-use for additional requests"
            },
            "paidPlans": [
                {
                    "name": "Pay-per-use",
                    "pricePerRequest": 0.0023,
                    "currency": "USD",
                    "description": "Starting at $0.0023 per prediction"
                }
            ],
            "websiteUrl": "https://replicate.com/pricing"
        }
    },
    
    # PAID PROVIDERS
    {
        "name": "OpenAI",
        "id": "openai",
        "logo": "/ai-providers/openai.svg",
        "isConfigured": False,
        "maxTokens": 4096,
        "temperature": 0.7,
        "isActive": True,
        "user_id": "1",
        "pricing": {
            "tier": "paid",
            "paidPlans": [
                {
                    "name": "GPT-4o",
                    "pricePerToken": 0.000005,
                    "currency": "USD",
                    "description": "$5 per 1M input tokens, $15 per 1M output tokens"
                },
                {
                    "name": "GPT-4 Turbo",
                    "pricePerToken": 0.00001,
                    "currency": "USD",
                    "description": "$10 per 1M input tokens, $30 per 1M output tokens"
                },
                {
                    "name": "DALL-E 3",
                    "pricePerRequest": 0.04,
                    "currency": "USD",
                    "description": "$0.04 per image (1024×1024)"
                }
            ],
            "websiteUrl": "https://openai.com/pricing"
        }
    },
    {
        "name": "Anthropic Claude",
        "id": "anthropic",
        "logo": "/ai-providers/anthropic.svg",
        "isConfigured": False,
        "maxTokens": 4096,
        "temperature": 0.7,
        "isActive": True,
        "user_id": "1",
        "pricing": {
            "tier": "paid",
            "paidPlans": [
                {
                    "name": "Claude 3 Haiku",
                    "pricePerToken": 0.00000025,
                    "currency": "USD",
                    "description": "$0.25 per 1M input tokens, $1.25 per 1M output tokens"
                },
                {
                    "name": "Claude 3 Sonnet",
                    "pricePerToken": 0.000003,
                    "currency": "USD",
                    "description": "$3 per 1M input tokens, $15 per 1M output tokens"
                },
                {
                    "name": "Claude 3 Opus",
                    "pricePerToken": 0.000015,
                    "currency": "USD",
                    "description": "$15 per 1M input tokens, $75 per 1M output tokens"
                }
            ],
            "websiteUrl": "https://www.anthropic.com/pricing"
        }
    },
    {
        "name": "Stability AI",
        "id": "stability",
        "logo": "/ai-providers/stability.svg",
        "isConfigured": False,
        "selectedModel": "stable-diffusion-xl-1024-v1-0",
        "maxTokens": 1000,
        "temperature": 0.7,
        "isActive": True,
        "user_id": "1",
        "pricing": {
            "tier": "paid",
            "paidPlans": [
                {
                    "name": "Starter",
                    "pricePerRequest": 0.04,
                    "currency": "USD",
                    "description": "$0.04 per image generation"
                },
                {
                    "name": "Professional",
                    "monthlyFee": 20,
                    "currency": "USD",
                    "description": "$20/month for 3,000 images"
                },
                {
                    "name": "Enterprise",
                    "monthlyFee": 100,
                    "currency": "USD",
                    "description": "$100/month for 15,000 images + priority support"
                }
            ],
            "websiteUrl": "https://stability.ai/pricing"
        }
    },
    {
        "name": "Midjourney",
        "id": "midjourney",
        "logo": "/ai-providers/midjourney.svg",
        "isConfigured": False,
        "selectedModel": "midjourney-v6",
        "maxTokens": 1000,
        "temperature": 0.7,
        "isActive": True,
        "user_id": "1",
        "pricing": {
            "tier": "paid",
            "paidPlans": [
                {
                    "name": "Basic",
                    "monthlyFee": 10,
                    "currency": "USD",
                    "description": "$10/month for ~200 generations"
                },
                {
                    "name": "Standard",
                    "monthlyFee": 30,
                    "currency": "USD",
                    "description": "$30/month for ~900 generations"
                },
                {
                    "name": "Pro",
                    "monthlyFee": 60,
                    "currency": "USD",
                    "description": "$60/month for ~1800 generations + stealth mode"
                }
            ],
            "websiteUrl": "https://docs.midjourney.com/docs/plans"
        }
    }
]

@router.get("", response_model=List[AIProviderModel])
async def get_user_ai_providers(request: Request):
    """Get all AI providers configured for the current user"""
    user_id = get_current_user_id()
    logger.debug(f"Getting AI providers for user_id: {user_id}")
    
    # Fall back to mock data if there's an issue
    providers = []
    
    try:
        # Try to get from database if it exists
        if hasattr(request.app, "mongodb") and hasattr(request.app.mongodb, "ai_providers"):
            logger.debug("Attempting to query MongoDB collection")
            providers_collection = request.app.mongodb.ai_providers
            try:
                providers = await providers_collection.find({"user_id": user_id}).to_list(100)
                logger.debug(f"Successfully retrieved {len(providers)} providers from database")
            except Exception as db_err:
                logger.error(f"Database query error: {db_err}")
                # Fall back to mock data
                providers = list(MOCK_PROVIDERS)
        else:
            logger.warning("MongoDB collection not available, using mock data")
            providers = list(MOCK_PROVIDERS)
            
        # Don't return API keys in the list view
        for provider in providers:
            if "apiKey" in provider:
                provider["apiKey"] = "••••••••••••••••"
            # Ensure ID is a string
            provider["id"] = str(provider["id"])
            # Remove MongoDB _id
            if "_id" in provider:
                del provider["_id"]
        
        return providers
    except Exception as e:
        # If there's an error or no database, return mock data
        logger.error(f"Error retrieving AI providers: {e}")
        return MOCK_PROVIDERS

@router.get("/{provider_id}", response_model=AIProviderModel)
async def get_ai_provider(provider_id: str, request: Request):
    """Get a specific AI provider by ID"""
    user_id = get_current_user_id()
    try:
        # Try to get from database
        providers_collection = request.app.mongodb.ai_providers
        provider = await providers_collection.find_one({
            "id": provider_id,
            "user_id": user_id
        })
        
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        # Mask the API key
        if "apiKey" in provider:
            provider["apiKey"] = "••••••••••••••••"
        
        # Remove MongoDB _id
        if "_id" in provider:
            del provider["_id"]
            
        return provider
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("", response_model=AIProviderModel)
async def create_ai_provider(provider: AIProviderModel, request: Request):
    """Create a new AI provider configuration"""
    user_id = get_current_user_id()
    logger.debug(f"Creating AI provider {provider.id} for user: {user_id}")
    
    try:
        # Create a provider dictionary
        provider_dict = {**provider.dict(), "user_id": user_id}
        
        # Try to use the database if it's available
        if hasattr(request.app, "mongodb") and hasattr(request.app.mongodb, "ai_providers"):
            logger.debug("Using database to create provider")
            providers_collection = request.app.mongodb.ai_providers
            
            try:
                # Check if provider already exists
                existing = await providers_collection.find_one({
                    "id": provider.id,
                    "user_id": user_id
                })
                
                if existing:
                    logger.warning(f"Provider with ID {provider.id} already exists")
                    raise HTTPException(status_code=400, detail="Provider with this ID already exists")
                
                # Insert into database
                await providers_collection.insert_one(provider_dict)
                logger.debug(f"Successfully created provider {provider.id}")
            except Exception as db_err:
                if isinstance(db_err, HTTPException):
                    raise db_err
                logger.error(f"Database error: {db_err}")
                # Just return the provider as if it was created
        else:
            logger.warning("MongoDB collection not available, using mock operation")
            # No database, simulate success
        
        # Return the created provider (without the API key for security)
        response = provider_dict.copy()
        if "apiKey" in response:
            response["apiKey"] = "••••••••••••••••"
        
        # Remove MongoDB _id
        if "_id" in response:
            del response["_id"]
            
        return response
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error creating AI provider: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/{provider_id}", response_model=AIProviderModel)
async def update_ai_provider(provider_id: str, request: Request, updates: Dict[str, Any] = Body(...)):
    """Update an existing AI provider configuration"""
    user_id = get_current_user_id()
    try:
        # Check if provider exists
        providers_collection = request.app.mongodb.ai_providers
        provider = await providers_collection.find_one({
            "id": provider_id,
            "user_id": user_id
        })
        
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        # Update the provider
        await providers_collection.update_one(
            {"id": provider_id, "user_id": user_id},
            {"$set": updates}
        )
        
        # Get the updated provider
        updated_provider = await providers_collection.find_one({
            "id": provider_id,
            "user_id": user_id
        })
        
        # Mask the API key
        if "apiKey" in updated_provider:
            updated_provider["apiKey"] = "••••••••••••••••"
        
        # Remove MongoDB _id
        if "_id" in updated_provider:
            del updated_provider["_id"]
            
        return updated_provider
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/{provider_id}")
async def delete_ai_provider(provider_id: str, request: Request):
    """Delete an AI provider configuration"""
    user_id = get_current_user_id()
    try:
        # Delete from database
        providers_collection = request.app.mongodb.ai_providers
        result = await providers_collection.delete_one({
            "id": provider_id,
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        return {"success": True}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/validate")
async def validate_api_key(validation: ValidationRequest):
    """Validate an API key for a provider"""
    # This is a mock implementation
    # In a real app, you would call the provider's API to validate the key
    
    # Simulate validation success for most keys, but fail for specific test cases
    if validation.apiKey == "invalid_key_test":
        return {"valid": False, "message": "Invalid API key"}
    
    if validation.apiKey == "connection_error_test":
        raise HTTPException(status_code=500, detail="Connection error")
    
    # For stability.ai, check if key starts with "sk-" as a simple validation
    if validation.providerId == "stability" and not validation.apiKey.startswith("sk-"):
        return {"valid": False, "message": "Invalid Stability API key format. Should start with 'sk-'"}
    
    # For HuggingFace, check if key starts with "hf_" as a simple validation
    if validation.providerId == "huggingface" and not validation.apiKey.startswith("hf_"):
        return {"valid": False, "message": "Invalid Hugging Face API key format. Should start with 'hf_'"}
        
    return {"valid": True, "message": "API key validated successfully"}

@router.get("/{provider_id}/options")
async def get_provider_options(provider_id: str):
    """Get available options for a provider (models, sizes, etc)"""
    # Mock implementation returning different models based on provider ID
    provider_models = {
        "stability": [
            "stable-diffusion-xl-1024-v1-0",
            "stable-diffusion-xl-1024-v0-9",
            "stable-diffusion-v1-5"
        ],
        "huggingface": [
            "runwayml/stable-diffusion-v1-5",
            "CompVis/stable-diffusion-v1-4",
            "stabilityai/stable-diffusion-2-1"
        ],
        "replicate": [
            "stability-ai/sdxl",
            "stability-ai/stable-diffusion",
            "cjwbw/dreamshaper"
        ]
    }
    
    # Return default models if provider not found
    default_models = ["default-model-1", "default-model-2"]
    models = provider_models.get(provider_id, default_models)
    
    return {"models": models}
