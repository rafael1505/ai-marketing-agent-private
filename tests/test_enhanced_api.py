#!/usr/bin/env python3
"""
Simple test API with enhanced error handling for demonstration
"""
import sys
sys.path.insert(0, '.')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our enhanced error handling
from app.core.provider_error_patterns import EnhancedErrorClassifier
from app.core.ai_generation_errors import AIGenerationError, AIGenerationErrorType

# Simple API
app = FastAPI(title='AI Marketing Agent API - Enhanced Errors', version='2.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:3001', 'http://localhost:3001'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

classifier = EnhancedErrorClassifier()

@app.post('/api/generate-content')
async def generate_content(request: dict):
    # Simulate OpenAI billing error for testing
    if request.get('provider') == 'openai':
        fake_error = Exception('You exceeded your current quota, please check your plan and billing details.')
        classified_error = classifier.classify_provider_error(fake_error, 'openai')
        
        return {
            'success': False,
            'error': {
                'type': classified_error.error_type.value,
                'correlation_id': classified_error.correlation_id,
                'user_message': classified_error.user_message,
                'technical_details': classified_error.technical_details,
                'suggested_actions': classified_error.suggested_actions,
                'metadata': classified_error.metadata
            }
        }
    
    return {'success': True, 'content': 'Generated content here'}

@app.get('/api/health')
async def health():
    return {'status': 'healthy', 'enhanced_errors': True}

if __name__ == '__main__':
    print('🚀 Starting Enhanced Error API on http://127.0.0.1:8088')
    print('📖 API Documentation: http://127.0.0.1:8088/docs')
    print('🔧 Enhanced error handling active!')
    uvicorn.run(app, host='127.0.0.1', port=8088)