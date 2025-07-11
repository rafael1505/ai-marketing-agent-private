"""
Test script to validate OpenAI DALL-E configuration setup
Based on the OpenAI documentation for Image API and DALL-E 3
"""
import os
import json
from typing import Dict, Any, Optional

class OpenAIConfigValidator:
    """Validates OpenAI DALL-E configuration based on API documentation"""
    
    def __init__(self):
        self.models = ["dall-e-3", "dall-e-2"]
        self.dall_e_3_sizes = ["1024x1024", "1024x1792", "1792x1024"]
        self.dall_e_2_sizes = ["256x256", "512x512", "1024x1024"]
        self.qualities = ["standard", "hd"]
        self.styles = ["vivid", "natural"]
        
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate OpenAI configuration based on API specs"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Validate API Key format
        api_key = config.get("apiKey", "")
        if not api_key:
            validation_result["errors"].append("API key is required")
            validation_result["valid"] = False
        elif not api_key.startswith("sk-"):
            validation_result["errors"].append("OpenAI API key should start with 'sk-'")
            validation_result["valid"] = False
        
        # Validate model
        model = config.get("selectedModel", "dall-e-3")
        if model not in self.models:
            validation_result["errors"].append(f"Invalid model '{model}'. Supported: {self.models}")
            validation_result["valid"] = False
        
        # Validate size based on model
        size = config.get("size", "1024x1024")
        if model == "dall-e-3" and size not in self.dall_e_3_sizes:
            validation_result["errors"].append(f"Invalid size '{size}' for DALL-E 3. Supported: {self.dall_e_3_sizes}")
            validation_result["valid"] = False
        elif model == "dall-e-2" and size not in self.dall_e_2_sizes:
            validation_result["errors"].append(f"Invalid size '{size}' for DALL-E 2. Supported: {self.dall_e_2_sizes}")
            validation_result["valid"] = False
        
        # Validate quality
        quality = config.get("quality", "standard")
        if quality not in self.qualities:
            validation_result["errors"].append(f"Invalid quality '{quality}'. Supported: {self.qualities}")
            validation_result["valid"] = False
        
        # Quality HD is only for DALL-E 3
        if quality == "hd" and model == "dall-e-2":
            validation_result["errors"].append("HD quality is only available for DALL-E 3")
            validation_result["valid"] = False
        
        # Validate style
        style = config.get("style", "vivid")
        if style not in self.styles:
            validation_result["errors"].append(f"Invalid style '{style}'. Supported: {self.styles}")
            validation_result["valid"] = False
        
        # Style is only for DALL-E 3
        if style and model == "dall-e-2":
            validation_result["warnings"].append("Style parameter is ignored for DALL-E 2")
        
        # Add cost warnings
        if quality == "hd":
            validation_result["warnings"].append("HD quality costs 2x more than standard quality")
        
        # Add recommendations
        if model == "dall-e-3":
            validation_result["recommendations"].append("DALL-E 3 provides higher quality and better instruction following")
        if size in ["1024x1792", "1792x1024"]:
            validation_result["recommendations"].append("Portrait/landscape formats work well for specific use cases")
        
        return validation_result
    
    def get_estimated_cost(self, config: Dict[str, Any], num_images: int = 1) -> float:
        """Calculate estimated cost based on configuration"""
        model = config.get("selectedModel", "dall-e-3")
        quality = config.get("quality", "standard")
        size = config.get("size", "1024x1024")
        
        # Pricing based on OpenAI documentation
        if model == "dall-e-3":
            if quality == "hd":
                base_cost = 0.08  # $0.08 per image
            else:
                base_cost = 0.04  # $0.04 per image
                
            # Size multipliers for DALL-E 3
            if size in ["1024x1792", "1792x1024"]:
                multiplier = 1.5  # Estimated for non-square
            else:
                multiplier = 1.0
        else:  # DALL-E 2
            if size == "1024x1024":
                base_cost = 0.020
            elif size == "512x512":
                base_cost = 0.018
            else:  # 256x256
                base_cost = 0.016
            multiplier = 1.0
        
        return base_cost * multiplier * num_images
    
    def generate_config_example(self) -> Dict[str, Any]:
        """Generate an example configuration for OpenAI DALL-E"""
        return {
            "id": "openai",
            "name": "OpenAI DALL-E",
            "apiKey": "sk-your-api-key-here",
            "selectedModel": "dall-e-3",
            "quality": "standard",
            "size": "1024x1024",
            "style": "vivid",
            "isActive": True,
            "customOptions": {
                "response_format": "b64_json",
                "user": "ai-marketing-agent"
            }
        }

# Test the validator
if __name__ == "__main__":
    validator = OpenAIConfigValidator()
    
    # Test valid configuration
    valid_config = validator.generate_config_example()
    print("Testing valid configuration:")
    print(json.dumps(valid_config, indent=2))
    print("\nValidation result:")
    result = validator.validate_config(valid_config)
    print(json.dumps(result, indent=2))
    print(f"\nEstimated cost for 1 image: ${validator.get_estimated_cost(valid_config):.4f}")
    
    # Test invalid configuration
    print("\n" + "="*50)
    print("Testing invalid configuration:")
    invalid_config = {
        "id": "openai",
        "apiKey": "invalid-key",
        "selectedModel": "invalid-model",
        "quality": "ultra",
        "size": "2048x2048",
        "style": "realistic"
    }
    print(json.dumps(invalid_config, indent=2))
    result = validator.validate_config(invalid_config)
    print("\nValidation result:")
    print(json.dumps(result, indent=2))
