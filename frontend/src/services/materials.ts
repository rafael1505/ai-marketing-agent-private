import api from './api';
import { Material, MaterialCreationFormData, MaterialStage, MaterialStatus } from '@/types';

// Edge-compatible localStorage wrapper
const safeLocalStorage = {
  getItem: (key: string): string | null => {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        return window.localStorage.getItem(key);
      }
    } catch (error) {
      console.warn('localStorage access failed:', error);
    }
    return null;
  },
  setItem: (key: string, value: string): boolean => {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem(key, value);
        return true;
      }
    } catch (error) {
      console.warn('localStorage write failed:', error);
    }
    return false;
  }
};

// Global cache that persists across module reloads
declare global {
  var __materialsCache: {
    data: Material[] | null;
    timestamp: number;
    ttl: number;
  } | undefined;
}

// Use global cache to persist across hot reloads
const materialsCache = globalThis.__materialsCache || {
  data: null as Material[] | null,
  timestamp: 0,
  ttl: 30000, // 30 seconds TTL
};

// Store in global for persistence
globalThis.__materialsCache = materialsCache;

// Enhanced cache management with localStorage backup for development
const loadCacheFromStorage = (): void => {
  if (isDevelopmentMode()) {
    try {
      const stored = safeLocalStorage.getItem('dev_materials_cache');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed.data && Array.isArray(parsed.data) && (Date.now() - parsed.timestamp) < parsed.ttl) {
          materialsCache.data = parsed.data;
          materialsCache.timestamp = parsed.timestamp;
          console.log('Loaded materials cache from localStorage:', materialsCache.data?.length || 0, 'materials');
        }
      }
    } catch (error) {
      console.warn('Failed to load cache from localStorage:', error);
    }
  }
};

const saveCacheToStorage = (): void => {
  if (isDevelopmentMode() && materialsCache.data) {
    try {
      safeLocalStorage.setItem('dev_materials_cache', JSON.stringify({
        data: materialsCache.data,
        timestamp: materialsCache.timestamp,
        ttl: materialsCache.ttl
      }));
      console.log('Saved materials cache to localStorage');
    } catch (error) {
      console.warn('Failed to save cache to localStorage:', error);
    }
  }
};

// Function to check if cache is valid
const isCacheValid = () => {
  return materialsCache.data !== null && 
    (Date.now() - materialsCache.timestamp) < materialsCache.ttl;
};

// Check if we're in development mode - Edge compatible
const isDevelopmentMode = () => {
  try {
    // Check if we're in a browser environment and if backend is available
    // Development mode should only activate when:
    // 1. Running in development (NODE_ENV === 'development')
    // 2. No backend connection available
    
    // For now, disable forced development mode to allow real database usage
    // This allows materials to persist to MongoDB
    return false;
    
    // Note: If backend API calls fail (404, network error), 
    // the service functions will automatically fallback to demo mode
    // in their catch blocks. This provides the best of both worlds:
    // - Use database when available (production behavior)
    // - Graceful degradation to demo mode when backend unavailable
    /*
    // Check NODE_ENV first (most reliable)
    if (process.env.NODE_ENV === 'development') {
      return true;
    }
    
    // Check Next.js development flag
    if (process.env.NEXT_PUBLIC_NODE_ENV === 'development') {
      return true;
    }
    
    // Check window location (browser only)
    if (typeof window !== 'undefined' && window.location) {
      const hostname = window.location.hostname;
      const isDev = hostname === 'localhost' || 
             hostname === '127.0.0.1' || 
             hostname.includes('localhost') ||
             hostname.startsWith('192.168.') ||
             hostname.endsWith('.local');
      if (isDev) return true;
    }
    
    return false;
    */
  } catch (error) {
    // Fallback for Edge or other browser compatibility issues
    console.warn('Error detecting development mode:', error);
    // Default to development mode for safety
    return true;
  }
};

// Demo materials for development mode
const getDemoMaterials = (): Material[] => [
  {
    id: 'demo-1',
    title: '🎯 Product Launch Campaign',
    description: 'A comprehensive marketing campaign for our new product launch, featuring multi-channel messaging and targeted content.',
    target_audience: 'Tech-savvy millennials and early adopters',
    campaign_objective: 'Generate awareness, drive pre-orders, and establish market positioning',
    keywords: ['innovation', 'technology', 'launch', 'exclusive', 'early-bird'],
    stage: MaterialStage.REFINEMENT,
    status: MaterialStatus.IN_PROGRESS,
    company_id: 'demo_company',
    created_by: 'demo_user',
    user_id: 'demo_user',
    created_at: new Date(Date.now() - 86400000 * 3).toISOString(), // 3 days ago
    updated_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    generated_images: [],
    feedback: [
      {
        user_id: 'demo_reviewer',
        comment: 'Great concept! Consider adding more specific call-to-action elements.',
        created_at: new Date().toISOString()
      }
    ],
    api_error: false // Explicitly set to false
  },
  {
    id: 'demo-2',
    title: '📱 Social Media Content Series',
    description: 'Weekly social media posts highlighting our brand values and engaging with our community.',
    target_audience: 'Young professionals aged 25-35',
    campaign_objective: 'Build brand engagement, increase followers, and nurture community',
    keywords: ['social', 'engagement', 'community', 'values', 'brand-building'],
    stage: MaterialStage.IDEA,
    status: MaterialStatus.DRAFT,
    company_id: 'demo_company',
    created_by: 'demo_user',
    user_id: 'demo_user',
    created_at: new Date(Date.now() - 86400000 * 2).toISOString(), // 2 days ago
    updated_at: new Date(Date.now() - 43200000).toISOString(), // 12 hours ago
    generated_images: [],
    feedback: [],
    api_error: false // Explicitly set to false
  },
  {
    id: 'demo-3',
    title: '📧 Email Newsletter Campaign',
    description: 'Monthly newsletter highlighting company updates, industry insights, and customer success stories.',
    target_audience: 'Existing customers and qualified prospects',
    campaign_objective: 'Maintain customer engagement, nurture leads, and drive retention',
    keywords: ['newsletter', 'insights', 'updates', 'engagement', 'retention'],
    stage: MaterialStage.FINALIZATION,
    status: MaterialStatus.READY_FOR_REVIEW,
    company_id: 'demo_company',
    created_by: 'demo_user',
    user_id: 'demo_user',
    created_at: new Date(Date.now() - 86400000 * 5).toISOString(), // 5 days ago
    updated_at: new Date(Date.now() - 1800000).toISOString(), // 30 minutes ago
    generated_images: [],
    feedback: [
      {
        user_id: 'demo_reviewer',
        comment: 'Content looks good! Ready for final approval.',
        created_at: new Date().toISOString()
      }
    ],
    api_error: false // Explicitly set to false
  }
];

export async function getMaterials(
  stage?: MaterialStage,
  status?: MaterialStatus,
  skip = 0,
  limit = 100,
  forceRefresh = false
): Promise<Material[]> {
  // In development mode, always return demo materials first
  if (isDevelopmentMode() && !forceRefresh) {
    console.log('Development mode: Loading materials');
    
    // Load from storage first
    loadCacheFromStorage();
    
    // If we don't have cache data, initialize with demo materials
    if (!materialsCache.data) {
      console.log('No cached data, returning demo materials');
      const demoMaterials = getDemoMaterials();
      
      // Cache the demo materials
      materialsCache.data = demoMaterials;
      materialsCache.timestamp = Date.now();
      saveCacheToStorage();
      
      return demoMaterials;
    }
    
    console.log('Returning cached materials:', materialsCache.data.length);
    return materialsCache.data;
  }

  // Return cached data if available and not forcing refresh
  if (!forceRefresh && !stage && !status && skip === 0 && isCacheValid()) {
    console.log('Using cached materials data');
    return materialsCache.data!;
  }

  try {
    let url = `/api/v1/materials?skip=${skip}&limit=${limit}`;
    if (stage) {
      url += `&stage=${stage}`;
    }
    if (status) {
      url += `&status=${status}`;
    }
    
    console.log('[Materials Service] Fetching materials from API:', url);
    const response = await api.get(url);
    console.log('[Materials Service] API response received:', response);
    console.log('[Materials Service] Response data type:', typeof response.data);
    console.log('[Materials Service] Response data is array?', Array.isArray(response.data));
    console.log('[Materials Service] Response data:', response.data);
    
    // Defensive check: ensure response.data is an array
    const materialsData = Array.isArray(response.data) ? response.data : [];
    
    if (!Array.isArray(response.data)) {
      console.warn('[Materials Service] API returned non-array data for materials:', response.data);
    }
    
    // Cache the results only if it's the default request (no filters)
    if (!stage && !status && skip === 0) {
      console.log('[Materials Service] Caching', materialsData.length, 'materials');
      materialsCache.data = materialsData;
      materialsCache.timestamp = Date.now();
    }
    
    console.log('[Materials Service] Returning', materialsData.length, 'materials');
    return materialsData;
  } catch (error) {
    console.error('Error fetching materials:', error);
    
    // If we have cached data and encounter an error, return the cache as fallback
    if (isCacheValid()) {
      console.log('Using cached materials data as fallback after error');
      return materialsCache.data!;
    }
    
    // In development mode, always return demo materials for any error
    if (isDevelopmentMode()) {
      console.log('Development mode: Returning demo materials after error');
      const demoMaterials = getDemoMaterials();
      
      // Cache the demo materials
      materialsCache.data = demoMaterials;
      materialsCache.timestamp = Date.now();
      
      return demoMaterials;
    }

    // If not in development mode, throw the error to let the calling component handle it
    throw error;
  }
}

export async function getMaterial(id: string): Promise<Material> {
  // In development mode, return demo material if it matches
  if (isDevelopmentMode()) {
    // Load from storage first
    loadCacheFromStorage();
    
    // Check cache first
    if (materialsCache.data) {
      const cachedMaterial = materialsCache.data.find(m => m.id === id);
      if (cachedMaterial) {
        console.log('Development mode: Returning cached material for ID:', id);
        return cachedMaterial;
      }
    }
    
    // Fallback to demo materials
    const demoMaterials = getDemoMaterials();
    const demoMaterial = demoMaterials.find(m => m.id === id);
    if (demoMaterial) {
      console.log('Development mode: Returning demo material for ID:', id);
      return demoMaterial;
    }
  }

  try {
    const response = await api.get(`/api/v1/materials/${id}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching material:', error);
    
    // In development mode, return first demo material as fallback
    if (isDevelopmentMode()) {
      console.log('Development mode: Returning fallback demo material');
      return getDemoMaterials()[0];
    }
    
    throw error;
  }
}

export async function createMaterial(data: MaterialCreationFormData): Promise<Material> {
  const devMode = isDevelopmentMode();
  console.log('createMaterial - Development mode detected:', devMode);
  
  // Try database first (unless forced development mode)
  if (!devMode) {
    try {
      console.log('Attempting to create material in database...');
      
      // Add required fields for backend validation
      const materialData = {
        ...data,
        stage: MaterialStage.IDEA,  // New materials always start in idea stage
        status: MaterialStatus.DRAFT  // New materials always start as draft
      };
      
      const response = await api.post('/api/v1/materials', materialData);
      
      // Invalidate cache after creating new material
      materialsCache.data = null;
      
      console.log('Material created successfully in database:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error creating material in database:', error);
      const is404 = error?.response?.status === 404;
      const isNetworkError = !error?.response;
      
      // Only fall back to demo mode if endpoint doesn't exist or network error
      if (!is404 && !isNetworkError) {
        throw error; // Re-throw other errors (auth, validation, etc.)
      }
      
      console.warn('Database unavailable, falling back to development mode');
    }
  }
  
  // Development mode or fallback: simulate creating a material
  console.log('Development mode: Simulating material creation');
  
  // Load cache from storage if available
  loadCacheFromStorage();
  
  const newMaterial: Material = {
    id: `demo-new-${Date.now()}`,
    title: data.title,
    description: data.description,
    target_audience: data.target_audience,
    campaign_objective: data.campaign_objective,
    keywords: data.keywords,
    stage: MaterialStage.IDEA,
    status: MaterialStatus.DRAFT,
    company_id: 'demo_company',
    created_by: 'demo_user',
    user_id: 'demo_user',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    generated_images: [],
    feedback: []
  };
  
  console.log('Created new material with ID:', newMaterial.id);
  
  // Initialize cache with demo materials if it doesn't exist
  if (!materialsCache.data) {
    console.log('Initializing cache with demo materials');
    materialsCache.data = getDemoMaterials();
    materialsCache.timestamp = Date.now();
  }
  
  // Add new material to the beginning of the cache
  materialsCache.data.unshift(newMaterial);
  console.log('Added material to cache. Cache now has', materialsCache.data.length, 'materials');
  console.log('Cache material IDs:', materialsCache.data.map(m => m.id));
  
  // Update global cache timestamp and save to storage
  materialsCache.timestamp = Date.now();
  saveCacheToStorage();
  
  return newMaterial;
}

export async function updateMaterial(id: string, data: Partial<Material>): Promise<Material> {
  // In development mode, simulate updating a material
  if (isDevelopmentMode()) {
    console.log('Development mode: Simulating material update for ID:', id);
    const demoMaterials = getDemoMaterials();
    const existingMaterial = demoMaterials.find(m => m.id === id) || demoMaterials[0];
    
    const updatedMaterial: Material = {
      ...existingMaterial,
      ...data,
      id: existingMaterial.id, // Keep original ID
      updated_at: new Date().toISOString()
    };
    
    // Update in cache if we have cached data
    if (materialsCache.data) {
      const index = materialsCache.data.findIndex(m => m.id === id);
      if (index >= 0) {
        materialsCache.data[index] = updatedMaterial;
      }
    }
    
    return updatedMaterial;
  }

  try {
    const response = await api.put(`/api/v1/materials/${id}`, data);
    
    // Update cache if we have cached data
    if (materialsCache.data) {
      const index = materialsCache.data.findIndex(m => m.id === id);
      if (index >= 0) {
        materialsCache.data[index] = response.data;
      }
    }
    
    return response.data;
  } catch (error) {
    console.error('Error updating material:', error);
    
    // In development mode, still return simulated update
    if (isDevelopmentMode()) {
      console.log('Development mode: Returning simulated update after error');
      const demoMaterials = getDemoMaterials();
      const existingMaterial = demoMaterials.find(m => m.id === id) || demoMaterials[0];
      
      return {
        ...existingMaterial,
        ...data,
        id: existingMaterial.id,
        updated_at: new Date().toISOString()
      };
    }
    
    throw error;
  }
}

export async function deleteMaterial(id: string): Promise<void> {
  // In development mode, simulate deleting a material
  if (isDevelopmentMode()) {
    console.log('Development mode: Simulating material deletion for ID:', id);
    
    // Remove from cache if we have cached data
    if (materialsCache.data) {
      materialsCache.data = materialsCache.data.filter(m => m.id !== id);
    }
    
    return;
  }

  try {
    await api.delete(`/api/v1/materials/${id}`);
    
    // Remove from cache if we have cached data
    if (materialsCache.data) {
      materialsCache.data = materialsCache.data.filter(m => m.id !== id);
    }
  } catch (error) {
    console.error('Error deleting material:', error);
    
    // In development mode, still simulate successful deletion
    if (isDevelopmentMode()) {
      console.log('Development mode: Simulated deletion after error');
      return;
    }
    
    throw error;
  }
}

// Add generated image to material
export async function addGeneratedImage(
  materialId: string,
  imageUrl: string,
  prompt: string,
  aiProvider: string,
  generationParams: any
): Promise<Material> {
  console.log('Adding generated image to material:', materialId);
  
  // FORCE development mode check with extensive logging
  const devMode = isDevelopmentMode();
  
  try {
    // In development mode, always work with local cache/simulation
    if (devMode) {
      console.log('Development mode: Handling image addition locally');
      
      // Load cache from storage if available
      loadCacheFromStorage();
      
      // Ensure cache exists
      if (!materialsCache.data) {
        console.log('Initializing cache with demo materials');
        materialsCache.data = getDemoMaterials();
        materialsCache.timestamp = Date.now();
      }
      
      // Find the material in cache
      let material = materialsCache.data.find(m => m.id === materialId);
      
      if (!material) {
        console.log('Material not found in cache, creating fallback material');
        // Create a fallback material if it doesn't exist
        material = {
          id: materialId,
          title: 'AI Marketing Material',
          description: 'Generated during image creation',
          target_audience: 'General audience',
          campaign_objective: 'Brand awareness',
          keywords: ['ai', 'marketing'],
          stage: MaterialStage.REFINEMENT,
          status: MaterialStatus.IN_PROGRESS,
          company_id: 'demo_company',
          created_by: 'demo_user',
          user_id: 'demo_user',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          generated_images: [],
          feedback: []
        };
        
        // Add to cache
        materialsCache.data.unshift(material);
        console.log('Created fallback material and added to cache');
      }
      
      // Add the image
      const newImage = {
        url: imageUrl,
        prompt,
        ai_provider: aiProvider,
        generation_params: generationParams,
        created_at: new Date().toISOString()
      };
      
      // Create updated material with new image
      const updatedMaterial = {
        ...material,
        generated_images: [...(material.generated_images || []), newImage],
        updated_at: new Date().toISOString()
      };
      
      // Update in cache
      const index = materialsCache.data.findIndex(m => m.id === materialId);
      if (index >= 0) {
        materialsCache.data[index] = updatedMaterial;
        console.log('Updated existing material in cache');
      } else {
        // This should not happen after our fallback creation, but just in case
        materialsCache.data.unshift(updatedMaterial);
        console.log('Added updated material to cache');
      }
      
      // Save to localStorage for persistence
      saveCacheToStorage();
      
      console.log('Image added successfully. Material now has', updatedMaterial.generated_images.length, 'images');
      return updatedMaterial;
    }

    // Production mode - use real API
    try {
      const fullUrl = `/materials/${materialId}/images?url=${encodeURIComponent(imageUrl)}&prompt=${encodeURIComponent(prompt)}&ai_provider=${encodeURIComponent(aiProvider)}&generation_params=${encodeURIComponent(JSON.stringify(generationParams))}`;
      console.log('Making production API call to:', fullUrl);
      
      const response = await api.post(fullUrl);
      
      // Clear cache to ensure fresh data
      materialsCache.data = null;
      
      return response.data;
    } catch (error) {
      console.error('Error adding generated image via API:', error);
      throw error;
    }
  } catch (error) {
    console.error('Error in addGeneratedImage:', error);
    
    // Ultimate fallback: always create a material with the image in demo mode
    console.log('Creating ultimate fallback material...');
    const fallbackMaterial: Material = {
      id: materialId,
      title: 'Fallback AI Marketing Material',
      description: 'Created as fallback during image generation error',
      target_audience: 'General audience',
      campaign_objective: 'Brand awareness',
      keywords: ['ai', 'marketing', 'fallback'],
      stage: MaterialStage.REFINEMENT,
      status: MaterialStatus.IN_PROGRESS,
      company_id: 'demo_company',
      created_by: 'demo_user',
      user_id: 'demo_user',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      generated_images: [{
        url: imageUrl,
        prompt,
        ai_provider: aiProvider,
        generation_params: generationParams,
        created_at: new Date().toISOString()
      }],
      feedback: []
    };
    
    console.log('Fallback material created successfully');
    return fallbackMaterial;
  }
}

// Select image for material
export async function selectImage(materialId: string, imageUrl: string): Promise<Material> {
  try {
    // Backend expects image_url as a query parameter, not in the body
    const response = await api.post(
      `/api/v1/materials/${materialId}/select-image?image_url=${encodeURIComponent(imageUrl)}`
    );
    
    // Clear cache to ensure fresh data
    materialsCache.data = null;
    
    return response.data;
  } catch (error) {
    console.error('Error selecting image:', error);
    
    // In development mode, simulate selecting image
    if (isDevelopmentMode()) {
      console.log('Development mode: Simulating image selection');
      
      const materials = getDemoMaterials();
      const material = materials.find(m => m.id === materialId);
      
      if (material) {
        const updatedMaterial = {
          ...material,
          selected_image: imageUrl
        };
        
        return updatedMaterial;
      }
    }
    
    throw error;
  }
}

// Add feedback to material
export async function addFeedback(materialId: string, feedback: string): Promise<Material> {
  try {
    const response = await api.post(`/api/v1/materials/${materialId}/feedback`, {
      feedback
    });
    
    // Clear cache to ensure fresh data
    materialsCache.data = null;
    
    return response.data;
  } catch (error) {
    console.error('Error adding feedback:', error);
    
    // In development mode, simulate adding feedback
    if (isDevelopmentMode()) {
      console.log('Development mode: Simulating feedback addition');
      
      const materials = getDemoMaterials();
      const material = materials.find(m => m.id === materialId);
      
      if (material) {
        const updatedMaterial = {
          ...material,
          final_feedback: feedback
        };
        
        return updatedMaterial;
      }
    }
    
    throw error;
  }
}

// Update material stage
export async function updateStage(
  materialId: string,
  stage: MaterialStage,
  status: MaterialStatus
): Promise<Material> {
  try {
    // Use the existing PUT endpoint for partial updates (now supports optional fields)
    const response = await api.put(`/api/v1/materials/${materialId}`, {
      stage,
      status
    });
    
    // Clear cache to ensure fresh data
    materialsCache.data = null;
    
    return response.data;
  } catch (error: any) {
    console.error('Error updating stage:', error);
    
    // Check if it's a 404 or network error - use development mode fallback
    const is404 = error?.response?.status === 404;
    const isNetworkError = !error?.response;
    
    if (is404 || isNetworkError || isDevelopmentMode()) {
      console.log('Development mode: Simulating stage update (backend endpoint not available)');
      
      const materials = getDemoMaterials();
      const material = materials.find(m => m.id === materialId);
      
      if (material) {
        const updatedMaterial = {
          ...material,
          stage,
          status,
          updated_at: new Date().toISOString()
        };
        
        // Update in cache
        const cachedMaterials = materialsCache.data || [];
        const index = cachedMaterials.findIndex(m => m.id === materialId);
        if (index >= 0) {
          cachedMaterials[index] = updatedMaterial;
          materialsCache.data = cachedMaterials;
          saveCacheToStorage();
        }
        
        console.log('Material updated:', updatedMaterial);
        return updatedMaterial;
      }
    }
    
    throw error;
  }
}
