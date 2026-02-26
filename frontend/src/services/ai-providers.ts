import { AIProviderConfig } from "@/types";
import type { ErrorDetails } from "@/types/api-errors";
import { apiRequest, generateCorrelationId } from "./api";
import { DEFAULT_AI_PROVIDERS } from "@/constants";
import api from "./api"; // Import api instance for timeout override
import axios from "axios"; // Import axios directly for bypassing Next.js proxy

// Error handling types for AI generation
export enum AIGenerationErrorType {
  BILLING_LIMIT_REACHED = 'billing_limit_reached',
  INVALID_API_KEY = 'invalid_api_key',
  QUOTA_EXCEEDED = 'quota_exceeded',
  RATE_LIMIT_EXCEEDED = 'rate_limit_exceeded',
  CONTENT_POLICY_VIOLATION = 'content_policy_violation',
  NETWORK_ERROR = 'network_error',
  SERVICE_UNAVAILABLE = 'service_unavailable',
  UNKNOWN_ERROR = 'unknown_error'
}

export interface AIGenerationError {
  type: AIGenerationErrorType;
  message: string;
  correlation_id?: string;
  suggested_actions?: string[];
  details?: Record<string, any>;
}

// Constants
const PROVIDER_CONFIGS_STORAGE_KEY = 'ai-provider-configurations';

// New interfaces for the backend AI provider manager integration
export interface AIProvider {
  id: string;
  name: string;
  configured: boolean;
  available: boolean;
  model: string;
  max_variations: number;
  supported_sizes?: string[];
  features?: string[];
  pricing?: Record<string, number>;
  status: string;
}

export interface ImageGenerationRequest {
  prompt: string;
  provider: string;
  size: string;
  variations: number;
  style?: string;
  quality?: string;
  negative_prompt?: string;
  seed?: number;
  model?: string;  // Added to include the selected model
  people_preference?: string;  // Smart 4-mode system: "auto" | "include" | "exclude" | "minimal"
}

export interface ImageGenerationResult {
  success: boolean;
  images: string[];
  provider: string;
  model: string;
  metadata: Record<string, unknown>;
  cost?: number;
  error?: string;
  error_details?: ErrorDetails;
}

// Configuration interfaces
export interface ProviderConfig {
  id: string;
  name: string;
  apiKey?: string;
  selectedModel?: string;
  modelOptions?: string[];
  maxTokens?: number;
  temperature?: number;
  quality?: string;
  size?: string;
  style?: string;
  isActive?: boolean;
  customOptions?: Record<string, any>;
}

export interface ValidationRequest {
  providerId: string;
  apiKey: string;
  config?: Record<string, any>;
}

/**
 * Helper function to get the correct test API URL without duplication
 */
const getTestApiUrl = (path: string): string => {
  // Remove any leading slashes to avoid path duplication
  const cleanPath = path.startsWith('/') ? path.substring(1) : path;
  return `http://127.0.0.1:8089/${cleanPath}`;
};

/**
 * Get all available AI providers from the backend
 */
export const getAvailableProviders = async (): Promise<AIProvider[]> => {
  try {
    // Database-driven only - no fallbacks
    const response = await apiRequest('ai-providers', {
      method: 'GET'
    });
    
    // Check if response is the array directly or wrapped in providers property
    if (Array.isArray(response)) {
      console.log('Loaded providers from database:', response);
      return response;
    } else if (response && response.providers) {
      console.log('Loaded providers from database (wrapped):', response.providers);
      return response.providers;
    }
    
    // If API returns unexpected format, return empty array
    console.warn('API returned unexpected format:', response);
    return [];
  } catch (error) {
    console.error('Error fetching providers from API:', error);
    // No fallbacks - return empty array to show error state
    return [];
  }
};

// Get provider-specific options (models) from the API
export const getProviderOptions = async (providerId: string): Promise<{ models: string[] }> => {
  try {
    // Try API call to get provider-specific options
    const response = await apiRequest(`ai-providers/${providerId}/options`, {
      method: "GET"
    });
    
    if (response && response.models) {
      console.log(`Loaded ${response.models.length} models for ${providerId} from API`);
      return response;
    }
    
    // If API returns unexpected format, return empty
    console.warn(`API returned unexpected format for provider options:`, response);
    return { models: [] };
  } catch (error) {
    console.error("Error fetching provider options:", error);
    // No fallbacks - return empty models
    return { models: [] };
  }
};

/**
 * Get all configurable AI providers for the configuration page
 * This returns all possible providers that can be configured, regardless of current status
 */
export const getConfigurableProviders = async (): Promise<AIProvider[]> => {
  const timestamp = new Date().toISOString();
  console.log(`🚀 [DEBUG] ${timestamp} getConfigurableProviders called`);
  console.log(`🚀 [DEBUG] ${timestamp} This log should appear in browser console`);
  
  // Add debugging to track execution flow
  console.log(`🚀 [DEBUG] ${timestamp} About to enter try block`);
  try {
    // Use direct fetch to bypass the apiRequest base URL issue
    console.log(`🔄 [DEBUG] ${timestamp} Making direct fetch to ai-providers`);
    const response = await fetch(`/api/ai-providers?bust=${Date.now()}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
    });
    
    console.log("📡 [DEBUG] Fetch response status:", response.status, response.statusText);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log("📥 [DEBUG] Direct fetch response received:", data);
    console.log("📥 [DEBUG] Response type:", typeof data, "Is array:", Array.isArray(data));
    console.log("📥 [DEBUG] First provider example:", data[0]);
    
    if (data && Array.isArray(data)) {
      console.log('✅ [DEBUG] Loaded configurable providers from ai-providers API:', data.length);
      
      // Convert the provider config format to AIProvider format
      const convertedProviders: AIProvider[] = data.map(provider => ({
        id: provider.id,
        name: provider.name,
        configured: provider.isConfigured || false,
        available: provider.isActive || false,
        model: provider.selectedModel || 'default',
        max_variations: 1,
        supported_sizes: ["1024x1024"],
        features: ["text-to-image"],
        pricing: provider.pricing || {}, // Use the actual pricing from backend
        status: provider.isConfigured ? 'configured' : 'not_configured'
      }));
      
      console.log('🎯 [DEBUG] Converted providers:', convertedProviders);
      console.log('🎯 [DEBUG] First provider example:', convertedProviders[0]);
      console.log('🎯 [DEBUG] OpenAI provider example:', convertedProviders.find(p => p.id === 'openai'));
      return convertedProviders;
    } else {
      console.log("⚠️ [DEBUG] Response is not an array or is empty");
      throw new Error("API response is not an array");
    }
  } catch (error) {
    console.error('❌ [DEBUG] Error fetching configurable providers:', error);
    console.error('❌ [DEBUG] Error details:', error instanceof Error ? error.message : 'Unknown error');
    console.error('❌ [DEBUG] Error stack:', error instanceof Error ? error.stack : 'No stack trace');
    // No fallback - return empty array to show error state
    return [];
  }
};

// Get all AI providers configured for the current user
export const getUserAIProviders = async (): Promise<AIProviderConfig[]> => {
  try {
    console.log("getUserAIProviders: Fetching from database...");
    
    // Database-driven only - no localStorage, no fallbacks
    const response = await apiRequest("ai-providers", {
      method: "GET"
    });
    
    if (response && Array.isArray(response)) {
      console.log(`getUserAIProviders: Loaded ${response.length} providers from database`);
      return response;
    }
    
    console.warn("getUserAIProviders: API returned unexpected format:", response);
    return [];
  } catch (error) {
    console.error("getUserAIProviders: Error fetching from database:", error);
    
    // Final fallback: try localStorage one more time
    try {
      const cachedProviders = localStorage.getItem(PROVIDER_CONFIGS_STORAGE_KEY);
      if (cachedProviders) {
        const parsed = JSON.parse(cachedProviders);
        if (Array.isArray(parsed)) {
          console.log("getUserAIProviders: Error fallback - using cached providers");
          return parsed;
        }
      }
    } catch (fallbackError) {
      console.error("getUserAIProviders: Fallback error:", fallbackError);
    }
    
    return [];
  }
};

// Save an AI provider configuration
export const saveAIProvider = async (provider: AIProviderConfig): Promise<AIProviderConfig | null> => {
  try {
    const response = await apiRequest("ai-providers", {
      method: "POST",
      body: JSON.stringify(provider)
    });
    
    if (response) {
      // Extract provider data from API response
      const providerData = response.provider || response;
      console.log("SaveAIProvider - saved to database:", providerData);
      return providerData;
    }
    
    console.warn("SaveAIProvider - API returned unexpected response:", response);
    return null;
  } catch (error) {
    console.error("Error saving AI provider to database:", error);
    return null;
  }
};

// Update an existing AI provider
export const updateAIProvider = async (providerId: string, updates: Partial<AIProviderConfig>): Promise<AIProviderConfig | null> => {
  console.log('updateAIProvider called with:', { providerId, updates });
  
  try {
    console.log('Making API request to update provider:', `ai-providers/${providerId}`);
    const response = await apiRequest(`ai-providers/${providerId}`, {
      method: "PUT",
      body: JSON.stringify(updates)
    });
    
    if (response) {
      const providerData = response.provider || response;
      console.log("updateAIProvider - saved to database:", providerData);
      return providerData;
    }
    
    console.warn("updateAIProvider - API returned unexpected response:", response);
    return null;
  } catch (error) {
    console.error("Error updating AI provider in database:", error);
    return null;
  }
};

// Delete an AI provider
export const deleteAIProvider = async (providerId: string): Promise<boolean> => {
  try {
    const response = await apiRequest(`ai-providers/${providerId}`, {
      method: "DELETE"
    });
    
    console.log(`deleteAIProvider - deleted ${providerId} from database`);
    return true;
  } catch (error) {
    console.error(`Error deleting AI provider ${providerId} from database:`, error);
    return false;
  }
};

// Validate an API key (test the connection)
export const validateAPIKey = async (providerId: string, apiKey: string): Promise<{ valid: boolean, message?: string }> => {
  try {
    // Try to validate via API
    try {
      const response = await apiRequest(`ai-providers/validate`, {
        method: "POST",
        body: JSON.stringify({ providerId, apiKey })
      });
      
      if (response) {
        return response;
      }
    } catch (error) {
      console.error("Error validating API key:", error);
    }
    
    // Mock validation logic when API is unavailable
    console.log("API unavailable, using mock validation");
    
    // Test for specific validation cases
    if (apiKey === "invalid_key_test") {
      return { valid: false, message: "Invalid API key" };
    }
    
    // For Stability.AI, check if key starts with "sk-" as a simple validation
    if (providerId === "stability" && !apiKey.startsWith("sk-")) {
      return { valid: false, message: "Invalid Stability API key format. Should start with 'sk-'" };
    }
    
    // For HuggingFace, check if key starts with "hf_" as a simple validation
    if (providerId === "huggingface" && !apiKey.startsWith("hf_")) {
      return { valid: false, message: "Invalid Hugging Face API key format. Should start with 'hf_'" };
    }
    
    // Default to accepting the key in mock mode
    return { valid: true, message: "API key validated successfully (mock mode)" };
  } catch (error) {
    console.error("Error in validateAPIKey:", error);
    // Always provide a fallback in case of error
    return { valid: false, message: "Connection error" };
  }
};

/**
 * Calculate dynamic timeout based on provider and image count
 * Different AI providers have different generation speeds
 */
const calculateTimeout = (imageCount: number, provider: string): number => {
  const baseTimeout = 30000; // 30s base overhead for API calls
  
  // Per-provider time estimates per image (in milliseconds)
  const providerTimePerImage: Record<string, number> = {
    'openai': 25000,          // DALL-E 3: ~20-25s per image
    'stability': 15000,       // Stability AI: ~12-15s per image
    'replicate': 20000,       // Replicate: ~15-20s per image
    'huggingface': 30000,     // HuggingFace: ~25-30s per image
    'midjourney': 35000,      // Midjourney: ~30-35s per image
    'default': 20000          // Default: ~20s per image
  };
  
  const timePerImage = providerTimePerImage[provider.toLowerCase()] || providerTimePerImage['default'];
  const calculatedTimeout = baseTimeout + (imageCount * timePerImage);
  
  // Cap at 120 seconds (2 minutes) to prevent infinite waits
  const maxTimeout = 120000;
  const finalTimeout = Math.min(calculatedTimeout, maxTimeout);
  
  console.log(`[calculateTimeout] Provider: ${provider}, Images: ${imageCount}, Timeout: ${finalTimeout}ms (${finalTimeout/1000}s)`);
  
  return finalTimeout;
};

/**
 * Generate images using the new backend AI provider manager
 */
export const generateImagesWithProvider = async (request: ImageGenerationRequest): Promise<ImageGenerationResult> => {
  // Calculate dynamic timeout based on provider and image count
  const dynamicTimeout = calculateTimeout(request.variations || 1, request.provider);
  const startTime = Date.now();
  
  try {
    console.log('[generateImagesWithProvider] Sending request to backend:', request);
    console.log(`[generateImagesWithProvider] Using dynamic timeout: ${dynamicTimeout}ms for ${request.variations || 1} images with ${request.provider}`);
    
    // Map frontend request to backend format
    const backendRequest = {
      prompt: request.prompt,
      ai_provider: request.provider, // Backend expects 'ai_provider', not 'provider'
      size: request.size,
      style: request.style || 'vivid',
      quality: request.quality || 'standard',
      variations: request.variations || 1,
      negative_prompt: request.negative_prompt,
      seed: request.seed,
      model: request.model,
      people_preference: request.people_preference || 'auto' // Smart 4-mode system (default: auto)
    };
    
    console.log('[generateImagesWithProvider] Backend request:', backendRequest);
    
    // CRITICAL: Bypass Next.js proxy for AI generation to avoid proxy timeout
    // Next.js proxy has hardcoded ~30s timeout, but DALL-E needs 60-90s
    // Call backend directly at http://127.0.0.1:8088
    const backendUrl = 'http://127.0.0.1:8088/api/v1/ai/generate-image';
    console.log(`[generateImagesWithProvider] Calling backend directly (bypassing proxy): ${backendUrl}`);
    
    // Get auth token from storage
    const token = localStorage.getItem('authToken');
    
    const response = await axios.post(backendUrl, backendRequest, {
      timeout: dynamicTimeout,
      headers: {
        'Content-Type': 'application/json',
        'X-Request-Type': 'ai-generation',
        'Authorization': token ? `Bearer ${token}` : '',
      }
    });

    const data = response.data;
    console.log('[generateImagesWithProvider] Backend response:', data);

    if (data && data.success) {
      console.log('Generated images with main API:', data);
      
      // Convert single image response to multiple images format for backward compatibility
      if (data.image_url && !data.images) {
        data.images = [data.image_url];
      }
      
      return data;
    } else if (data && !data.success && data.error_details) {
      // Return enriched error details (backend contract shape)
      const details = data.error_details as ErrorDetails;
      console.error('API returned error with details:', details);
      return {
        success: false,
        images: [],
        provider: data.provider || request.provider,
        model: 'unknown',
        metadata: {},
        error: data.error,
        error_details: details
      };
    }
  } catch (error: unknown) {
    type ApiErr = { normalizedErrorDetails?: ErrorDetails; config?: { headers?: Record<string, unknown> }; response?: { data?: unknown }; message?: string; code?: string; isTimeout?: boolean };
    const err = error as ApiErr;
    const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
    console.error('Error generating images with main API:', error);
    console.error(`Request failed after ${elapsedTime}s (timeout was ${dynamicTimeout/1000}s)`);

    // Prefer normalized error from api interceptor (UUID correlation_id)
    if (err.normalizedErrorDetails) {
      return {
        success: false,
        images: [],
        provider: request.provider,
        model: 'unknown',
        metadata: {},
        error: err.message || 'Failed to generate images',
        error_details: err.normalizedErrorDetails
      };
    }

    // Check if this is a timeout error from axios interceptor (legacy path)
    if (err.isTimeout || err.code === 'ECONNABORTED') {
      const correlationId = (err.config?.headers?.['X-Correlation-ID'] as string) || generateCorrelationId();
      const fallbackDetails: ErrorDetails = {
        error_type: 'timeout',
        user_message: 'errors.ai.timeout',
        provider: request.provider,
        correlation_id: correlationId,
        http_status: 408,
        details: {
          timeout_seconds: dynamicTimeout / 1000,
          images_requested: request.variations || 1,
          provider: request.provider,
          elapsed_seconds: elapsedTime,
          url: err.config?.url
        },
        timestamp: new Date().toISOString(),
        suggested_actions: ['actions.try_again', 'actions.reduce_image_count', 'actions.simplify_prompt', 'actions.try_different_provider']
      };
      return {
        success: false,
        images: [],
        provider: request.provider,
        model: 'unknown',
        metadata: {},
        error: `Request timed out after ${dynamicTimeout/1000}s`,
        error_details: fallbackDetails
      };
    }

    // Check if error has enriched details from backend (legacy)
    if (err.response?.data && typeof err.response.data === 'object' && (err.response.data as Record<string, unknown>).error_details) {
      const details = (err.response.data as { error_details: ErrorDetails }).error_details;
      return {
        success: false,
        images: [],
        provider: request.provider,
        model: 'unknown',
        metadata: {},
        error: err.message || 'Failed to generate images',
        error_details: details
      };
    }
    
    // Fallback to test server
    try {
      const fallbackResponse = await fetch('http://127.0.0.1:8089/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: request.prompt,
          provider: request.provider,
          size: request.size,
          variations: request.variations,
        }),
      });

      if (fallbackResponse.ok) {
        const fallbackResult = await fallbackResponse.json();
        console.log('Generated images with test server:', fallbackResult);
        return fallbackResult;
      }
    } catch (fallbackError) {
      console.error('Fallback generation failed:', fallbackError);
    }
  }

  // Return error result
  return {
    success: false,
    images: [],
    provider: request.provider,
    model: 'unknown',
    metadata: {},
    error: 'Failed to generate images with any available service',
  };
};

/**
 * Get provider configuration from localStorage
 */
const getStoredProviderConfig = (providerId: string): ProviderConfig | null => {
  try {
    const stored = localStorage.getItem(PROVIDER_CONFIGS_STORAGE_KEY);
    if (stored) {
      const configs = JSON.parse(stored);
      return configs.find((config: ProviderConfig) => config.id === providerId) || null;
    }
  } catch (error) {
    console.error('Error reading provider config from localStorage:', error);
  }
  return null;
};

/**
 * Generate multiple image variations efficiently
 * PURE DATABASE-DRIVEN: Uses provider from database, no localStorage dependency
 */
export const generateMultipleImages = async (
  prompt: string,
  provider: string = 'openai',
  variations: number = 5,
  size: string = '1024x1024',
  peoplePreference: string = 'auto'
): Promise<ImageGenerationResult> => {
  console.log(`[generateMultipleImages] Using provider: ${provider}, variations: ${variations}, peoplePreference: ${peoplePreference}`);
  
  const request: ImageGenerationRequest = {
    prompt,
    provider,
    size,
    variations,
    style: 'vivid',
    quality: 'standard',
    people_preference: peoplePreference,
  };

  console.log('[generateMultipleImages] Request:', request);
  return generateImagesWithProvider(request);
};

/**
 * Get the recommended AI provider
 */
export const getRecommendedProvider = async (): Promise<string> => {
  try {
    const response = await apiRequest('ai/providers/recommended');
    if (response && response.recommended_provider) {
      return response.recommended_provider;
    }
  } catch (error) {
    console.error('Error getting recommended provider:', error);
  }
  return 'free-test-provider';
};

/**
 * Save provider configuration
 */
export const saveProviderConfiguration = async (config: ProviderConfig): Promise<ProviderConfig> => {
  try {
    console.log('Saving provider configuration:', config);
    
    // Try main API first
    try {
      const response = await apiRequest('ai-providers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });
      
      if (response) {
        console.log('Successfully saved configuration via main API:', response);
        
        // If the API response has a masked API key, use the original config instead
        let configToStore = response;
        if (response.apiKey && isMaskedApiKey(response.apiKey) && config.apiKey && !isMaskedApiKey(config.apiKey)) {
          console.log('API returned masked key, preserving original real API key in storage');
          configToStore = { ...response, apiKey: config.apiKey };
        }
        
        // Update localStorage
        updateLocalStorageConfigurations(configToStore);
        return configToStore;
      }
    } catch (apiError) {
      console.error('Main API save failed:', apiError);
    }
    
    // Try fallback to test server
    try {
      console.log('Attempting to save via test server...');
      const testResponse = await fetch(getTestApiUrl('api/v1/ai-providers'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });
      
      if (testResponse.ok) {
        const testData = await testResponse.json();
        console.log('Successfully saved configuration via test server:', testData);
        
        // If the test server response has a masked API key, use the original config instead
        let configToStore = testData;
        if (testData.apiKey && isMaskedApiKey(testData.apiKey) && config.apiKey && !isMaskedApiKey(config.apiKey)) {
          console.log('Test server returned masked key, preserving original real API key in storage');
          configToStore = { ...testData, apiKey: config.apiKey };
        }
        
        // Update localStorage
        updateLocalStorageConfigurations(configToStore);
        return configToStore;
      } else {
        console.error('Test server save failed with status:', testResponse.status);
      }
    } catch (testError) {
      console.error('Test server save failed:', testError);
    }
    
    // If both APIs fail, save to localStorage only
    console.log('Both APIs failed, saving to localStorage only');
    updateLocalStorageConfigurations(config);
    return config;
    
  } catch (error) {
    console.error('Error saving provider configuration:', error);
    throw error;
  }
};

/**
 * Update provider configuration
 */
export const updateProviderConfiguration = async (providerId: string, updates: Partial<ProviderConfig>): Promise<ProviderConfig> => {
  try {
    console.log(`Updating provider configuration for ${providerId}:`, updates);
    
    // Create the full config by merging with existing localStorage data
    const cached = localStorage.getItem(PROVIDER_CONFIGS_STORAGE_KEY);
    let existingConfig: ProviderConfig | undefined;
    
    if (cached) {
      const configurations = JSON.parse(cached);
      existingConfig = configurations.find((c: ProviderConfig) => c.id === providerId);
    }
    
    const fullConfig = {
      id: providerId,
      name: providerId,
      ...existingConfig,
      ...updates
    } as ProviderConfig;
    
    // Try main API first
    try {
      const response = await apiRequest(`ai-providers/${providerId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(fullConfig),
      });
      
      if (response) {
        console.log('Successfully updated configuration via main API:', response);
        
        // If the API response has a masked API key, use the original config instead
        let configToStore = response;
        if (response.apiKey && isMaskedApiKey(response.apiKey) && fullConfig.apiKey && !isMaskedApiKey(fullConfig.apiKey)) {
          console.log('API returned masked key, preserving original real API key in storage');
          configToStore = { ...response, apiKey: fullConfig.apiKey };
        }
        
        // Update localStorage
        updateLocalStorageConfigurations(configToStore);
        return configToStore;
      }
    } catch (apiError) {
      console.error('Main API update failed:', apiError);
    }
    
    // Try fallback to test server
    try {
      console.log('Attempting to update via test server...');
      const testResponse = await fetch(getTestApiUrl(`api/v1/ai-providers/${providerId}`), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(fullConfig),
      });
      
      if (testResponse.ok) {
        const testData = await testResponse.json();
        console.log('Successfully updated configuration via test server:', testData);
        
        // If the test server response has a masked API key, use the original config instead
        let configToStore = testData;
        if (testData.apiKey && isMaskedApiKey(testData.apiKey) && fullConfig.apiKey && !isMaskedApiKey(fullConfig.apiKey)) {
          console.log('Test server returned masked key, preserving original real API key in storage');
          configToStore = { ...testData, apiKey: fullConfig.apiKey };
        }
        
        // Update localStorage
        updateLocalStorageConfigurations(configToStore);
        return configToStore;
      } else {
        console.error('Test server update failed with status:', testResponse.status);
      }
    } catch (testError) {
      console.error('Test server update failed:', testError);
    }
    
    // If both APIs fail, save to localStorage only
    console.log('Both APIs failed, updating localStorage only');
    updateLocalStorageConfigurations(fullConfig);
    return fullConfig;
    
  } catch (error) {
    console.error('Error updating provider configuration:', error);
    throw error;
  }
};

/**
 * Test provider configuration
 */
export const testProviderConfiguration = async (config: ProviderConfig): Promise<boolean> => {
  try {
    // Try main API first
    try {
      const response = await apiRequest('ai-providers/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          providerId: config.id,
          apiKey: config.apiKey,
          config: config.customOptions,
        }),
      });
      
      if (response && response.valid === true) {
        console.log('Provider configuration validated via main API');
        return true;
      }
    } catch (apiError) {
      console.error('Main API validation failed:', apiError);
    }
    
    // Try fallback to test server
    try {
      console.log('Attempting to validate via test server...');
      const testResponse = await fetch(getTestApiUrl('api/v1/ai-providers/validate'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          providerId: config.id,
          apiKey: config.apiKey,
          config: config.customOptions,
        }),
      });
      
      if (testResponse.ok) {
        const testData = await testResponse.json();
        console.log('Validation response from test server:', testData);
        return testData.valid === true;
      } else {
        console.error('Test server validation failed with status:', testResponse.status);
      }
    } catch (testError) {
      console.error('Test server validation failed:', testError);
    }
    
    return false;
  } catch (error) {
    console.error('Error testing provider configuration:', error);
    return false;
  }
};

/**
 * Get provider configurations
 */
export const getProviderConfigurations = async (): Promise<ProviderConfig[]> => {
  try {
    console.log('Fetching provider configurations...');
    
    // Always start with localStorage as the primary source
    let localConfigs: ProviderConfig[] = [];
    try {
      const cached = localStorage.getItem(PROVIDER_CONFIGS_STORAGE_KEY);
      if (cached) {
        const parsed = JSON.parse(cached);
        // Ensure we always work with an array
        localConfigs = Array.isArray(parsed) ? parsed : [];
        console.log('Found provider configurations in localStorage:', localConfigs);
      } else {
        console.log('No cached provider configurations found');
      }
    } catch (cacheError) {
      console.error('Error reading cached provider configurations:', cacheError);
      localConfigs = [];
    }
    
    // Check if any local configs have real API keys (non-masked)
    const hasRealApiKeys = localConfigs.some(config => 
      config.apiKey && 
      config.apiKey.length > 0 && 
      !isMaskedApiKey(config.apiKey)
    );
    
    // If we have local configs with real API keys, ALWAYS return them
    // Never allow API calls to overwrite real user API keys
    if (localConfigs.length > 0 && hasRealApiKeys) {
      console.log('Returning localStorage configurations with real API keys - never overwriting');
      return localConfigs;
    }
    
    // If we have local configs but they all have masked keys, keep them but don't fetch from API
    // This prevents infinite loops of fetching masked keys
    if (localConfigs.length > 0) {
      console.log('Found localStorage configurations but all have masked keys - not fetching from API to prevent overwrite');
      return localConfigs;
    }
    
    // Only fetch from API if we have NO local configs (first time setup)
    console.log('No local configs found, fetching initial setup from API...');
    
    // Try main API to get initial configurations only for first setup
    try {
      const response = await apiRequest('ai-providers/configurations', {
        method: 'GET',
      });
      
      if (response && Array.isArray(response) && response.length > 0) {
        console.log('Successfully received initial provider configurations from main API:', response);
        
        // Filter out any configurations with masked API keys to prevent overwriting real keys
        const safeConfigs = response.filter(config => {
          if (config.apiKey && isMaskedApiKey(config.apiKey)) {
            console.warn(`Filtering out provider ${config.id} from API response due to masked API key`);
            return false;
          }
          return true;
        });
        
        if (safeConfigs.length > 0) {
          console.log(`Storing ${safeConfigs.length} safe provider configurations from API`);
          localStorage.setItem(PROVIDER_CONFIGS_STORAGE_KEY, JSON.stringify(safeConfigs));
          return safeConfigs;
        } else {
          console.log('All API configs had masked keys, not storing any');
        }
      } else {
        console.log('Main API returned empty or invalid data, not overwriting localStorage');
      }
    } catch (apiError) {
      console.log('Main API unavailable (this is normal):', apiError);
    }
    
    // Try the test server on port 8089 as fallback only for initial setup
    try {
      console.log('Trying fallback to test API server for initial setup...');
      const testResponse = await fetch(getTestApiUrl('ai-providers/configurations'));
      if (testResponse.ok) {
        const testData = await testResponse.json();
        console.log('Received provider configs from test server:', testData);
        
        if (Array.isArray(testData) && testData.length > 0) {
          // Filter out any configurations with masked API keys
          const safeConfigs = testData.filter(config => {
            if (config.apiKey && isMaskedApiKey(config.apiKey)) {
              console.warn(`Filtering out provider ${config.id} from test server response due to masked API key`);
              return false;
            }
            return true;
          });
          
          if (safeConfigs.length > 0) {
            console.log(`Test server returned ${safeConfigs.length} safe configurations for initial setup`);
            localStorage.setItem(PROVIDER_CONFIGS_STORAGE_KEY, JSON.stringify(safeConfigs));
            return safeConfigs;
          } else {
            console.log('All test server configs had masked keys, not storing any');
          }
        } else {
          console.log('Test server returned empty data, not overwriting localStorage');
        }
      }
    } catch (testError) {
      console.log('Test server also unavailable (this is normal):', testError);
    }
    
    console.log('No API data available, returning empty array for initial setup');
    return [];
    
  } catch (error) {
    console.error('Error getting provider configurations:', error);
    
    // Final fallback: always try localStorage one more time
    try {
      const cached = localStorage.getItem(PROVIDER_CONFIGS_STORAGE_KEY);
      if (cached) {
        const parsed = JSON.parse(cached);
        const parsedConfigs = Array.isArray(parsed) ? parsed : [];
        console.log('Error fallback: using cached provider configurations:', parsedConfigs);
        return parsedConfigs;
      }
    } catch (cacheError) {
      console.error('Error reading cached provider configurations in fallback:', cacheError);
    }
    
    return [];
  }
};

/**
 * Helper function to merge configurations from different sources
 */
const mergeConfigurations = (localConfigs: ProviderConfig[], apiConfigs: ProviderConfig[]): ProviderConfig[] => {
  const merged: ProviderConfig[] = [...localConfigs];
  
  // Add or update from API configs
  apiConfigs.forEach(apiConfig => {
    const existingIndex = merged.findIndex(config => config.id === apiConfig.id);
    if (existingIndex >= 0) {
      // Merge existing config with API config, preferring local changes
      merged[existingIndex] = {
        ...apiConfig,
        ...merged[existingIndex],
        // Preserve local API key if it exists and is not masked
        apiKey: merged[existingIndex].apiKey && !isMaskedApiKey(merged[existingIndex].apiKey) 
          ? merged[existingIndex].apiKey 
          : apiConfig.apiKey
      };
    } else {
      // Add new config from API
      merged.push(apiConfig);
    }
  });
  
  return merged;
};

/**
 * Helper function to check if an API key is masked
 */
const isMaskedApiKey = (apiKey: string | undefined): boolean => {
  if (!apiKey || typeof apiKey !== 'string') return true;
  
  // Check for various masking patterns
  return apiKey.includes('••••') || 
         apiKey.includes('****') || 
         apiKey.includes('...') ||
         /^\*+$/.test(apiKey) ||
         apiKey === 'hidden' ||
         apiKey === 'masked' ||
         apiKey.length < 8; // API keys are typically longer than 8 characters
};

/**
 * Delete provider configuration
 */
export const deleteProviderConfiguration = async (providerId: string): Promise<void> => {
  try {
    await apiRequest(`ai-providers/${providerId}`, {
      method: 'DELETE',
    });
  } catch (error) {
    console.error('Error deleting provider configuration:', error);
    throw error;
  }
};

/**
 * Helper function to update provider configurations in localStorage
 */
const updateLocalStorageConfigurations = (config: ProviderConfig): void => {
  try {
    console.log('Updating localStorage with config:', config);
    
    // Check if the config has a masked API key
    const hasMaskedApiKey = config.apiKey && isMaskedApiKey(config.apiKey);
    console.log(`Config for ${config.id} has masked API key: ${hasMaskedApiKey}`);
    
    // CRITICAL: If this is a configuration with a masked API key, do NOT save it
    // This prevents API responses from overwriting real user API keys
    if (hasMaskedApiKey) {
      console.warn(`REFUSING to save config for ${config.id} because it has a masked API key. This protects real user API keys.`);
      return;
    }
    
    const cached = localStorage.getItem(PROVIDER_CONFIGS_STORAGE_KEY);
    let configurations: ProviderConfig[] = [];
    
    if (cached) {
      try {
        const parsed = JSON.parse(cached);
        // Ensure we always work with an array
        configurations = Array.isArray(parsed) ? parsed : [];
        console.log('Existing localStorage configurations:', configurations);
      } catch (parseError) {
        console.error('Error parsing cached configurations, starting fresh:', parseError);
        configurations = [];
      }
    }
    
    // Find if the provider already exists
    const existingIndex = configurations.findIndex(c => c.id === config.id);
    
    if (existingIndex >= 0) {
      // Update existing provider, preserving existing values unless explicitly overridden
      configurations[existingIndex] = {
        ...configurations[existingIndex],
        ...config,
        // Ensure id and name are always preserved
        id: config.id,
        name: config.name || configurations[existingIndex].name || config.id
      };
      console.log(`Updated existing configuration for ${config.id}`);
    } else {
      // Add new provider
      const newConfig = {
        ...config,
        name: config.name || config.id
      };
      configurations.push(newConfig);
      console.log(`Added new configuration for ${config.id}`);
    }
    
    // Always save back to localStorage
    localStorage.setItem(PROVIDER_CONFIGS_STORAGE_KEY, JSON.stringify(configurations));
    console.log('Saved localStorage configurations:', configurations);
    
    // Dispatch a custom event to notify other parts of the app
    window.dispatchEvent(new CustomEvent('aiProviderConfigUpdated', { 
      detail: { providerId: config.id, configurations } 
    }));
    
  } catch (error) {
    console.error('Error updating localStorage configurations:', error);
  }
};

/**
 * Get active and configured AI providers for use in material creation/editing
 * This function is used by material pages to get available providers
 * PURE DATABASE-DRIVEN: Fetches from API, no localStorage fallback
 */
export const getActiveProviders = async (): Promise<ProviderConfig[]> => {
  try {
    console.log('=== Getting active providers for material creation/editing (database-driven) ===');
    
    // Fetch directly from database via API
    const response = await apiRequest("ai-providers", {
      method: "GET",
    });
    
    if (!response || !Array.isArray(response)) {
      console.error('Invalid response from API:', response);
      return [];
    }
    
    console.log('All providers from database:', response);
    
    // Filter for active and configured providers
    const activeProviders = response.filter(provider => {
      if (!provider || typeof provider !== 'object') {
        console.warn('Invalid provider object:', provider);
        return false;
      }
      
      // Check if the provider is explicitly marked as configured
      // Only include providers that have been explicitly configured by the user
      const isConfigured = provider.isConfigured === true;
      
      // Check if provider has API key (for providers that need one)
      const hasApiKey = provider.apiKey && 
                       typeof provider.apiKey === 'string' && 
                       provider.apiKey.trim().length > 0;
      
      // Special local providers (Ollama, LM Studio) need to have a selected model to be considered configured
      const isLocalProvider = provider.id === 'ollama' || provider.id === 'lmstudio';
      const hasSelectedModel = provider.selectedModel && 
                              typeof provider.selectedModel === 'string' && 
                              provider.selectedModel.trim().length > 0;
      
      console.log(`Provider ${provider.id}:`, {
        isConfigured,
        hasApiKey,
        isLocalProvider,
        hasSelectedModel
      });
      
      // Include only if explicitly configured AND:
      // - Has API key (for cloud providers), OR
      // - Is local provider AND has selected model
      const shouldInclude = isConfigured && (hasApiKey || (isLocalProvider && hasSelectedModel));
      
      console.log(`Provider ${provider.id} should be included: ${shouldInclude}`);
      
      return shouldInclude;
    });
    
    console.log('=== Active providers found ===', activeProviders.length, 'providers:', activeProviders.map(p => p.id));
    
    if (activeProviders.length === 0) {
      console.warn('No active providers found. Please configure and enable at least one AI provider in the AI Providers page.');
    }
    
    return activeProviders;
  } catch (error) {
    console.error('Error getting active providers:', error);
    return [];
  }
};
