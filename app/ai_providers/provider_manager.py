"""
AI Provider Manager for Marketing Image Generation
Supports multiple real AI providers: OpenAI DALL-E, Stability AI, Replicate, etc.
"""
import os
import asyncio
import aiohttp
import base64
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

from .errors import AIErrorClassifier, AIProviderError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Provider Registry - Maps provider IDs to their implementation classes
# Add new providers here when implementing new provider integrations
PROVIDER_REGISTRY = {}  # Will be populated after class definitions

class ProviderStatus(Enum):
    CONFIGURED = "configured"
    NOT_CONFIGURED = "not_configured"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"

@dataclass
class ImageGenerationRequest:
    prompt: str
    size: str = "1024x1024"
    style: str = "photorealistic"
    quality: str = "standard"
    variations: int = 1
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    people_preference: str = "auto"  # Smart 4-mode system: "auto" | "include" | "exclude" | "minimal"
    creative_approach: str = "hybrid"  # Visual storytelling: "story_led" | "concept_led" | "hybrid"

@dataclass
class ImageGenerationResult:
    success: bool
    images: List[str]  # Base64 or URLs
    provider: str
    model: str
    metadata: Dict[str, Any]
    error: Optional[str] = None
    cost: Optional[float] = None
    error_details: Optional[Dict[str, Any]] = None  # Enriched error information

class AIProviderManager:
    """Manages multiple AI providers for image generation"""
    
    def __init__(self, database_client=None):
        self.providers = {}
        self.provider_configs = {}
        self.db = database_client
        self._load_provider_configs()
        self._initialize_providers()
    
    def _load_provider_configs(self):
        """
        Initialize provider configs dictionary
        Configs will be loaded from database via refresh_provider_configs()
        Environment variables are used ONLY as fallback if database is unavailable
        """
        # Start with empty configs - will be populated from database
        self.provider_configs = {}
        
        # Fallback templates with environment variables (only used if DB unavailable)
        self._env_fallback_configs = {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "model": "dall-e-3",
                "max_variations": 1,
                "supported_sizes": ["1024x1024", "1024x1792", "1792x1024"],
                "pricing": {"standard": 0.04, "hd": 0.08}
            },
            "stability": {
                "api_key": os.getenv("STABILITY_API_KEY"),
                "base_url": "https://api.stability.ai/v1",
                "model": "stable-diffusion-xl-1024-v1-0",
                "max_variations": 4,
                "supported_sizes": ["1024x1024", "1152x896", "896x1152", "1216x832", "832x1216"],
                "pricing": {"standard": 0.02}
            },
            "replicate": {
                "api_key": os.getenv("REPLICATE_API_TOKEN"),
                "base_url": "https://api.replicate.com/v1",
                "model": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                "max_variations": 4,
                "supported_sizes": ["1024x1024", "1152x896", "896x1152"],
                "pricing": {"standard": 0.0025}
            },
            "huggingface": {
                "api_key": os.getenv("HUGGINGFACE_API_KEY"),
                "base_url": "https://api-inference.huggingface.co/models",
                "model": "runwayml/stable-diffusion-v1-5",
                "max_variations": 1,
                "supported_sizes": ["512x512", "768x768"],
                "pricing": {"free": 0.0}
            }
        }
        
        logger.info("Provider configuration system initialized (will load from database)")
    
    async def _load_provider_from_database(self, provider_id: str, user_id: str = "1") -> Optional[Dict[str, Any]]:
        """
        Load provider configuration from database
        This is the PRIMARY method for getting provider configs
        """
        if self.db is None:
            logger.warning(f"No database connection - using environment fallback for {provider_id}")
            return None
            
        try:
            providers_collection = self.db.ai_providers
            provider_data = await providers_collection.find_one({
                "id": provider_id,
                "user_id": user_id
            })
            
            if provider_data:
                # Map database fields to internal config structure
                config = {
                    "api_key": provider_data.get("apiKey") or provider_data.get("api_key"),
                    "model": provider_data.get("selectedModel") or provider_data.get("model"),
                    "base_url": provider_data.get("baseUrl") or provider_data.get("base_url"),
                    "max_tokens": provider_data.get("maxTokens") or provider_data.get("max_tokens"),
                    "temperature": provider_data.get("temperature", 0.7),
                    "configured": bool(provider_data.get("apiKey") or provider_data.get("api_key")),
                }
                
                # Add fallback defaults from environment templates if needed
                if provider_id in self._env_fallback_configs:
                    fallback = self._env_fallback_configs[provider_id]
                    config.setdefault("base_url", fallback.get("base_url"))
                    config.setdefault("max_variations", fallback.get("max_variations"))
                    config.setdefault("supported_sizes", fallback.get("supported_sizes"))
                    config.setdefault("pricing", fallback.get("pricing"))
                    # Only use environment API key if database has none
                    if not config["api_key"]:
                        config["api_key"] = fallback.get("api_key")
                
                if config["api_key"]:
                    logger.info(f"✅ Loaded configuration for '{provider_id}' from database")
                else:
                    logger.debug(f"⚠️  Provider '{provider_id}' found in database but has no API key")
                
                return config
            else:
                logger.debug(f"Provider '{provider_id}' not found in database")
                return None
                
        except Exception as e:
            logger.error(f"Error loading provider '{provider_id}' from database: {e}")
            return None
    
    async def _load_all_configs_from_database(self, user_id: str = "1"):
        """
        Load ALL provider configurations from database
        This replaces hardcoded configs with database-driven configs
        """
        if self.db is None:
            logger.warning("No database connection - using environment fallback configs")
            # Use environment fallback
            self.provider_configs = self._env_fallback_configs.copy()
            return
            
        try:
            self.provider_configs = {}
            providers_collection = self.db.ai_providers
            
            # Load all providers for this user
            db_providers = await providers_collection.find({"user_id": user_id}).to_list(1000)
            
            logger.info(f"Found {len(db_providers)} providers in database for user '{user_id}'")
            
            for provider_data in db_providers:
                provider_id = provider_data["id"]
                
                # Map database fields to internal config structure
                config = {
                    "api_key": provider_data.get("apiKey") or provider_data.get("api_key"),
                    "model": provider_data.get("selectedModel") or provider_data.get("model"),
                    "base_url": provider_data.get("baseUrl") or provider_data.get("base_url"),
                    "max_tokens": provider_data.get("maxTokens") or provider_data.get("max_tokens"),
                    "temperature": provider_data.get("temperature", 0.7),
                }
                
                # Add defaults from environment templates if available
                if provider_id in self._env_fallback_configs:
                    fallback = self._env_fallback_configs[provider_id]
                    # Use fallback for missing or None values (not just missing keys)
                    if not config.get("base_url"):
                        config["base_url"] = fallback.get("base_url")
                        logger.debug(f"  🔄 '{provider_id}' - using fallback base_url: {config['base_url']}")
                    config.setdefault("max_variations", fallback.get("max_variations"))
                    config.setdefault("supported_sizes", fallback.get("supported_sizes"))
                    config.setdefault("pricing", fallback.get("pricing"))
                    # Use environment API key as fallback if database has none
                    if not config["api_key"]:
                        config["api_key"] = fallback.get("api_key")
                        if config["api_key"]:
                            logger.debug(f"  🔄 '{provider_id}' - using fallback API key from environment")
                
                self.provider_configs[provider_id] = config
                
                if config.get("api_key"):
                    logger.debug(f"  ✅ '{provider_id}' - configured with API key")
                else:
                    logger.debug(f"  ⚪ '{provider_id}' - no API key")
            
            logger.info(f"✅ Loaded {len(self.provider_configs)} provider configurations from database")
            
        except Exception as e:
            logger.error(f"Error loading providers from database: {e}")
            logger.warning("Falling back to environment variable configs")
            self.provider_configs = self._env_fallback_configs.copy()

    
    async def refresh_provider_configs(self, user_id: str = "1"):
        """
        Refresh ALL provider configurations from database
        This ensures we always have the latest API keys and settings
        """
        logger.info(f"♻️  Refreshing provider configurations from database for user '{user_id}'")
        
        # Load all configs from database
        await self._load_all_configs_from_database(user_id)
        
        # Reinitialize providers with new configs
        self._initialize_providers()
        
        configured_count = sum(1 for p in self.providers.values() if p.is_configured())
        logger.info(f"✅ Refresh complete: {configured_count}/{len(self.providers)} providers configured")
    
    def _initialize_providers(self):
        """
        Initialize providers based on registry and available configurations
        Only providers with registered classes and API keys will be initialized
        """
        self.providers = {}
        initialized_count = 0
        
        # Iterate through all configs (from database or fallback)
        for provider_id, config in self.provider_configs.items():
            # Check if provider has a registered implementation class
            if provider_id not in PROVIDER_REGISTRY:
                logger.debug(f"⚪ Provider '{provider_id}' not in registry (no implementation class) - skipping")
                continue
            
            # Check if provider has API key
            if not config.get("api_key"):
                logger.debug(f"⚪ Provider '{provider_id}' has no API key - skipping")
                continue
            
            # Initialize the provider with its registered class
            try:
                provider_class = PROVIDER_REGISTRY[provider_id]
                self.providers[provider_id] = provider_class(config)
                initialized_count += 1
                logger.info(f"✅ Initialized provider: '{provider_id}' ({provider_class.__name__})")
            except Exception as e:
                logger.error(f"❌ Failed to initialize provider '{provider_id}': {e}")
        
        # Always include the test provider (no API key needed)
        self.providers["free-test-provider"] = TestProvider()
        logger.info(f"✅ Initialized test provider: 'free-test-provider'")
        
        logger.info(f"🎯 Total providers initialized: {len(self.providers)} ({initialized_count} real + 1 test)")
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers (initialized and available in registry)"""
        status = {}
        
        # Add initialized providers (those currently running)
        for provider_id, provider in self.providers.items():
            status[provider_id] = {
                "name": provider.get_name(),
                "configured": provider.is_configured(),
                "available": provider.is_available(),
                "model": provider.get_model(),
                "max_variations": provider.get_max_variations(),
                "supported_sizes": provider.get_supported_sizes(),
                "features": provider.get_features(),
                "pricing": provider.get_pricing(),
                "status": provider.get_status().value
            }
        
        # Add registered providers that aren't initialized (for visibility)
        provider_display_names = {
            "openai": "OpenAI DALL-E",
            "stability": "Stability AI",
            "replicate": "Replicate",
            "huggingface": "HuggingFace"
        }
        
        for provider_id in PROVIDER_REGISTRY.keys():
            if provider_id not in status:
                config = self.provider_configs.get(provider_id, {})
                has_api_key = bool(config.get("api_key"))
                
                status[provider_id] = {
                    "name": provider_display_names.get(provider_id, provider_id.title()),
                    "configured": has_api_key,
                    "available": False,  # Not initialized, so not available
                    "model": config.get("model", "unknown"),
                    "max_variations": config.get("max_variations", 1),
                    "supported_sizes": config.get("supported_sizes", ["1024x1024"]),
                    "features": ["image_generation"],
                    "pricing": config.get("pricing", {}),
                    "status": ProviderStatus.NOT_CONFIGURED.value if not has_api_key else ProviderStatus.ERROR.value
                }
        
        return status
    
    async def generate_image(self, provider_id: str, request: ImageGenerationRequest) -> ImageGenerationResult:
        """Generate image using specified provider"""
        if provider_id not in self.providers:
            # Get available providers for error message
            available_providers = [p_id for p_id, p in self.providers.items() if p.is_available()]
            return ImageGenerationResult(
                success=False,
                images=[],
                provider=provider_id,
                model="unknown",
                metadata={},
                error=f"Provider '{provider_id}' not available",
                error_details={
                    "error_type": "provider_not_found",
                    "message": f"The AI provider '{provider_id}' is not initialized or not supported.",
                    "user_message": f"errors.ai.provider_not_available",
                    "provider": provider_id,
                    "available_providers": available_providers,
                    "suggested_actions": [
                        f"Switch to an available provider: {', '.join(available_providers)}" if available_providers else "Configure an AI provider in Settings"
                    ]
                }
            )
        
        provider = self.providers[provider_id]
        
        if not provider.is_available():
            return ImageGenerationResult(
                success=False,
                images=[],
                provider=provider_id,
                model=provider.get_model(),
                metadata={},
                error=f"Provider '{provider_id}' is not available or configured",
                error_details={
                    "error_type": "provider_not_configured",
                    "message": f"The provider '{provider_id}' is not properly configured.",
                    "user_message": "errors.ai.provider_not_configured",
                    "provider": provider_id,
                    "suggested_actions": [
                        "Check API keys in AI Provider settings",
                        "Verify base URL configuration",
                        "Test provider connection"
                    ]
                }
            )
        
        try:
            return await provider.generate_image(request)
        except Exception as e:
            logger.error(f"Error generating image with {provider_id}: {str(e)}")
            return ImageGenerationResult(
                success=False,
                images=[],
                provider=provider_id,
                model=provider.get_model(),
                metadata={},
                error=str(e)
            )
    
    async def generate_images_parallel(
        self, 
        provider_id: str, 
        request: ImageGenerationRequest,
        max_concurrent: int = None
    ) -> ImageGenerationResult:
        """
        Generate multiple images in parallel with rate limiting and error handling.
        
        Args:
            provider_id: ID of the AI provider to use
            request: Image generation request with variations count
            max_concurrent: Maximum concurrent requests (defaults based on provider)
        
        Returns:
            ImageGenerationResult with all successfully generated images
        """
        if request.variations <= 1:
            # For single image, use standard generation
            return await self.generate_image(provider_id, request)
        
        # Provider-specific concurrency limits to avoid rate limiting
        default_concurrency_limits = {
            "openai": 2,        # OpenAI: Conservative to avoid rate limits
            "stability": 3,     # Stability AI: Moderate concurrency
            "replicate": 3,     # Replicate: Moderate concurrency
            "huggingface": 5,   # HuggingFace: Higher tolerance
            "free-test-provider": 10  # Free test: No limits
        }
        
        # Determine concurrency limit
        if max_concurrent is None:
            max_concurrent = default_concurrency_limits.get(provider_id, 2)
        
        logger.info(
            f"Generating {request.variations} images in parallel with "
            f"max_concurrent={max_concurrent} for provider '{provider_id}'"
        )
        
        # Create individual requests for each variation
        single_requests = []
        for i in range(request.variations):
            single_request = ImageGenerationRequest(
                prompt=request.prompt,
                size=request.size,
                style=request.style,
                quality=request.quality,
                variations=1,  # Each task generates 1 image
                negative_prompt=request.negative_prompt,
                seed=request.seed + i if request.seed else None  # Vary seed for different results
            )
            single_requests.append(single_request)
        
        # Execute requests in batches to respect concurrency limits
        all_images = []
        all_errors = []
        total_cost = 0.0
        successful_count = 0
        
        # Process in batches
        for batch_start in range(0, len(single_requests), max_concurrent):
            batch_end = min(batch_start + max_concurrent, len(single_requests))
            batch = single_requests[batch_start:batch_end]
            
            logger.info(f"Processing batch {batch_start//max_concurrent + 1}: images {batch_start+1} to {batch_end}")
            
            # Execute batch in parallel
            tasks = [self.generate_image(provider_id, req) for req in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                image_num = batch_start + i + 1
                
                if isinstance(result, Exception):
                    error_msg = f"Image {image_num} failed with exception: {str(result)}"
                    logger.error(error_msg)
                    all_errors.append({
                        "image_num": image_num,
                        "error": str(result),
                        "error_type": "exception"
                    })
                elif result.success:
                    all_images.extend(result.images)
                    total_cost += result.cost or 0.0
                    successful_count += 1
                    logger.info(f"Image {image_num} generated successfully")
                else:
                    error_msg = f"Image {image_num} failed: {result.error}"
                    logger.error(error_msg)
                    all_errors.append({
                        "image_num": image_num,
                        "error": result.error,
                        "error_type": result.error_details.get("error_type") if result.error_details else "unknown",
                        "error_details": result.error_details
                    })
            
            # Small delay between batches to avoid rate limiting
            if batch_end < len(single_requests):
                await asyncio.sleep(0.5)
        
        # Determine overall success
        success = successful_count > 0
        
        # Get provider info for metadata
        provider = self.providers.get(provider_id)
        model = provider.get_model() if provider else "unknown"
        
        # Build response
        if success:
            metadata = {
                "total_requested": request.variations,
                "total_generated": successful_count,
                "total_failed": len(all_errors),
                "errors": all_errors if all_errors else None,
                "parallel_execution": True,
                "max_concurrent": max_concurrent
            }
            
            if all_errors:
                logger.warning(
                    f"Partial success: {successful_count}/{request.variations} images generated, "
                    f"{len(all_errors)} failed"
                )
            else:
                logger.info(f"All {successful_count} images generated successfully")
            
            return ImageGenerationResult(
                success=True,
                images=all_images,
                provider=provider_id,
                model=model,
                metadata=metadata,
                cost=total_cost
            )
        else:
            # Complete failure
            logger.error(f"All {request.variations} image generation attempts failed")
            
            # Use first error for main error message
            first_error = all_errors[0] if all_errors else {"error": "Unknown error", "error_type": "unknown"}
            
            return ImageGenerationResult(
                success=False,
                images=[],
                provider=provider_id,
                model=model,
                metadata={
                    "total_requested": request.variations,
                    "total_failed": len(all_errors),
                    "errors": all_errors
                },
                error=first_error.get("error", "All image generation attempts failed"),
                error_details=first_error.get("error_details")
            )
    
    def get_recommended_provider(self, features: List[str] = None) -> str:
        """Get recommended provider based on features and availability"""
        # Priority order based on quality and reliability
        priority_order = ["openai", "stability", "replicate", "huggingface", "free-test-provider"]
        
        for provider_id in priority_order:
            if provider_id in self.providers and self.providers[provider_id].is_available():
                return provider_id
        
        return "free-test-provider"  # Fallback

class BaseProvider:
    """Base class for AI providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
        self.status = ProviderStatus.NOT_CONFIGURED
    
    def get_name(self) -> str:
        return self.name
    
    def get_model(self) -> str:
        return self.config.get("model", "unknown")
    
    def get_max_variations(self) -> int:
        return self.config.get("max_variations", 1)
    
    def get_supported_sizes(self) -> List[str]:
        return self.config.get("supported_sizes", ["1024x1024"])
    
    def get_features(self) -> List[str]:
        return ["image_generation"]
    
    def get_pricing(self) -> Dict[str, Any]:
        return self.config.get("pricing", {})
    
    def get_status(self) -> ProviderStatus:
        return self.status
    
    def is_configured(self) -> bool:
        return self.config.get("api_key") is not None
    
    def is_available(self) -> bool:
        return self.is_configured() and self.status != ProviderStatus.ERROR
    
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """Generate image - to be implemented by subclasses"""
        raise NotImplementedError

class OpenAIProvider(BaseProvider):
    """OpenAI DALL-E provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "OpenAI DALL-E"
        if self.is_configured():
            self.status = ProviderStatus.CONFIGURED
    
    def is_configured(self) -> bool:
        """Check if provider is configured with API key AND model"""
        has_api_key = self.config.get("api_key") is not None
        has_model = self.config.get("model") is not None and self.config.get("model") != ""
        return has_api_key and has_model
    
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """Generate image using OpenAI DALL-E"""
        
        # Validate model is configured
        if not self.config.get("model"):
            ai_error = AIErrorClassifier.classify_provider_error(
                provider="openai",
                status_code=None,
                error_data={"error": {"message": "Model not configured"}},
                exception=ValueError("Model not selected for OpenAI provider")
            )
            # Override error details to be more user-friendly
            ai_error.error_type = "configuration_error"
            ai_error.message = "OpenAI model not selected"
            ai_error.user_message = "Please select a model for the OpenAI provider in AI Provider settings"
            ai_error.suggested_actions = [
                "Go to AI Providers settings",
                "Select a model for OpenAI (e.g., dall-e-3)",
                "Save the configuration and try again"
            ]
            
            return ImageGenerationResult(
                success=False,
                images=[],
                provider="openai",
                model="none",
                metadata={},
                error=ai_error.message,
                error_details=ai_error.to_dict()
            )
        
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        
        # DALL-E 3 only supports 1 image at a time
        num_images = min(request.variations, 1)
        
        # Apply smart people preference modification (4-mode system)
        modified_prompt = request.prompt
        people_pref = request.people_preference or "auto"
        
        if people_pref == "exclude":
            # Strong exclusion - product-only imagery
            modified_prompt = f"{request.prompt}\n\nCRITICAL REQUIREMENT: Absolutely NO people, NO humans, NO faces, NO body parts. Focus exclusively on products, objects, abstract elements, or scenery. This is a product-only visual."
        elif people_pref == "include":
            # Reinforce people presence (only if not already in prompt)
            if not any(keyword in request.prompt.lower() for keyword in ["people", "person", "human", "customer", "user", "family", "lifestyle"]):
                modified_prompt = f"{request.prompt}\n\nIMPORTANT: Include diverse, authentic people in natural settings. Show real human moments and connections."
        elif people_pref == "minimal":
            # Product-focused with subtle human context
            modified_prompt = f"{request.prompt}\n\nGUIDELINE: Prioritize product showcase. If people appear, they should be minimal, in background, or partial (hands holding product). Main focus must be on the product/object."
        # "auto" mode: no modification - let enrichments guide naturally
        
        # Apply creative approach enrichment (storytelling method)
        creative_approach = request.creative_approach or "hybrid"
        
        if creative_approach == "story_led":
            # Story-Led: Narrative scenes with people
            modified_prompt = f"{modified_prompt}\n\n[STORYTELLING: Story-Led] Create narrative scenes showing people in authentic situations. Tell visual stories through human experiences, emotions, and natural interactions. Focus on documentary-style, candid moments."
        elif creative_approach == "concept_led":
            # Concept-Led: Clear visual concepts, symbols
            modified_prompt = f"{modified_prompt}\n\n[STORYTELLING: Concept-Led] Focus on clear visual concepts, symbolic imagery, and informative presentation. Emphasize clarity, professionalism, and direct communication through visual metaphors and clean compositions."
        # "hybrid" mode: no modification - let context decide
        
        payload = {
            "model": self.config["model"],
            "prompt": modified_prompt,
            "n": num_images,
            "size": request.size if request.size in self.get_supported_sizes() else "1024x1024",
            "quality": request.quality if request.quality in ["standard", "hd"] else "standard",
            "response_format": "url"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config['base_url']}/images/generations",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        images = [img["url"] for img in data["data"]]
                        
                        # If we need more variations, make additional calls
                        if request.variations > 1:
                            for _ in range(min(request.variations - 1, 3)):  # Max 4 total
                                try:
                                    async with session.post(
                                        f"{self.config['base_url']}/images/generations",
                                        headers=headers,
                                        json=payload,
                                        timeout=aiohttp.ClientTimeout(total=120)
                                    ) as extra_response:
                                        if extra_response.status == 200:
                                            extra_data = await extra_response.json()
                                            images.extend([img["url"] for img in extra_data["data"]])
                                except Exception as e:
                                    logger.warning(f"Failed to generate additional variation: {e}")
                                    break
                        
                        # Calculate cost (handle case where pricing is None or missing)
                        pricing = self.config.get("pricing") or {}
                        cost = len(images) * pricing.get(request.quality, 0.04)
                        
                        return ImageGenerationResult(
                            success=True,
                            images=images,
                            provider="openai",
                            model=self.config["model"],
                            metadata={
                                "size": payload["size"],
                                "quality": payload["quality"],
                                "total_images": len(images),
                                "cost_usd": cost
                            },
                            cost=cost
                        )
                    else:
                        # Error response - use enriched error classification
                        error_data = await response.json()
                        ai_error = AIErrorClassifier.classify_provider_error(
                            provider="openai",
                            status_code=response.status,
                            error_data=error_data
                        )
                        
                        logger.error(f"OpenAI error [{ai_error.correlation_id}]: {ai_error.message}")
                        
                        return ImageGenerationResult(
                            success=False,
                            images=[],
                            provider="openai",
                            model=self.config["model"],
                            metadata={},
                            error=ai_error.message,
                            error_details=ai_error.to_dict()
                        )
        except asyncio.TimeoutError as e:
            ai_error = AIErrorClassifier.classify_provider_error(
                provider="openai",
                status_code=None,
                error_data={},
                exception=e
            )
            logger.error(f"OpenAI timeout [{ai_error.correlation_id}]: {ai_error.message}")
            return ImageGenerationResult(
                success=False,
                images=[],
                provider="openai",
                model=self.config["model"],
                metadata={},
                error=ai_error.message,
                error_details=ai_error.to_dict()
            )
        except Exception as e:
            ai_error = AIErrorClassifier.classify_provider_error(
                provider="openai",
                status_code=None,
                error_data={},
                exception=e
            )
            logger.error(f"OpenAI exception [{ai_error.correlation_id}]: {ai_error.message}")
            return ImageGenerationResult(
                success=False,
                images=[],
                provider="openai",
                model=self.config["model"],
                metadata={},
                error=ai_error.message,
                error_details=ai_error.to_dict()
            )

class StabilityAIProvider(BaseProvider):
    """Stability AI provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "Stability AI"
        if self.is_configured():
            self.status = ProviderStatus.CONFIGURED
    
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """Generate image using Stability AI"""
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Parse size
        width, height = map(int, request.size.split('x'))
        
        # Apply smart people preference modification (4-mode system)
        modified_prompt = request.prompt
        negative_prompt_additions = []
        people_pref = request.people_preference or "auto"
        
        if people_pref == "exclude":
            # Strong exclusion - product-only imagery
            modified_prompt = f"{request.prompt}. CRITICAL: Absolutely NO people, NO humans, NO faces, NO body parts."
            negative_prompt_additions.append("people, humans, persons, faces, portraits, crowds, human figures, body parts, hands, feet, silhouettes")
        elif people_pref == "include":
            # Reinforce people presence
            if not any(keyword in request.prompt.lower() for keyword in ["people", "person", "human", "customer", "user", "family", "lifestyle"]):
                modified_prompt = f"{request.prompt}. Include diverse, authentic people in natural settings."
        elif people_pref == "minimal":
            # Product-focused with subtle human context
            modified_prompt = f"{request.prompt}. Product-focused composition. People minimal or in background only."
            negative_prompt_additions.append("crowds, group photos, portrait mode, face close-ups, human-centric composition")
        # "auto" mode: no modification
        
        # Apply creative approach enrichment (storytelling method)
        creative_approach = request.creative_approach or "hybrid"
        
        if creative_approach == "story_led":
            # Story-Led: Narrative scenes with people
            modified_prompt = f"{modified_prompt}. [STORYTELLING: Story-Led] Narrative scene showing people in authentic situations, documentary-style, candid moments."
        elif creative_approach == "concept_led":
            # Concept-Led: Clear visual concepts
            modified_prompt = f"{modified_prompt}. [STORYTELLING: Concept-Led] Clear visual concept, symbolic imagery, professional presentation, clean composition."
        # "hybrid" mode: no modification
        
        payload = {
            "text_prompts": [
                {"text": modified_prompt, "weight": 1.0}
            ],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": min(request.variations, self.get_max_variations()),
            "steps": 30,
        }
        
        # Build negative prompts
        if request.negative_prompt:
            payload["text_prompts"].append({"text": request.negative_prompt, "weight": -1.0})
        
        # Add people-related negative prompts based on preference
        if negative_prompt_additions:
            payload["text_prompts"].append({
                "text": ", ".join(negative_prompt_additions),
                "weight": -1.0
            })
        
        if request.seed:
            payload["seed"] = request.seed
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config['base_url']}/generation/{self.config['model']}/text-to-image",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        images = []
                        
                        for artifact in data["artifacts"]:
                            if artifact["finishReason"] == "SUCCESS":
                                # Convert base64 to data URL
                                image_data = f"data:image/png;base64,{artifact['base64']}"
                                images.append(image_data)
                        
                        # Calculate cost (handle case where pricing is None or missing)
                        pricing = self.config.get("pricing") or {}
                        cost = len(images) * pricing.get("standard", 0.02)
                        
                        return ImageGenerationResult(
                            success=True,
                            images=images,
                            provider="stability",
                            model=self.config["model"],
                            metadata={
                                "size": request.size,
                                "steps": payload["steps"],
                                "cfg_scale": payload["cfg_scale"],
                                "total_images": len(images),
                                "cost_usd": cost
                            },
                            cost=cost
                        )
                    else:
                        error_data = await response.json()
                        return ImageGenerationResult(
                            success=False,
                            images=[],
                            provider="stability",
                            model=self.config["model"],
                            metadata={},
                            error=f"Stability AI error: {error_data.get('message', 'Unknown error')}"
                        )
        except Exception as e:
            return ImageGenerationResult(
                success=False,
                images=[],
                provider="stability",
                model=self.config["model"],
                metadata={},
                error=f"Request failed: {str(e)}"
            )

class ReplicateProvider(BaseProvider):
    """Replicate provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "Replicate"
        if self.is_configured():
            self.status = ProviderStatus.CONFIGURED
    
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """Generate image using Replicate"""
        headers = {
            "Authorization": f"Token {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        
        width, height = map(int, request.size.split('x'))
        
        # Apply smart people preference modification (4-mode system)
        modified_prompt = request.prompt
        negative_prompt_additions = []
        people_pref = request.people_preference or "auto"
        
        if people_pref == "exclude":
            # Strong exclusion - product-only imagery
            modified_prompt = f"{request.prompt}. CRITICAL: Absolutely NO people, NO humans, NO faces, NO body parts."
            negative_prompt_additions.append("people, humans, persons, faces, portraits, crowds, human figures, body parts, hands, feet, silhouettes")
        elif people_pref == "include":
            # Reinforce people presence
            if not any(keyword in request.prompt.lower() for keyword in ["people", "person", "human", "customer", "user", "family", "lifestyle"]):
                modified_prompt = f"{request.prompt}. Include diverse, authentic people in natural settings."
        elif people_pref == "minimal":
            # Product-focused with subtle human context
            modified_prompt = f"{request.prompt}. Product-focused composition. People minimal or in background only."
            negative_prompt_additions.append("crowds, group photos, portrait mode, face close-ups, human-centric composition")
        # "auto" mode: no modification
        
        # Apply creative approach enrichment (storytelling method)
        creative_approach = request.creative_approach or "hybrid"
        
        if creative_approach == "story_led":
            # Story-Led: Narrative scenes with people
            modified_prompt = f"{modified_prompt}. [STORYTELLING: Story-Led] Narrative scene showing people in authentic situations, documentary-style, candid moments."
        elif creative_approach == "concept_led":
            # Concept-Led: Clear visual concepts
            modified_prompt = f"{modified_prompt}. [STORYTELLING: Concept-Led] Clear visual concept, symbolic imagery, professional presentation, clean composition."
        # "hybrid" mode: no modification
        
        payload = {
            "version": self.config["model"].split(":")[-1],
            "input": {
                "prompt": modified_prompt,
                "width": width,
                "height": height,
                "num_outputs": min(request.variations, self.get_max_variations()),
                "guidance_scale": 7.5,
                "num_inference_steps": 30
            }
        }
        
        # Build negative prompt
        negative_prompts = []
        if request.negative_prompt:
            negative_prompts.append(request.negative_prompt)
        if negative_prompt_additions:
            negative_prompts.extend(negative_prompt_additions)
        
        if negative_prompts:
            payload["input"]["negative_prompt"] = ", ".join(negative_prompts)
        
        if request.seed:
            payload["input"]["seed"] = request.seed
        
        try:
            async with aiohttp.ClientSession() as session:
                # Create prediction
                async with session.post(
                    f"{self.config['base_url']}/predictions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 201:
                        prediction = await response.json()
                        prediction_id = prediction["id"]
                        
                        # Poll for completion
                        max_attempts = 30
                        for attempt in range(max_attempts):
                            await asyncio.sleep(2)
                            
                            async with session.get(
                                f"{self.config['base_url']}/predictions/{prediction_id}",
                                headers=headers
                            ) as status_response:
                                if status_response.status == 200:
                                    status_data = await status_response.json()
                                    
                                    if status_data["status"] == "succeeded":
                                        images = status_data["output"] or []
                                        # Calculate cost (handle case where pricing is None or missing)
                                        pricing = self.config.get("pricing") or {}
                                        cost = len(images) * pricing.get("standard", 0.01)
                                        
                                        return ImageGenerationResult(
                                            success=True,
                                            images=images,
                                            provider="replicate",
                                            model=self.config["model"],
                                            metadata={
                                                "size": request.size,
                                                "total_images": len(images),
                                                "cost_usd": cost,
                                                "prediction_id": prediction_id
                                            },
                                            cost=cost
                                        )
                                    elif status_data["status"] == "failed":
                                        return ImageGenerationResult(
                                            success=False,
                                            images=[],
                                            provider="replicate",
                                            model=self.config["model"],
                                            metadata={},
                                            error=f"Prediction failed: {status_data.get('error', 'Unknown error')}"
                                        )
                        
                        return ImageGenerationResult(
                            success=False,
                            images=[],
                            provider="replicate",
                            model=self.config["model"],
                            metadata={},
                            error="Prediction timed out"
                        )
                    else:
                        error_data = await response.json()
                        return ImageGenerationResult(
                            success=False,
                            images=[],
                            provider="replicate",
                            model=self.config["model"],
                            metadata={},
                            error=f"Replicate error: {error_data.get('detail', 'Unknown error')}"
                        )
        except Exception as e:
            return ImageGenerationResult(
                success=False,
                images=[],
                provider="replicate",
                model=self.config["model"],
                metadata={},
                error=f"Request failed: {str(e)}"
            )

class HuggingFaceProvider(BaseProvider):
    """Hugging Face provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "Hugging Face"
        if self.is_configured():
            self.status = ProviderStatus.CONFIGURED
    
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """Generate image using Hugging Face"""
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": request.prompt,
            "parameters": {
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config['base_url']}/{self.config['model']}",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                        image_b64 = base64.b64encode(image_bytes).decode()
                        image_data = f"data:image/jpeg;base64,{image_b64}"
                        
                        return ImageGenerationResult(
                            success=True,
                            images=[image_data],
                            provider="huggingface",
                            model=self.config["model"],
                            metadata={
                                "size": "512x512",  # Default HF size
                                "total_images": 1,
                                "cost_usd": 0.0
                            },
                            cost=0.0
                        )
                    else:
                        error_text = await response.text()
                        return ImageGenerationResult(
                            success=False,
                            images=[],
                            provider="huggingface",
                            model=self.config["model"],
                            metadata={},
                            error=f"Hugging Face error: {error_text}"
                        )
        except Exception as e:
            return ImageGenerationResult(
                success=False,
                images=[],
                provider="huggingface",
                model=self.config["model"],
                metadata={},
                error=f"Request failed: {str(e)}"
            )

class TestProvider(BaseProvider):
    """Test provider for fallback"""
    
    def __init__(self):
        super().__init__({"model": "test-svg-generator"})
        self.name = "Test Provider"
        self.status = ProviderStatus.CONFIGURED
    
    def is_configured(self) -> bool:
        return True
    
    def is_available(self) -> bool:
        return True
    
    def get_max_variations(self) -> int:
        return 5
    
    def get_pricing(self) -> Dict[str, Any]:
        return {"free": 0.0}
    
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """Generate test SVG images"""
        images = []
        width, height = map(int, request.size.split('x'))
        
        # Default company context for test provider
        company = {
            "name": "Test Company",
            "brand_colors": ["#2563EB", "#DC2626", "#059669", "#7C3AED"],
            "industry": "General Business",
            "style": "professional, modern"
        }
        
        for i in range(request.variations):
            variation_id = i if request.variations > 1 else 0
            # Generate a simple SVG for testing
            svg_content = self._generate_test_svg(width, height, company, request.prompt, variation_id)
            # Convert to data URL
            image_url = f"data:image/svg+xml;base64,{base64.b64encode(svg_content.encode()).decode()}"
            images.append(image_url)
        
        return ImageGenerationResult(
            success=True,
            images=images,
            provider="free-test-provider",
            model="svg-generator",
            metadata={
                "size": request.size,
                "total_images": len(images),
                "cost_usd": 0.0,
                "type": "svg"
            },
            cost=0.0
        )
    
    def _generate_test_svg(self, width: int, height: int, company: dict, prompt: str, variation_id: int = 0) -> str:
        """Generate a simple test SVG"""
        colors = company.get("brand_colors", ["#2563EB", "#DC2626"])
        bg_color = colors[variation_id % len(colors)]
        text_color = "#FFFFFF" if variation_id % 2 == 0 else "#000000"
        
        # Simple prompt analysis
        shapes = []
        if any(word in prompt.lower() for word in ["circle", "round", "ball"]):
            shapes.append(f'<circle cx="{width//2}" cy="{height//2}" r="{min(width, height)//4}" fill="{colors[(variation_id + 1) % len(colors)]}" opacity="0.7"/>')
        
        if any(word in prompt.lower() for word in ["square", "box", "rectangle"]):
            shapes.append(f'<rect x="{width//4}" y="{height//4}" width="{width//2}" height="{height//3}" fill="{colors[(variation_id + 2) % len(colors)]}" opacity="0.6"/>')
        
        return f'''
        <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="{bg_color}"/>
            {''.join(shapes)}
            <text x="{width//2}" y="{height//2}" font-family="Arial, sans-serif" font-size="16" 
                  fill="{text_color}" text-anchor="middle" dominant-baseline="middle">
                {company['name']} - {prompt[:30]}{'...' if len(prompt) > 30 else ''}
            </text>
            <text x="{width//2}" y="{height//2 + 30}" font-family="Arial, sans-serif" font-size="12" 
                  fill="{text_color}" text-anchor="middle" dominant-baseline="middle" opacity="0.8">
                Variation {variation_id + 1}
            </text>
        </svg>
        '''.strip()

# ==========================================
# PROVIDER REGISTRY
# ==========================================
# Maps provider IDs to their implementation classes
# Add new provider implementations here to make them available
PROVIDER_REGISTRY = {
    "openai": OpenAIProvider,
    "stability": StabilityAIProvider,
    "replicate": ReplicateProvider,
    "huggingface": HuggingFaceProvider,
}

logger.info(f"📋 Provider Registry: {len(PROVIDER_REGISTRY)} implementations available")
logger.info(f"   Registered providers: {', '.join(PROVIDER_REGISTRY.keys())}")

# ==========================================
# GLOBAL INSTANCE & FACTORY
# ==========================================

# Global instance - will be initialized with database connection in main.py
ai_provider_manager = None

def get_provider_manager(database_client=None):
    """
    Get or create the provider manager instance with database connection
    This ensures the manager always has access to the database
    """
    global ai_provider_manager
    if ai_provider_manager is None:
        ai_provider_manager = AIProviderManager(database_client=database_client)
    elif database_client is not None and ai_provider_manager.db is None:
        # Update the database connection if it was None
        ai_provider_manager.db = database_client
    return ai_provider_manager
