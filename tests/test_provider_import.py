#!/usr/bin/env python3
"""
Test script to check provider manager import
"""
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.getcwd())

try:
    print("Testing provider manager import...")
    from app.ai_providers.provider_manager import ai_provider_manager, ImageGenerationRequest
    print("✓ Import successful")
    
    print("Testing provider status...")
    status = ai_provider_manager.get_provider_status()
    print(f"✓ Found {len(status)} providers: {list(status.keys())}")
    
    print("Testing provider manager initialization...")
    recommended = ai_provider_manager.get_recommended_provider()
    print(f"✓ Recommended provider: {recommended}")
    
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print("All tests passed!")
