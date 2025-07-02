import api from './api';
import { Material, MaterialCreationFormData, MaterialStage, MaterialStatus } from '@/types';

// In-memory cache for materials
const materialsCache = {
  data: null as Material[] | null,
  timestamp: 0,
  ttl: 30000, // 30 seconds TTL
};

// Function to check if cache is valid
const isCacheValid = () => {
  return materialsCache.data !== null && 
    (Date.now() - materialsCache.timestamp) < materialsCache.ttl;
};

// Check if we're in development mode - Edge compatible
const isDevelopmentMode = () => {
  try {
    // Check window location first (more reliable in browser)
    if (typeof window !== 'undefined' && window.location) {
      const hostname = window.location.hostname;
      const isDev = hostname === 'localhost' || 
             hostname === '127.0.0.1' || 
             hostname.includes('localhost');
      if (isDev) return true;
    }
    
    // Check NODE_ENV as fallback
    if (process.env.NODE_ENV === 'development') {
      return true;
    }
    
    return false;
  } catch (error) {
    // Fallback for Edge or other browser compatibility issues
    console.warn('Error detecting development mode:', error);
    return false;
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
    console.log('Development mode: Returning demo materials');
    const demoMaterials = getDemoMaterials();
    
    // Cache the demo materials
    materialsCache.data = demoMaterials;
    materialsCache.timestamp = Date.now();
    
    return demoMaterials;
  }

  // Return cached data if available and not forcing refresh
  if (!forceRefresh && !stage && !status && skip === 0 && isCacheValid()) {
    console.log('Using cached materials data');
    return materialsCache.data!;
  }

  try {
    let url = `/materials?skip=${skip}&limit=${limit}`;
    if (stage) {
      url += `&stage=${stage}`;
    }
    if (status) {
      url += `&status=${status}`;
    }
    
    console.log('Fetching materials from API');
    const response = await api.get(url);
    
    // Cache the results only if it's the default request (no filters)
    if (!stage && !status && skip === 0) {
      materialsCache.data = response.data;
      materialsCache.timestamp = Date.now();
    }
    
    return response.data;
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
    const demoMaterials = getDemoMaterials();
    const demoMaterial = demoMaterials.find(m => m.id === id);
    if (demoMaterial) {
      console.log('Development mode: Returning demo material for ID:', id);
      return demoMaterial;
    }
  }

  try {
    const response = await api.get(`/materials/${id}`);
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
  // In development mode, simulate creating a material
  if (isDevelopmentMode()) {
    console.log('Development mode: Simulating material creation');
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
    
    // Add to cache if we have cached data
    if (materialsCache.data) {
      materialsCache.data.unshift(newMaterial);
    }
    
    return newMaterial;
  }

  try {
    const response = await api.post('/materials', data);
    
    // Invalidate cache after creating new material
    materialsCache.data = null;
    
    return response.data;
  } catch (error) {
    console.error('Error creating material:', error);
    
    // In development mode, still return simulated material
    if (isDevelopmentMode()) {
      console.log('Development mode: Returning simulated material after error');
      return {
        id: `demo-error-${Date.now()}`,
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
    }
    
    throw error;
  }
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
    const response = await api.put(`/materials/${id}`, data);
    
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
    await api.delete(`/materials/${id}`);
    
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
  try {
    console.log('Adding generated image:', { materialId, imageUrl, prompt, aiProvider });
    
    const response = await api.post(`/materials/${materialId}/images`, {
      url: imageUrl,
      prompt,
      ai_provider: aiProvider,
      generation_params: generationParams
    });
    
    // Clear cache to ensure fresh data
    materialsCache.data = null;
    
    return response.data;
  } catch (error) {
    console.error('Error adding generated image:', error);
    
    // In development mode, simulate adding image to demo material
    if (isDevelopmentMode()) {
      console.log('Development mode: Simulating image addition');
      
      const materials = getDemoMaterials();
      const material = materials.find(m => m.id === materialId);
      
      if (material) {
        const newImage = {
          url: imageUrl,
          prompt,
          ai_provider: aiProvider,
          generation_params: generationParams,
          created_at: new Date().toISOString()
        };
        
        // Add to generated_images array
        const updatedMaterial = {
          ...material,
          generated_images: [...(material.generated_images || []), newImage]
        };
        
        return updatedMaterial;
      }
    }
    
    throw error;
  }
}

// Select image for material
export async function selectImage(materialId: string, imageUrl: string): Promise<Material> {
  try {
    const response = await api.post(`/materials/${materialId}/select-image`, {
      image_url: imageUrl
    });
    
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
    const response = await api.post(`/materials/${materialId}/feedback`, {
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
    const response = await api.patch(`/materials/${materialId}/stage`, {
      stage,
      status
    });
    
    // Clear cache to ensure fresh data
    materialsCache.data = null;
    
    return response.data;
  } catch (error) {
    console.error('Error updating stage:', error);
    
    // In development mode, simulate stage update
    if (isDevelopmentMode()) {
      console.log('Development mode: Simulating stage update');
      
      const materials = getDemoMaterials();
      const material = materials.find(m => m.id === materialId);
      
      if (material) {
        const updatedMaterial = {
          ...material,
          stage,
          status,
          updated_at: new Date().toISOString()
        };
        
        return updatedMaterial;
      }
    }
    
    throw error;
  }
}

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
