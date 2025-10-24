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
    
    def __init__(self):
        self.providers = {}
        self.provider_configs = {}
        self._load_provider_configs()
        self._initialize_providers()
    
    def _load_provider_configs(self):
        """Load provider configurations from environment variables"""
        self.provider_configs = {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "model": "dall-e-3",
                "max_variations": 1,  # DALL-E 3 limitation
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
    
    def _initialize_providers(self):
        """Initialize available providers based on API keys"""
        if self.provider_configs["openai"]["api_key"]:
            self.providers["openai"] = OpenAIProvider(self.provider_configs["openai"])
        
        if self.provider_configs["stability"]["api_key"]:
            self.providers["stability"] = StabilityAIProvider(self.provider_configs["stability"])
        
        if self.provider_configs["replicate"]["api_key"]:
            self.providers["replicate"] = ReplicateProvider(self.provider_configs["replicate"])
        
        if self.provider_configs["huggingface"]["api_key"]:
            self.providers["huggingface"] = HuggingFaceProvider(self.provider_configs["huggingface"])
        
        # Always include the test provider
        self.providers["free-test-provider"] = TestProvider()
        
        logger.info(f"Initialized {len(self.providers)} AI providers: {list(self.providers.keys())}")
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        status = {}
        
        # Add initialized providers
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
        
        # Add non-initialized providers for visibility
        all_provider_names = {
            "openai": "OpenAI DALL-E",
            "stability": "Stability AI",
            "replicate": "Replicate",
            "huggingface": "HuggingFace"
        }
        
        for provider_id, provider_name in all_provider_names.items():
            if provider_id not in status:
                config = self.provider_configs.get(provider_id, {})
                has_api_key = bool(config.get("api_key"))
                status[provider_id] = {
                    "name": provider_name,
                    "configured": has_api_key,
                    "available": False,
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
            return ImageGenerationResult(
                success=False,
                images=[],
                provider=provider_id,
                model="unknown",
                metadata={},
                error=f"Provider '{provider_id}' not available"
            )
        
        provider = self.providers[provider_id]
        
        if not provider.is_available():
            return ImageGenerationResult(
                success=False,
                images=[],
                provider=provider_id,
                model=provider.get_model(),
                metadata={},
                error=f"Provider '{provider_id}' is not available or configured"
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
    
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """Generate image using OpenAI DALL-E"""
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        
        # DALL-E 3 only supports 1 image at a time
        num_images = min(request.variations, 1)
        
        payload = {
            "model": self.config["model"],
            "prompt": request.prompt,
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
                        
                        cost = len(images) * self.config["pricing"].get(request.quality, 0.04)
                        
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
        
        payload = {
            "text_prompts": [
                {"text": request.prompt, "weight": 1.0}
            ],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": min(request.variations, self.get_max_variations()),
            "steps": 30,
        }
        
        if request.negative_prompt:
            payload["text_prompts"].append({"text": request.negative_prompt, "weight": -1.0})
        
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
                        
                        cost = len(images) * self.config["pricing"]["standard"]
                        
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
        
        payload = {
            "version": self.config["model"].split(":")[-1],
            "input": {
                "prompt": request.prompt,
                "width": width,
                "height": height,
                "num_outputs": min(request.variations, self.get_max_variations()),
                "guidance_scale": 7.5,
                "num_inference_steps": 30
            }
        }
        
        if request.negative_prompt:
            payload["input"]["negative_prompt"] = request.negative_prompt
        
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
                                        cost = len(images) * self.config["pricing"]["standard"]
                                        
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

# Global instance
ai_provider_manager = AIProviderManager()
