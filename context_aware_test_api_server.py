#!/usr/bin/env python3
"""
Enhanced context-aware test server with company brand colors and material context
"""
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Annotated, Dict, Any, Optional, List
import random
import base64
import hashlib
import json
from datetime import datetime

# Create a minimal FastAPI app
app = FastAPI(title="AI Marketing Agent - Context-Aware Test API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files from frontend/public directory
app.mount("/static", StaticFiles(directory="frontend/public"), name="static")

# Mock company data with brand colors (this would come from your database)
MOCK_COMPANIES = {
    "philips": {
        "name": "Philips",
        "brand_colors": ["#0096D6", "#00A651", "#FF6600", "#D50000"],
        "industry": "Healthcare Technology",
        "style": "clean, modern, professional"
    },
    "nike": {
        "name": "Nike", 
        "brand_colors": ["#000000", "#FFFFFF", "#FF6600"],
        "industry": "Sports & Athletic",
        "style": "dynamic, energetic, bold"
    },
    "apple": {
        "name": "Apple",
        "brand_colors": ["#000000", "#FFFFFF", "#007AFF", "#FF3B30"],
        "industry": "Technology",
        "style": "minimalist, premium, sleek"
    },
    "default": {
        "name": "Default Company",
        "brand_colors": ["#2563EB", "#DC2626", "#059669", "#7C3AED"],
        "industry": "General Business",
        "style": "professional, modern"
    }
}

# Mock material types and their characteristics
MATERIAL_CONTEXTS = {
    "product_launch": {
        "style": "exciting, dynamic, attention-grabbing",
        "elements": ["product showcase", "bold typography", "energetic design"]
    },
    "brand_awareness": {
        "style": "trustworthy, professional, memorable", 
        "elements": ["brand logo", "consistent messaging", "clean layout"]
    },
    "educational": {
        "style": "clear, informative, accessible",
        "elements": ["diagrams", "clean typography", "organized layout"]
    },
    "promotional": {
        "style": "compelling, urgent, value-focused",
        "elements": ["offer highlights", "call-to-action", "promotional badges"]
    },
    "corporate": {
        "style": "professional, authoritative, polished",
        "elements": ["corporate imagery", "formal typography", "structured layout"]
    }
}

def get_company_context(company_id: Optional[str] = None) -> Dict[str, Any]:
    """Get company context including brand colors and style"""
    if company_id and company_id.lower() in MOCK_COMPANIES:
        return MOCK_COMPANIES[company_id.lower()]
    return MOCK_COMPANIES["default"]

def enhance_prompt_with_context(
    base_prompt: str,
    company: Dict[str, Any],
    material_type: Optional[str] = None,
    additional_context: Optional[Dict[str, Any]] = None
) -> str:
    """Enhance the base prompt with company brand context and material type"""
    
    # Start with base prompt
    enhanced_prompt = base_prompt
    
    # Add company context
    brand_colors_hex = ", ".join(company["brand_colors"])
    enhanced_prompt += f" incorporating {company['name']} brand colors ({brand_colors_hex})"
    enhanced_prompt += f" with {company['style']} design aesthetic"
    enhanced_prompt += f" suitable for {company['industry']} industry"
    
    # Add material type context
    if material_type and material_type in MATERIAL_CONTEXTS:
        material_ctx = MATERIAL_CONTEXTS[material_type]
        enhanced_prompt += f" designed for {material_type} with {material_ctx['style']} style"
        enhanced_prompt += f" including elements like {', '.join(material_ctx['elements'])}"
    
    # Add any additional context
    if additional_context:
        if additional_context.get('target_audience'):
            enhanced_prompt += f" targeting {additional_context['target_audience']}"
        if additional_context.get('campaign_theme'):
            enhanced_prompt += f" with {additional_context['campaign_theme']} theme"
    
    return enhanced_prompt

def analyze_prompt_content(prompt: str) -> Dict[str, Any]:
    """Analyze the prompt to extract visual elements and themes"""
    prompt_lower = prompt.lower()
    
    # Detect objects/subjects
    objects = []
    if any(word in prompt_lower for word in ['device', 'product', 'equipment', 'machine']):
        objects.append('device')
    if any(word in prompt_lower for word in ['person', 'people', 'human', 'professional', 'doctor', 'athlete']):
        objects.append('person')
    if any(word in prompt_lower for word in ['building', 'office', 'hospital', 'facility']):
        objects.append('building')
    if any(word in prompt_lower for word in ['logo', 'brand', 'symbol', 'icon']):
        objects.append('logo')
    if any(word in prompt_lower for word in ['chart', 'graph', 'data', 'statistics']):
        objects.append('chart')
    if any(word in prompt_lower for word in ['shoe', 'sneaker', 'footwear', 'athletic']):
        objects.append('shoe')
    if any(word in prompt_lower for word in ['phone', 'smartphone', 'mobile', 'iphone']):
        objects.append('phone')
    if any(word in prompt_lower for word in ['heart', 'medical', 'health', 'stethoscope']):
        objects.append('medical')
    
    # Detect style/mood
    style_keywords = {
        'modern': ['modern', 'contemporary', 'sleek', 'minimalist'],
        'dynamic': ['dynamic', 'energetic', 'active', 'motion', 'speed'],
        'professional': ['professional', 'business', 'corporate', 'formal'],
        'friendly': ['friendly', 'warm', 'welcoming', 'approachable'],
        'innovative': ['innovative', 'cutting-edge', 'advanced', 'futuristic'],
        'clean': ['clean', 'simple', 'clear', 'pure', 'minimal']
    }
    
    detected_styles = []
    for style, keywords in style_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            detected_styles.append(style)
    
    # Detect colors mentioned
    color_keywords = {
        'blue': ['blue', 'azure', 'navy', 'cyan'],
        'red': ['red', 'crimson', 'scarlet'],
        'green': ['green', 'emerald', 'lime'],
        'orange': ['orange', 'amber'],
        'black': ['black', 'dark'],
        'white': ['white', 'light', 'bright'],
        'purple': ['purple', 'violet'],
        'yellow': ['yellow', 'gold']
    }
    
    detected_colors = []
    for color, keywords in color_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            detected_colors.append(color)
    
    # Detect composition
    composition = 'centered'  # default
    if any(word in prompt_lower for word in ['background', 'backdrop']):
        composition = 'background_focus'
    if any(word in prompt_lower for word in ['close-up', 'closeup', 'detail']):
        composition = 'close_up'
    if any(word in prompt_lower for word in ['landscape', 'wide', 'panoramic']):
        composition = 'landscape'
    if any(word in prompt_lower for word in ['portrait', 'vertical']):
        composition = 'portrait'
    
    return {
        'objects': objects,
        'styles': detected_styles,
        'colors': detected_colors,
        'composition': composition,
        'text_content': [word for word in prompt.split() if len(word) > 3][:3]  # Key words for text
    }

def generate_context_aware_svg(
    width: int, 
    height: int, 
    company: Dict[str, Any],
    prompt: str,
    material_type: Optional[str] = None,
    variation_id: int = 0
) -> str:
    """Generate a context-aware SVG image using company brand colors and prompt analysis"""
    
    # Analyze the prompt content
    prompt_analysis = analyze_prompt_content(prompt)
    
    # Use company brand colors
    brand_colors = company["brand_colors"]
    primary_color = brand_colors[0] if brand_colors else "#2563EB"
    secondary_color = brand_colors[1] if len(brand_colors) > 1 else "#DC2626"
    accent_color = brand_colors[2] if len(brand_colors) > 2 else "#059669"
    text_color = "#FFFFFF" if primary_color.lower() in ['#000000', '#333333'] else "#FFFFFF"
    
    # Generate unique image ID based on prompt, company, and variation
    image_id = abs(hash(prompt + company["name"] + str(variation_id))) % 1000
    
    # Vary the design based on variation_id
    variation_seed = variation_id + 1
    random.seed(image_id + variation_seed)  # Consistent variations for same prompt
    
    # Start building SVG
    svg_elements = []
    
    # Background variations based on variation_id
    if variation_id == 0:  # Clean gradient
        svg_elements.append(f'''
        <defs>
            <linearGradient id="bgGrad{image_id}" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{primary_color};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{secondary_color};stop-opacity:0.8" />
            </linearGradient>
            <filter id="shadow{image_id}">
                <feDropShadow dx="2" dy="2" stdDeviation="4" flood-opacity="0.3"/>
            </filter>
        </defs>
        <rect width="100%" height="100%" fill="url(#bgGrad{image_id})"/>''')
    elif variation_id == 1:  # Radial gradient
        svg_elements.append(f'''
        <defs>
            <radialGradient id="bgGrad{image_id}" cx="30%" cy="30%" r="70%">
                <stop offset="0%" style="stop-color:{accent_color};stop-opacity:0.9" />
                <stop offset="50%" style="stop-color:{primary_color};stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:{secondary_color};stop-opacity:1" />
            </radialGradient>
            <filter id="shadow{image_id}">
                <feDropShadow dx="3" dy="3" stdDeviation="5" flood-opacity="0.4"/>
            </filter>
        </defs>
        <rect width="100%" height="100%" fill="url(#bgGrad{image_id})"/>''')
    elif variation_id == 2:  # Diagonal stripes background
        svg_elements.append(f'''
        <defs>
            <pattern id="stripes{image_id}" patternUnits="userSpaceOnUse" width="20" height="20" patternTransform="rotate(45)">
                <rect width="10" height="20" fill="{primary_color}" opacity="0.8"/>
                <rect x="10" width="10" height="20" fill="{secondary_color}" opacity="0.6"/>
            </pattern>
            <filter id="shadow{image_id}">
                <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
            </filter>
        </defs>
        <rect width="100%" height="100%" fill="url(#stripes{image_id})"/>''')
    elif variation_id == 3:  # Geometric pattern
        svg_elements.append(f'''
        <defs>
            <linearGradient id="bgGrad{image_id}" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:{secondary_color};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{accent_color};stop-opacity:0.9" />
            </linearGradient>
            <filter id="shadow{image_id}">
                <feDropShadow dx="1" dy="1" stdDeviation="2" flood-opacity="0.2"/>
            </filter>
        </defs>
        <rect width="100%" height="100%" fill="url(#bgGrad{image_id})"/>
        <!-- Geometric pattern -->
        <circle cx="{width//6}" cy="{height//6}" r="15" fill="{primary_color}" opacity="0.3"/>
        <circle cx="{width*5//6}" cy="{height//6}" r="15" fill="{primary_color}" opacity="0.3"/>
        <circle cx="{width//6}" cy="{height*5//6}" r="15" fill="{primary_color}" opacity="0.3"/>
        <circle cx="{width*5//6}" cy="{height*5//6}" r="15" fill="{primary_color}" opacity="0.3"/>''')
    else:  # variation_id == 4, Minimalist
        svg_elements.append(f'''
        <defs>
            <filter id="shadow{image_id}">
                <feDropShadow dx="1" dy="1" stdDeviation="1" flood-opacity="0.1"/>
            </filter>
        </defs>
        <rect width="100%" height="100%" fill="{primary_color}" opacity="0.1"/>
        <rect x="0" y="0" width="100%" height="8" fill="{accent_color}" opacity="0.8"/>
        <rect x="0" y="{height-8}" width="100%" height="8" fill="{accent_color}" opacity="0.8"/>''')
    
    # Generate visual elements based on detected objects with variations
    element_offset_x = (variation_id - 2) * 20  # Slight positioning variations
    element_offset_y = (variation_id - 2) * 15
    
    if 'device' in prompt_analysis['objects'] or 'product' in prompt_analysis['objects']:
        # Vary device representation based on variation
        device_width = width // 3 + (variation_id * 10)
        device_height = height // 4 + (variation_id * 5)
        device_x = width // 2 - device_width // 2 + element_offset_x
        device_y = height // 3 + element_offset_y
        
        if variation_id < 3:
            svg_elements.append(f'''
            <rect x="{device_x}" y="{device_y}" width="{device_width}" height="{device_height}" 
                  fill="{text_color}" opacity="0.9" rx="8" filter="url(#shadow{image_id})"/>
            <rect x="{device_x + 10}" y="{device_y + 10}" width="{device_width - 20}" height="{device_height - 20}" 
                  fill="{primary_color}" opacity="0.3" rx="4"/>
            <circle cx="{device_x + device_width//2}" cy="{device_y + device_height//2}" r="8" fill="{accent_color}"/>''')
        else:
            # Different style for variations 3-4
            svg_elements.append(f'''
            <rect x="{device_x}" y="{device_y}" width="{device_width}" height="{device_height}" 
                  fill="{accent_color}" opacity="0.7" rx="12" filter="url(#shadow{image_id})"/>
            <rect x="{device_x + 15}" y="{device_y + 15}" width="{device_width - 30}" height="{device_height - 30}" 
                  fill="{text_color}" opacity="0.2" rx="6"/>''')
    
    if 'phone' in prompt_analysis['objects']:
        phone_width = width // 5 + (variation_id * 5)
        phone_height = height // 3 + (variation_id * 8)
        phone_x = width // 2 - phone_width // 2 + element_offset_x
        phone_y = height // 4 + element_offset_y
        
        corner_radius = 12 if variation_id < 2 else 8 if variation_id < 4 else 16
        
        svg_elements.append(f'''
        <rect x="{phone_x}" y="{phone_y}" width="{phone_width}" height="{phone_height}" 
              fill="{text_color}" opacity="0.95" rx="{corner_radius}" filter="url(#shadow{image_id})"/>
        <rect x="{phone_x + 8}" y="{phone_y + 15}" width="{phone_width - 16}" height="{phone_height - 30}" 
              fill="{primary_color}" opacity="0.2" rx="6"/>
        <circle cx="{phone_x + phone_width//2}" cy="{phone_y + phone_height - 10}" r="4" fill="{accent_color}"/>''')
    
    if 'shoe' in prompt_analysis['objects']:
        shoe_width = width // 3 + (variation_id * 8)
        shoe_height = height // 6 + (variation_id * 3)
        shoe_x = width // 2 - shoe_width // 2 + element_offset_x
        shoe_y = height // 2 + element_offset_y
        
        if variation_id % 2 == 0:
            # Elliptical shoe
            svg_elements.append(f'''
            <ellipse cx="{shoe_x + shoe_width//2}" cy="{shoe_y + shoe_height//2}" 
                     rx="{shoe_width//2}" ry="{shoe_height//2}" 
                     fill="{text_color}" opacity="0.9" filter="url(#shadow{image_id})"/>
            <ellipse cx="{shoe_x + shoe_width//3}" cy="{shoe_y + shoe_height//3}" 
                     rx="{shoe_width//4}" ry="{shoe_height//4}" 
                     fill="{accent_color}" opacity="0.8"/>''')
        else:
            # More angular shoe design
            svg_elements.append(f'''
            <path d="M {shoe_x},{shoe_y + shoe_height//2} 
                     Q {shoe_x + shoe_width//4},{shoe_y} {shoe_x + shoe_width//2},{shoe_y + shoe_height//3}
                     Q {shoe_x + shoe_width*3//4},{shoe_y} {shoe_x + shoe_width},{shoe_y + shoe_height//2}
                     L {shoe_x + shoe_width*4//5},{shoe_y + shoe_height} 
                     L {shoe_x + shoe_width//5},{shoe_y + shoe_height} Z" 
                  fill="{text_color}" opacity="0.9" filter="url(#shadow{image_id})"/>''')
    
    if 'medical' in prompt_analysis['objects'] or 'heart' in prompt_analysis['objects']:
        heart_size = min(width, height) // 8 + (variation_id * 3)
        heart_x = width // 2 + element_offset_x
        heart_y = height // 3 + element_offset_y
        
        svg_elements.append(f'''
        <path d="M {heart_x},{heart_y + heart_size//3} 
                 C {heart_x},{heart_y} {heart_x - heart_size//2},{heart_y} {heart_x - heart_size//2},{heart_y + heart_size//4}
                 C {heart_x - heart_size//2},{heart_y + heart_size//2} {heart_x},{heart_y + heart_size} {heart_x},{heart_y + heart_size}
                 C {heart_x},{heart_y + heart_size} {heart_x + heart_size//2},{heart_y + heart_size//2} {heart_x + heart_size//2},{heart_y + heart_size//4}
                 C {heart_x + heart_size//2},{heart_y} {heart_x},{heart_y} {heart_x},{heart_y + heart_size//3} Z" 
              fill="{accent_color}" opacity="0.8" filter="url(#shadow{image_id})"/>''')
    
    if 'chart' in prompt_analysis['objects']:
        chart_x = width // 4 + element_offset_x
        chart_y = height // 3 + element_offset_y
        chart_width = width // 2
        chart_height = height // 3
        
        svg_elements.append(f'''
        <rect x="{chart_x}" y="{chart_y}" width="{chart_width}" height="{chart_height}" 
              fill="{text_color}" opacity="0.1" stroke="{text_color}" stroke-width="2"/>''')
        
        # Vary the number and style of bars
        num_bars = 3 + (variation_id % 2)
        bar_width = chart_width // (num_bars + 2)
        for i in range(num_bars):
            bar_height = (chart_height // 4) * (i + 1 + variation_id % 2)
            bar_x = chart_x + (i + 1) * chart_width // (num_bars + 1)
            bar_y = chart_y + chart_height - bar_height
            color = [primary_color, secondary_color, accent_color][i % 3]
            svg_elements.append(f'''
            <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" 
                  fill="{color}" opacity="0.8" filter="url(#shadow{image_id})"/>''')
    
    # Add decorative elements with variations
    if 'dynamic' in prompt_analysis['styles'] or 'energetic' in prompt_analysis['styles']:
        num_triangles = 2 + variation_id
        for i in range(num_triangles):
            tri_size = 15 + (variation_id * 5) + random.randint(10, 25)
            tri_x = random.randint(tri_size, width - tri_size)
            tri_y = random.randint(tri_size, height - tri_size)
            rotation = random.randint(0, 360)
            
            svg_elements.append(f'''
            <polygon points="{tri_x},{tri_y} {tri_x + tri_size},{tri_y + tri_size//2} {tri_x},{tri_y + tri_size}" 
                     fill="{accent_color}" opacity="0.4" 
                     transform="rotate({rotation} {tri_x + tri_size//2} {tri_y + tri_size//2})"/>''')
    
    # Text content with variation positioning
    text_y_pos = height - 60 - (variation_id * 5)
    font_size = 18 + (variation_id * 2)
    
    # Company name
    svg_elements.append(f'''
    <text x="{width//2}" y="{text_y_pos}" text-anchor="middle" 
          font-family="Arial, sans-serif" font-size="{font_size}" font-weight="bold" fill="{text_color}">
        {company["name"]}
    </text>''')
    
    # Key words from prompt
    if prompt_analysis['text_content']:
        key_words = ' • '.join(prompt_analysis['text_content'][:2])
        svg_elements.append(f'''
        <text x="{width//2}" y="{text_y_pos + 20}" text-anchor="middle" 
              font-family="Arial, sans-serif" font-size="12" fill="{text_color}" opacity="0.9">
            {key_words}
        </text>''')
    
    # Variation indicator
    svg_elements.append(f'''
    <text x="{width - 10}" y="{height - 10}" text-anchor="end" 
          font-family="monospace" font-size="10" fill="{text_color}" opacity="0.6">
        V{variation_id + 1} #{image_id}
    </text>''')
    
    # Combine all elements
    svg_content = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    svg_content += ''.join(svg_elements)
    svg_content += '</svg>'
    
    # Convert SVG to base64 data URL
    svg_base64 = base64.b64encode(svg_content.encode()).decode()
    return f"data:image/svg+xml;base64,{svg_base64}"

# Enhanced image generation endpoint with context awareness
@app.post("/api/v1/ai/generate-image")
async def generate_context_aware_image(
    prompt: Annotated[str, Query()],
    ai_provider: Annotated[str, Query()] = "context-aware-test-provider",
    size: Annotated[str, Query()] = "1024x1024",
    style: Annotated[str, Query()] = "photorealistic",
    company_id: Annotated[Optional[str], Query()] = None,
    material_type: Annotated[Optional[str], Query()] = None,
    target_audience: Annotated[Optional[str], Query()] = None,
    campaign_theme: Annotated[Optional[str], Query()] = None,
    variations: Annotated[int, Query()] = 1
) -> Dict[str, Any]:
    """Generate context-aware marketing image(s) using company brand colors and material context"""
    
    if ai_provider not in ["context-aware-test-provider", "free-test-provider"]:
        raise HTTPException(status_code=400, detail=f"Provider '{ai_provider}' not supported")
    
    # Parse size
    try:
        width, height = map(int, size.split('x'))
    except:
        width, height = 1024, 1024
    
    # Get company context
    company = get_company_context(company_id)
    
    # Prepare additional context
    additional_context = {}
    if target_audience:
        additional_context['target_audience'] = target_audience
    if campaign_theme:
        additional_context['campaign_theme'] = campaign_theme
    
    # Enhance prompt with context
    enhanced_prompt = enhance_prompt_with_context(
        prompt, company, material_type, additional_context
    )
    
    # Generate variations if requested
    if variations > 1:
        image_variations = []
        for i in range(min(variations, 5)):  # Limit to 5 variations max
            variation_id = i + 1
            image_url = generate_context_aware_svg(width, height, company, prompt, material_type, variation_id)
            image_id = abs(hash(enhanced_prompt + str(datetime.now().timestamp()) + str(i))) % 10000
            
            image_variations.append({
                "image_url": image_url,
                "variation_id": variation_id,
                "image_id": image_id,
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt
            })
        
        return {
            "success": True,
            "prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "provider": ai_provider,
            "variations": image_variations,
            "metadata": {
                "size": size,
                "style": style,
                "total_variations": len(image_variations),
                "service": "context-aware-svg-generator",
                "format": "svg-data-url",
                "company": {
                    "name": company["name"],
                    "brand_colors": company["brand_colors"],
                    "industry": company["industry"],
                    "style": company["style"]
                },
                "material_type": material_type,
                "context_applied": {
                    "brand_colors": True,
                    "company_style": True,
                    "material_type": bool(material_type),
                    "target_audience": bool(target_audience),
                    "campaign_theme": bool(campaign_theme)
                }
            }
        }
    else:
        # Single image generation (backward compatibility)
        image_url = generate_context_aware_svg(width, height, company, prompt, material_type)
        image_id = abs(hash(enhanced_prompt + str(datetime.now().timestamp()))) % 10000
        
        return {
            "success": True,
            "image_url": image_url,
            "prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "provider": ai_provider,
            "metadata": {
                "size": size,
                "style": style,
                "image_id": image_id,
                "service": "context-aware-svg-generator",
                "format": "svg-data-url",
                "company": {
                    "name": company["name"],
                    "brand_colors": company["brand_colors"],
                    "industry": company["industry"],
                    "style": company["style"]
                },
                "material_type": material_type,
                "context_applied": {
                    "brand_colors": True,
                    "company_style": True,
                    "material_type": bool(material_type),
                    "target_audience": bool(target_audience),
                    "campaign_theme": bool(campaign_theme)
                }
            }
        }

@app.get("/api/v1/companies/{company_id}/context")
async def get_company_image_context(company_id: str):
    """Get company context for image generation"""
    company = get_company_context(company_id)
    return {
        "company": company,
        "available_material_types": list(MATERIAL_CONTEXTS.keys()),
        "material_contexts": MATERIAL_CONTEXTS
    }

@app.get("/")
async def root():
    return {
        "message": "AI Marketing Agent - Context-Aware Test API", 
        "status": "running",
        "features": [
            "Company brand color integration",
            "Material type context awareness", 
            "Enhanced prompt generation",
            "SVG-based context-aware images"
        ],
        "test_pages": [
            "/multi-image-test - Multi-image selection and zoom interface",
            "/static/multi-image-selection-test.html - Direct static file access"
        ]
    }

@app.get("/multi-image-test")
async def serve_multi_image_test():
    """Serve the multi-image selection test page"""
    return FileResponse("frontend/public/multi-image-selection-test.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "context-aware-test-api"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Context-Aware AI Marketing Agent Test API...")
    print("📋 Features:")
    print("   • Company brand color integration")
    print("   • Material type context awareness") 
    print("   • Enhanced prompt generation")
    print("   • Mock company data for testing")
    print(f"   • Available companies: {', '.join(MOCK_COMPANIES.keys())}")
    print(f"   • Available material types: {', '.join(MATERIAL_CONTEXTS.keys())}")
    uvicorn.run(app, host="127.0.0.1", port=8088)
