#!/usr/bin/env python3
"""
Minimal test server to isolate the image generation issue
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, Dict, Any
import random
import base64

# Create a minimal FastAPI app
app = FastAPI(title="AI Marketing Agent Test API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_svg_image(width: int, height: int, category: str, image_id: int) -> str:
    """Generate a simple SVG image as a data URL"""
    
    # Color schemes based on category
    color_schemes = {
        "technology": ["#007acc", "#4CAF50", "#FF9800"],
        "business": ["#2196F3", "#607D8B", "#795548"], 
        "marketing": ["#E91E63", "#9C27B0", "#FF5722"],
        "creative": ["#FF4081", "#3F51B5", "#00BCD4"],
        "product": ["#4CAF50", "#FFC107", "#F44336"]
    }
    
    colors = color_schemes.get(category, ["#666666", "#999999", "#CCCCCC"])
    primary_color = colors[image_id % len(colors)]
    
    # Generate a simple SVG with geometric shapes
    svg_content = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad{image_id}" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{primary_color};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{colors[(image_id+1) % len(colors)]};stop-opacity:0.7" />
            </linearGradient>
        </defs>
        <rect width="100%" height="100%" fill="url(#grad{image_id})"/>
        <circle cx="{width//4}" cy="{height//4}" r="{min(width, height)//8}" fill="{colors[(image_id+2) % len(colors)]}" opacity="0.8"/>
        <rect x="{width//2}" y="{height//2}" width="{width//3}" height="{height//3}" fill="{colors[image_id % len(colors)]}" opacity="0.6"/>
        <text x="{width//2}" y="{height//2 + 20}" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="white">
            {category.title()} #{image_id}
        </text>
    </svg>'''
    
    # Convert SVG to base64 data URL
    svg_base64 = base64.b64encode(svg_content.encode()).decode()
    return f"data:image/svg+xml;base64,{svg_base64}"

# Simple image generation endpoint
@app.post("/api/v1/ai/generate-image")
async def generate_image_test(
    prompt: Annotated[str, Query()],
    ai_provider: Annotated[str, Query()] = "free-test-provider",
    size: Annotated[str, Query()] = "1024x1024",
    style: Annotated[str, Query()] = "photorealistic"
) -> Dict[str, Any]:
    """Generate a test image using placeholder service"""
    
    if ai_provider != "free-test-provider":
        raise HTTPException(status_code=400, detail=f"Provider '{ai_provider}' not supported")
    
    # Parse size
    try:
        width, height = map(int, size.split('x'))
    except:
        width, height = 1024, 1024
    
    # Generate image details
    categories = ["technology", "business", "marketing", "creative", "product"]
    category = random.choice(categories)
    image_id = random.randint(100, 999)
    
    # Generate SVG image as data URL
    image_url = generate_svg_image(width, height, category, image_id)
    
    return {
        "success": True,
        "image_url": image_url,
        "prompt": prompt,
        "provider": ai_provider,
        "metadata": {
            "size": size,
            "style": style,
            "category": category,
            "image_id": image_id,
            "service": "local-svg-generator",
            "format": "svg-data-url"
        }
    }

@app.get("/")
async def root():
    return {"message": "AI Marketing Agent Test API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "test-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8089)
