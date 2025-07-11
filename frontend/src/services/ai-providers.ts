import { AIProviderConfig } from "@/types";
import { apiRequest } from "./api";
import { DEFAULT_AI_PROVIDERS } from "@/constants";

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
}

export interface ImageGenerationResult {
  success: boolean;
  images: string[];
  provider: string;
  model: string;
  metadata: Record<string, any>;
  cost?: number;
  error?: string;
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
    // Try the main API first
    const response = await apiRequest('/api/v1/ai/providers', {
      method: 'GET'
    });
    
    if (response && response.providers) {
      console.log('Loaded providers from main API:', response.providers);
      return response.providers;
    }
  } catch (error) {
    console.error('Error fetching providers from main API:', error);
    
    // Fallback to test server
    try {
      const fallbackResponse = await fetch('http://127.0.0.1:8089/providers');
      if (fallbackResponse.ok) {
        const fallbackData = await fallbackResponse.json();
        console.log('Loaded providers from test server:', fallbackData.providers);
        return fallbackData.providers || [];
      }
    } catch (fallbackError) {
      console.error('Fallback provider fetch failed:', fallbackError);
    }
  }
  
  // Return mock data for testing when all APIs fail
  console.log('Using mock providers for testing');
  return [
    {
      id: "free-test-provider",
      name: "Free Test Provider",
      configured: true,
      available: true,
      model: "test-svg-generator",
      max_variations: 4,
      supported_sizes: ["512x512", "1024x1024"],
      features: ["fast", "free", "testing"],
      pricing: { per_image: 0.0 },
      status: "active"
    },
    {
      id: "openai",
      name: "OpenAI DALL-E",
      configured: false,
      available: false,
      model: "dall-e-3",
      max_variations: 1,
      supported_sizes: ["1024x1024", "1792x1024", "1024x1792"],
      features: ["high-quality", "realistic", "creative"],
      pricing: { per_image: 0.04 },
      status: "not_configured"
    },
    {
      id: "stability",
      name: "Stability AI",
      configured: false,
      available: false,
      model: "stable-diffusion-xl-1024-v1-0",
      max_variations: 10,
      supported_sizes: ["1024x1024", "1152x896", "896x1152"],
      features: ["artistic", "customizable", "fast"],
      pricing: { per_image: 0.03 },
      status: "not_configured"
    }
  ];
};

// Get default provider options for a given provider ID
export const getProviderOptions = async (providerId: string): Promise<{ models: string[] }> => {
  try {
    // Try API call to get provider-specific options
    try {
      const response = await apiRequest(`/api/v1/ai-providers/${providerId}/options`, {
        method: "GET"
      });
      
      if (response && response.models) {
        return response;
      }
    } catch (error) {
      console.error("Error fetching provider options:", error);
    }
    
    // If API fails, return mock options based on provider ID
    const mockOptions = {
      stability: [
        "stable-diffusion-xl-1024-v1-0",
        "stable-diffusion-xl-1024-v0-9",
        "stable-diffusion-v1-5"
      ],
      huggingface: [
        "runwayml/stable-diffusion-v1-5",
        "CompVis/stable-diffusion-v1-4",
        "stabilityai/stable-diffusion-2-1"
      ],
      replicate: [
        "stability-ai/sdxl",
        "stability-ai/stable-diffusion",
        "cjwbw/dreamshaper"
      ]
    };
    
    console.log(`Using mock options for ${providerId}`);
    return { 
      models: mockOptions[providerId as keyof typeof mockOptions] || ["default-model-1", "default-model-2"] 
    };
  } catch (error) {
    console.error("Error in getProviderOptions:", error);
    return { models: [] };
  }
};

// Get all AI providers configured for the current user
export const getUserAIProviders = async (): Promise<AIProviderConfig[]> => {
  try {
    console.log("getUserAIProviders: Starting...");
    
    // Always check localStorage first - it's our source of truth for user configurations
    const cachedProviders = localStorage.getItem(PROVIDER_CONFIGS_STORAGE_KEY);
    if (cachedProviders) {
      try {
        const parsed = JSON.parse(cachedProviders);
        if (Array.isArray(parsed)) {
          console.log(`getUserAIProviders: Found ${parsed.length} cached providers, using as authoritative source`);
          return parsed;
        }
      } catch (parseError) {
        console.error("getUserAIProviders: Error parsing cached providers:", parseError);
      }
    }
    
    // Only if no localStorage data exists, try to get initial setup from API
    console.log("getUserAIProviders: No cached providers found, attempting initial API fetch...");
    
    try {
      const response = await apiRequest("/ai-providers", {
        method: "GET"
      });
      
      if (response && Array.isArray(response) && response.length > 0) {
        console.log(`getUserAIProviders: API returned ${response.length} providers for initial setup`);
        
        // Filter out any configurations with masked API keys before storing
        const safeConfigs = response.filter(config => 
          !config.apiKey || !isMaskedApiKey(config.apiKey)
        );
        
        console.log(`getUserAIProviders: Filtered out ${response.length - safeConfigs.length} providers with masked keys`);
        
        if (safeConfigs.length > 0) {
          localStorage.setItem(PROVIDER_CONFIGS_STORAGE_KEY, JSON.stringify(safeConfigs));
          return safeConfigs;
        } else {
          console.log("getUserAIProviders: All API configs had masked keys, not storing");
        }
      } else {
        console.log("getUserAIProviders: API returned empty or invalid data, not storing");
      }
    } catch (apiErr) {
      console.log("getUserAIProviders: API unavailable (normal):", apiErr);
    }
    
    // If API fails and no cache, return empty array instead of defaults
    // This prevents overwriting user configurations with default values
    console.log("getUserAIProviders: No data available, returning empty array");
    return [];
  } catch (error) {
    console.error("getUserAIProviders: Error:", error);
    
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
    // Try to save via API
    try {
      const response = await apiRequest("/api/v1/ai-providers", {
        method: "POST",
        body: JSON.stringify(provider)
      });
      
      if (response) {
        // Update local storage with the new/updated provider
        // Note: Converting AIProviderConfig to ProviderConfig for storage
        const configForStorage: ProviderConfig = {
          id: response.id,
          name: response.name || response.id,
          apiKey: response.apiKey,
          isActive: response.isActive,
          ...response
        };
        updateLocalStorageConfigurations(configForStorage);
        return response;
      }
    } catch (apiErr) {
      console.error("API error saving AI provider:", apiErr);
    }
    
    // If API fails, just update localStorage as fallback
    const configForStorage: ProviderConfig = {
      ...provider,
      id: provider.id,
      name: provider.name || provider.id
    };
    updateLocalStorageConfigurations(configForStorage);
    return provider;
  } catch (error) {
    console.error("Error in saveAIProvider:", error);
    return null;
  }
};

// Update an existing AI provider
export const updateAIProvider = async (providerId: string, updates: Partial<AIProviderConfig>): Promise<AIProviderConfig | null> => {
  try {
    // Try to update via API
    try {
      const response = await apiRequest(`/api/v1/ai-providers/${providerId}`, {
        method: "PUT",
        body: JSON.stringify(updates)
      });
      
      if (response) {
        // Update local storage with the updated provider
        const configForStorage: ProviderConfig = {
          ...response,
          id: response.id,
          name: response.name || response.id
        };
        updateLocalStorageConfigurations(configForStorage);
        return response;
      }
    } catch (apiErr) {
      console.error(`API error updating AI provider ${providerId}:`, apiErr);
    }
    
    // If API fails, update localStorage as fallback
    const cachedProviders = localStorage.getItem(PROVIDER_CONFIGS_STORAGE_KEY);
    if (cachedProviders) {
      const providers = JSON.parse(cachedProviders) as AIProviderConfig[];
      const updatedProviders = providers.map(p => 
        p.id === providerId ? { ...p, ...updates } : p
      );
      
      localStorage.setItem(PROVIDER_CONFIGS_STORAGE_KEY, JSON.stringify(updatedProviders));
      
      return updatedProviders.find(p => p.id === providerId) || null;
    }
    
    return null;
  } catch (error) {
    console.error("Error in updateAIProvider:", error);
    return null;
  }
};

// Delete an AI provider
export const deleteAIProvider = async (providerId: string): Promise<boolean> => {
  try {
    // Try to delete via API
    try {
      await apiRequest(`/api/v1/ai-providers/${providerId}`, {
        method: "DELETE"
      });
    } catch (apiErr) {
      console.error(`API error deleting AI provider ${providerId}:`, apiErr);
    }
    
    // Always update localStorage regardless of API success
    const cachedProviders = localStorage.getItem(PROVIDER_CONFIGS_STORAGE_KEY);
    if (cachedProviders) {
      const providers = JSON.parse(cachedProviders) as AIProviderConfig[];
      const updatedProviders = providers.filter(p => p.id !== providerId);
      localStorage.setItem(PROVIDER_CONFIGS_STORAGE_KEY, JSON.stringify(updatedProviders));
    }
    
    return true;
  } catch (error) {
    console.error("Error in deleteAIProvider:", error);
    return false;
  }
};

// Validate an API key (test the connection)
export const validateAPIKey = async (providerId: string, apiKey: string): Promise<{ valid: boolean, message?: string }> => {
  try {
    // Try to validate via API
    try {
      const response = await apiRequest(`/api/v1/ai-providers/validate`, {
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
 * Generate images using the new backend AI provider manager
 */
export const generateImagesWithProvider = async (request: ImageGenerationRequest): Promise<ImageGenerationResult> => {
  try {
    // Try the main API first
    const response = await apiRequest('/api/v1/ai/generate-image', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (response && response.success) {
      console.log('Generated images with main API:', response);
      
      // Convert single image response to multiple images format for backward compatibility
      if (response.image_url && !response.images) {
        response.images = [response.image_url];
      }
      
      return response;
    }
  } catch (error) {
    console.error('Error generating images with main API:', error);
    
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
 */
export const generateMultipleImages = async (
  prompt: string,
  provider: string = 'free-test-provider',
  variations: number = 5,
  size: string = '1024x1024'
): Promise<ImageGenerationResult> => {
  // Get the provider configuration to include selected model and other options
  const providerConfig = getStoredProviderConfig(provider);
  
  const request: ImageGenerationRequest = {
    prompt,
    provider,
    size: providerConfig?.size || size,
    variations,
    style: providerConfig?.style || 'vivid',
    quality: providerConfig?.quality || 'standard',
  };

  // Add selected model if available
  if (providerConfig?.selectedModel) {
    request.model = providerConfig.selectedModel;
  }

  return generateImagesWithProvider(request);
};

/**
 * Get the recommended AI provider
 */
export const getRecommendedProvider = async (): Promise<string> => {
  try {
    const response = await apiRequest('/api/v1/ai/providers/recommended');
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
      const response = await apiRequest('/ai-providers', {
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
      const testResponse = await fetch(getTestApiUrl('/api/v1/ai-providers'), {
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
      const response = await apiRequest(`/ai-providers/${providerId}`, {
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
      const testResponse = await fetch(getTestApiUrl(`/api/v1/ai-providers/${providerId}`), {
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
      const response = await apiRequest('/ai-providers/validate', {
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
      const response = await apiRequest('/ai-providers/configurations', {
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
    await apiRequest(`/api/v1/ai-providers/${providerId}`, {
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
 */
export const getActiveProviders = async (): Promise<ProviderConfig[]> => {
  try {
    console.log('=== Getting active providers for material creation/editing ===');
    
    // Get all provider configurations
    const allConfigs = await getProviderConfigurations();
    console.log('All configurations loaded:', allConfigs);
    
    if (!Array.isArray(allConfigs)) {
      console.error('allConfigs is not an array:', typeof allConfigs, allConfigs);
      return [];
    }
    
    // Filter for active and configured providers
    const activeProviders = allConfigs.filter(config => {
      if (!config || typeof config !== 'object') {
        console.warn('Invalid config object:', config);
        return false;
      }
      
      // More lenient API key checking
      const hasApiKey = config.apiKey && 
                       typeof config.apiKey === 'string' && 
                       config.apiKey.trim().length > 0 && 
                       !isMaskedApiKey(config.apiKey);
      
      // Check if the provider is marked as active
      const isActive = config.isActive === true;
      
      console.log(`Provider ${config.id}:`, {
        hasApiKey,
        isActive,
        apiKeyLength: config.apiKey ? config.apiKey.length : 0,
        apiKeyMasked: config.apiKey ? isMaskedApiKey(config.apiKey) : false,
        apiKeyValue: config.apiKey ? config.apiKey.substring(0, 10) + '...' : 'none',
        rawConfig: config
      });
      
      // A provider is active if it has a valid API key AND is marked as active
      // OR if it's a special provider that doesn't need an API key
      const isSpecialProvider = config.id === 'free-test-provider' || config.id === 'ollama' || config.id === 'lmstudio';
      
      if (isSpecialProvider) {
        console.log(`Special provider ${config.id}: requires no API key, active=${isActive}`);
        return isActive;
      }
      
      const shouldInclude = hasApiKey && isActive;
      console.log(`Provider ${config.id} should be included: ${shouldInclude} (hasApiKey=${hasApiKey}, isActive=${isActive})`);
      
      return shouldInclude;
    });
    
    console.log('=== Active providers found ===', activeProviders.length, 'providers:', activeProviders);
    
    if (activeProviders.length === 0) {
      console.warn('No active providers found. Troubleshooting:');
      console.warn('1. Check that providers are configured with valid API keys');
      console.warn('2. Check that providers are enabled (isActive: true)');
      console.warn('3. Check localStorage contains the configurations');
      console.warn('4. Use browser dev tools to inspect localStorage:', localStorage.getItem(PROVIDER_CONFIGS_STORAGE_KEY));
      
      // Show current localStorage state for debugging
      const stored = localStorage.getItem(PROVIDER_CONFIGS_STORAGE_KEY);
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          console.warn('Current localStorage state:', parsed);
        } catch (e) {
          console.warn('Error parsing localStorage:', e);
        }
      } else {
        console.warn('No data in localStorage under key:', PROVIDER_CONFIGS_STORAGE_KEY);
      }
    }
    
    return activeProviders;
  } catch (error) {
    console.error('Error getting active providers:', error);
    return [];
  }
};
