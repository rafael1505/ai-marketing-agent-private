"""
Free AI Provider Implementation
Generates placeholder images for testing without requiring API keys
"""
import random
from typing import Dict, Any

class FreeTestProvider:
    """Free test provider that generates placeholder images"""
    
    def __init__(self):
        self.name = "Free Test Provider"
        self.id = "free-test-provider"
        self.is_configured = True
        
    def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a placeholder image URL based on the prompt"""
        
        # Generate different placeholder images based on prompt keywords
        size = kwargs.get('size', '1024x1024')
        width, height = size.split('x') if 'x' in size else ('1024', '1024')
        
        # Create themed URLs based on prompt content
        if any(word in prompt.lower() for word in ['business', 'meeting', 'office']):
            seed = 'business'
        elif any(word in prompt.lower() for word in ['product', 'item', 'object']):
            seed = 'product'
        elif any(word in prompt.lower() for word in ['people', 'person', 'human']):
            seed = 'people'
        elif any(word in prompt.lower() for word in ['nature', 'landscape', 'outdoor']):
            seed = 'nature'
        else:
            seed = 'abstract'
        
        # Generate a unique ID for this image
        image_id = random.randint(100, 999)
        
        # Use different placeholder services for variety
        services = [
            f"https://picsum.photos/seed/{seed}{image_id}/{width}/{height}",
            f"https://source.unsplash.com/{width}x{height}/?{seed}",
            f"https://via.placeholder.com/{width}x{height}/0891b2/ffffff?text={seed.title()}+Image"
        ]
        
        selected_url = random.choice(services)
        
        return {
            'url': selected_url,
            'prompt': prompt,
            'provider': self.id,
            'generated_at': 'now',
            'metadata': {
                'size': size,
                'seed': seed,
                'service': 'placeholder'
            }
        }
    
    def is_available(self) -> bool:
        """Always available since it's a test provider"""
        return True
    
    def get_config_status(self) -> Dict[str, Any]:
        """Return configuration status"""
        return {
            'configured': True,
            'api_key_valid': True,
            'ready': True
        }

# Global instance
free_provider = FreeTestProvider()
