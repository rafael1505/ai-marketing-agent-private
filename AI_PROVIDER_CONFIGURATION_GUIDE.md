# AI Provider Configuration Guide

This guide explains how to configure each AI provider for optimal image generation results, based on their official API documentation.

## OpenAI DALL-E Configuration

### API Setup
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in to your account
3. Navigate to API Keys
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)

### Models Available
- **DALL-E 3** (Recommended): Latest model with superior instruction following and text rendering
- **DALL-E 2**: Lower cost option with concurrent requests and inpainting support

### Configuration Options

#### Image Size
**DALL-E 3:**
- `1024x1024` (Square) - Standard format
- `1024x1792` (Portrait) - Good for vertical compositions
- `1792x1024` (Landscape) - Good for horizontal compositions

**DALL-E 2:**
- `256x256` - Lowest cost ($0.016 per image)
- `512x512` - Good balance ($0.018 per image)
- `1024x1024` - Highest quality ($0.020 per image)

#### Quality Settings
- **Standard**: Default quality ($0.040 per image for DALL-E 3)
- **HD**: High definition, 2x cost ($0.080 per image for DALL-E 3, DALL-E 3 only)

#### Style Settings (DALL-E 3 only)
- **Vivid**: Hyper-real and dramatic images
- **Natural**: More natural, less hyper-real images

#### Advanced Options
- **Response Format**: `b64_json` (base64) or `url` (temporary URL)
- **User ID**: Optional identifier for abuse monitoring
- **Revised Prompt**: Automatic prompt enhancement (enabled by default)

### Cost Optimization
- Use **Standard** quality for development/testing
- Use **HD** quality only for final production images
- **DALL-E 2** is more cost-effective for high-volume generation
- **Square formats** (1024x1024) are fastest to generate

### Example Configuration
```json
{
  "id": "openai",
  "name": "OpenAI DALL-E",
  "apiKey": "sk-your-api-key-here",
  "selectedModel": "dall-e-3",
  "quality": "standard",
  "size": "1024x1024",
  "style": "vivid",
  "isActive": true,
  "customOptions": {
    "response_format": "b64_json",
    "user": "ai-marketing-agent"
  }
}
```

## Stability AI Configuration

### API Setup
1. Visit [Stability AI Platform](https://platform.stability.ai/account/keys)
2. Sign in to your account
3. Navigate to API Keys
4. Generate a new API key
5. Copy the key (starts with `sk-`)

### Models Available
- **stable-diffusion-xl-1024-v1-0**: Latest SDXL model, high quality
- **stable-diffusion-v1-6**: Fast and reliable
- **stable-diffusion-xl-beta-v2-2-2**: Beta version with advanced features

### Configuration Options

#### Image Sizes
- `1024x1024` (Square)
- `1152x896` (Landscape)
- `896x1152` (Portrait)
- `1216x832` (Wide landscape)
- `832x1216` (Tall portrait)

#### Advanced Parameters
- **CFG Scale** (1-35): How strictly the model follows the prompt (default: 7)
- **Steps** (10-150): Number of diffusion steps (default: 30)
- **Sampler**: Diffusion algorithm to use
- **Seed**: For reproducible results

### Example Configuration
```json
{
  "id": "stability",
  "name": "Stability AI",
  "apiKey": "sk-your-stability-key",
  "selectedModel": "stable-diffusion-xl-1024-v1-0",
  "size": "1024x1024",
  "customOptions": {
    "cfg_scale": 7,
    "steps": 30,
    "sampler": "K_DPMPP_2M"
  }
}
```

## Replicate Configuration

### API Setup
1. Visit [Replicate](https://replicate.com/account/api-tokens)
2. Sign in to your account
3. Navigate to API tokens
4. Create a new token
5. Copy the token (starts with `r8_`)

### Models Available
- **SDXL**: Stable Diffusion XL for high-quality images
- **Stable Diffusion 1.5**: Fast and efficient

### Configuration Options
- **Inference Steps** (1-100): Number of denoising steps (default: 20)
- **Guidance Scale** (1-20): How closely to follow the prompt (default: 7.5)
- **Scheduler**: Algorithm for the denoising process

### Example Configuration
```json
{
  "id": "replicate",
  "name": "Replicate",
  "apiKey": "r8_your-token-here",
  "selectedModel": "stability-ai/sdxl",
  "customOptions": {
    "num_inference_steps": 20,
    "guidance_scale": 7.5,
    "scheduler": "K_EULER"
  }
}
```

## HuggingFace Configuration

### API Setup
1. Visit [HuggingFace](https://huggingface.co/settings/tokens)
2. Sign in to your account
3. Navigate to Access Tokens
4. Create a new token with 'read' role
5. Copy the token (starts with `hf_`)

### Models Available
- **runwayml/stable-diffusion-v1-5**: Popular and reliable
- **stabilityai/stable-diffusion-xl-base-1.0**: Higher quality SDXL
- **CompVis/stable-diffusion-v1-4**: Original Stable Diffusion

### Configuration Options
- **Use Cache**: Enable for faster repeated requests
- **Wait for Model**: If model is loading, wait instead of error

### Example Configuration
```json
{
  "id": "huggingface",
  "name": "HuggingFace",
  "apiKey": "hf_your-token-here",
  "selectedModel": "runwayml/stable-diffusion-v1-5",
  "customOptions": {
    "use_cache": true,
    "wait_for_model": true
  }
}
```

## Best Practices

### For Marketing Content
1. **Use OpenAI DALL-E 3** for text-heavy images and logos
2. **Use Stability AI** for artistic and creative content
3. **Use Standard quality** for development, HD for production
4. **Test with different aspect ratios** for various marketing materials

### Cost Management
1. Start with lower-cost providers for testing
2. Use batch generation when possible
3. Cache results for repeated use
4. Monitor usage and set budgets

### Quality Optimization
1. Use specific, detailed prompts
2. Include style descriptors (photorealistic, artistic, etc.)
3. Specify lighting and composition preferences
4. Test different models for different content types

### Security
1. Store API keys securely (environment variables)
2. Use separate keys for development and production
3. Monitor API usage for unusual activity
4. Rotate keys regularly

## Troubleshooting

### Common Issues
1. **Invalid API Key**: Ensure key format is correct for each provider
2. **Rate Limits**: Implement proper retry logic with exponential backoff
3. **Model Loading**: Some HuggingFace models need warm-up time
4. **Size Restrictions**: Check provider-specific size limitations

### Error Codes
- **401**: Invalid or missing API key
- **429**: Rate limit exceeded
- **400**: Invalid parameters
- **500**: Server error, retry recommended
