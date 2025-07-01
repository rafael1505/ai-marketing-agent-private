import { AIProviderConfig } from "@/types";
import { apiRequest } from "./api";
import { DEFAULT_AI_PROVIDERS } from "@/constants";

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
    // Try to fetch from API first, with a short timeout
    try {
      console.log("Fetching AI providers from API...");
      const response = await apiRequest("/ai-providers", {
        method: "GET"
      });
      
      if (response && Array.isArray(response)) {
        console.log(`Successfully fetched ${response.length} providers from API`);
        // Save to local storage as backup
        localStorage.setItem("userAIProviders", JSON.stringify(response));
        return response;
      }
    } catch (apiErr) {
      console.error("API error fetching AI providers:", apiErr);
    }
    
    // If API fails, try to load from localStorage
    const cachedProviders = localStorage.getItem("userAIProviders");
    if (cachedProviders) {
      console.log("Using cached AI providers from localStorage");
      return JSON.parse(cachedProviders);
    }
    
    // If no cached data, use default mock providers from constants
    console.log("Using default AI providers from constants");
    localStorage.setItem("userAIProviders", JSON.stringify(DEFAULT_AI_PROVIDERS));
    return DEFAULT_AI_PROVIDERS;
  } catch (error) {
    console.error("Error in getUserAIProviders:", error);
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
        updateLocalStorageProvider(response);
        return response;
      }
    } catch (apiErr) {
      console.error("API error saving AI provider:", apiErr);
    }
    
    // If API fails, just update localStorage as fallback
    updateLocalStorageProvider(provider);
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
        updateLocalStorageProvider(response);
        return response;
      }
    } catch (apiErr) {
      console.error(`API error updating AI provider ${providerId}:`, apiErr);
    }
    
    // If API fails, update localStorage as fallback
    const cachedProviders = localStorage.getItem("userAIProviders");
    if (cachedProviders) {
      const providers = JSON.parse(cachedProviders) as AIProviderConfig[];
      const updatedProviders = providers.map(p => 
        p.id === providerId ? { ...p, ...updates } : p
      );
      
      localStorage.setItem("userAIProviders", JSON.stringify(updatedProviders));
      
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
    const cachedProviders = localStorage.getItem("userAIProviders");
    if (cachedProviders) {
      const providers = JSON.parse(cachedProviders) as AIProviderConfig[];
      const updatedProviders = providers.filter(p => p.id !== providerId);
      localStorage.setItem("userAIProviders", JSON.stringify(updatedProviders));
    }
    
    return true;
  } catch (error) {
    console.error("Error in deleteAIProvider:", error);
    return false;
  }
};

// Helper function to update a provider in localStorage
const updateLocalStorageProvider = (provider: AIProviderConfig): void => {
  const cachedProviders = localStorage.getItem("userAIProviders");
  let providers: AIProviderConfig[] = [];
  
  if (cachedProviders) {
    providers = JSON.parse(cachedProviders);
  }
  
  // Find if the provider already exists
  const existingIndex = providers.findIndex(p => p.id === provider.id);
  
  if (existingIndex >= 0) {
    // Update existing provider
    providers[existingIndex] = {
      ...providers[existingIndex],
      ...provider
    };
  } else {
    // Add new provider
    providers.push(provider);
  }
  
  localStorage.setItem("userAIProviders", JSON.stringify(providers));
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
