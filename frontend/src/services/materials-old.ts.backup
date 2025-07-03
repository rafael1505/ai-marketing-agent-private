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

export async function getMaterials(
  stage?: MaterialStage,
  status?: MaterialStatus,
  skip = 0,
  limit = 100,
  forceRefresh = false
): Promise<Material[]> {
  // Return cached data if available and not forcing refresh
  if (!forceRefresh && !stage && !status && skip === 0 && isCacheValid()) {
    console.log('Using cached materials data');
    return materialsCache.data!;
  }

  // Check if we have a token, if not try to get one for development
  const token = localStorage.getItem('token');
  if (!token) {
    console.log('No authentication token found, will let API handle auth and fallback to demo data...');
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
    
    // Check if we're in development mode
    const isDevelopment = process.env.NODE_ENV === 'development' || 
                         (typeof window !== 'undefined' && 
                          (window.location.hostname === 'localhost' || 
                           window.location.hostname === '127.0.0.1'));
    
    // If we have cached data and encounter an error, return the cache as fallback
    if (isCacheValid()) {
      console.log('Using cached materials data as fallback after error');
      return materialsCache.data!;
    }
    
    // In development mode, always return demo materials for any error
    if (isDevelopment) {
      console.log('Development mode: Returning demo materials for any error');
      
      const demoMaterials: Material[] = [
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
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          generated_images: [],
          feedback: [
            {
              user_id: 'demo_reviewer',
              comment: 'Great concept! Consider adding more specific call-to-action elements.',
              created_at: new Date().toISOString()
            }
          ],
          api_error: true
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
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          generated_images: [],
          feedback: [],
          api_error: true
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
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          generated_images: [],
          feedback: [
            {
              user_id: 'demo_reviewer',
              comment: 'Content looks good! Ready for final approval.',
              created_at: new Date().toISOString()
            }
          ],
          api_error: true
        }
      ];
      
      // Cache the demo materials
      materialsCache.data = demoMaterials;
      materialsCache.timestamp = Date.now();
      
      return demoMaterials;
    }

    // Special handling for the mock database error (keeping original logic for production)
    // If this is the MongoDB error from the server (SimpleMockDatabase not subscriptable)
    if (error.response?.status === 500 && 
        (error.response?.data?.detail?.includes("SimpleMockDatabase") || 
         error.response?.data?.detail?.includes("not subscriptable"))) {
      console.log('Detected mock database error - returning example materials for demo');
      
      // Return example materials for demo purposes
      const exampleMaterials: Material[] = [
        {
          id: 'example-1',
          title: 'Product Launch Campaign',
          description: 'A comprehensive marketing campaign for our new product launch',
          target_audience: 'Tech-savvy millennials',
          campaign_objective: 'Generate awareness and drive pre-orders',
          keywords: ['innovation', 'technology', 'launch', 'exclusive'],
          stage: MaterialStage.REFINEMENT,
          status: MaterialStatus.IN_PROGRESS,
          company_id: 'demo_company',
          created_by: 'demo_user',
          user_id: 'demo_user',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          generated_images: [],
          feedback: [],
          api_error: true
        },
        {
          id: 'example-2',
          title: 'Social Media Content Series',
          description: 'Weekly social media posts highlighting our brand values',
          target_audience: 'Young professionals',
          campaign_objective: 'Build brand engagement and community',
          keywords: ['social', 'engagement', 'community', 'values'],
          stage: MaterialStage.IDEA,
          status: MaterialStatus.DRAFT,
          company_id: 'demo_company',
          created_by: 'demo_user',
          user_id: 'demo_user',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          generated_images: [],
          feedback: [],
          api_error: true
        },
        {
          id: 'example-3',
          title: 'Email Newsletter Campaign',
          description: 'Monthly newsletter highlighting company updates and insights',
          target_audience: 'Existing customers and prospects',
          campaign_objective: 'Maintain customer engagement and nurture leads',
          keywords: ['newsletter', 'insights', 'updates', 'engagement'],
          stage: MaterialStage.FINALIZATION,
          status: MaterialStatus.READY_FOR_REVIEW,
          company_id: 'demo_company',
          created_by: 'demo_user',
          user_id: 'demo_user',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          generated_images: [],
          feedback: [],
          api_error: true
        }
      ];
      
      return exampleMaterials;
    }
    
    // Return example materials for connection errors to help with demo
    if (error.isConnectionError || 
        error.response?.status === 401 || 
        error.isDevelopmentAuthError ||
        error.response?.status === 403) {
      console.log('Connection/auth error - returning example materials for demo');
      
      const exampleMaterials: Material[] = [
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
          feedback: [{
            user_id: 'reviewer_1',
            comment: 'Great concept! Consider adding more focus on sustainability messaging.',
            created_at: new Date(Date.now() - 7200000).toISOString()
          }],
          api_error: true
        },
        {
          id: 'demo-2',
          title: '📱 Social Media Content Series',
          description: 'Weekly social media posts highlighting our brand values, featuring behind-the-scenes content and user stories.',
          target_audience: 'Young professionals and brand enthusiasts',
          campaign_objective: 'Build brand engagement, foster community, and increase social media following',
          keywords: ['social', 'engagement', 'community', 'values', 'authentic'],
          stage: MaterialStage.IDEA,
          status: MaterialStatus.DRAFT,
          company_id: 'demo_company',
          created_by: 'demo_user',
          user_id: 'demo_user',
          created_at: new Date(Date.now() - 86400000 * 2).toISOString(), // 2 days ago
          updated_at: new Date(Date.now() - 1800000).toISOString(), // 30 mins ago
          generated_images: [],
          feedback: [],
          api_error: true
        },
        {
          id: 'demo-3',
          title: '📧 Email Newsletter Campaign',
          description: 'Monthly newsletter highlighting company updates, industry insights, and customer success stories.',
          target_audience: 'Existing customers, prospects, and industry partners',
          campaign_objective: 'Maintain customer engagement, nurture leads, and position as thought leader',
          keywords: ['newsletter', 'insights', 'updates', 'engagement', 'thought-leadership'],
          stage: MaterialStage.FINALIZATION,
          status: MaterialStatus.READY_FOR_REVIEW,
          company_id: 'demo_company',
          created_by: 'demo_user',
          user_id: 'demo_user',
          created_at: new Date(Date.now() - 86400000 * 5).toISOString(), // 5 days ago
          updated_at: new Date(Date.now() - 900000).toISOString(), // 15 mins ago
          generated_images: [],
          feedback: [{
            user_id: 'reviewer_2',
            comment: 'Ready for final approval. All sections look comprehensive.',
            created_at: new Date(Date.now() - 900000).toISOString()
          }],
          api_error: true
        },
        {
          id: 'demo-4',
          title: '🎨 Brand Refresh Campaign',
          description: 'Complete visual identity refresh including logo updates, color palette changes, and brand messaging evolution.',
          target_audience: 'All stakeholders and customer base',
          campaign_objective: 'Successfully communicate brand evolution while maintaining customer loyalty',
          keywords: ['rebrand', 'visual-identity', 'evolution', 'modern', 'cohesive'],
          stage: MaterialStage.FINALIZATION,
          status: MaterialStatus.COMPLETED,
          company_id: 'demo_company',
          created_by: 'demo_user',
          user_id: 'demo_user',
          created_at: new Date(Date.now() - 86400000 * 10).toISOString(), // 10 days ago
          updated_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
          generated_images: [],
          feedback: [{
            user_id: 'reviewer_1',
            comment: 'Excellent execution! The new brand identity perfectly captures our evolution.',
            created_at: new Date(Date.now() - 86400000).toISOString()
          }],
          api_error: true
        }
      ];
      
      return exampleMaterials;
    }
    
    // Handle authentication errors by returning example materials
    if (error.response?.status === 401 || error.response?.status === 403) {
      console.log('Authentication error - returning example materials for demo');
      
      const exampleMaterials: Material[] = [
        {
          id: 'auth-demo-1',
          title: 'Authentication Demo Material',
          description: 'This material is shown when authentication is not configured',
          target_audience: 'Demo users',
          campaign_objective: 'Show the interface without backend authentication',
          keywords: ['demo', 'auth', 'example'],
          stage: MaterialStage.REFINEMENT,
          status: MaterialStatus.IN_PROGRESS,
          company_id: 'demo_company',
          created_by: 'demo_user',
          user_id: 'demo_user',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          generated_images: [],
          feedback: [],
          api_error: true
        }
      ];
      
      return exampleMaterials;
    }
    
    throw error;
  }
}

export async function getMaterial(id: string): Promise<Material> {
  try {
    const response = await api.get(`/materials/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching material with ID ${id}:`, error);
    // For connection errors, return a placeholder material
    if (error.isConnectionError) {
      return {
        id: id,
        title: 'Connection Error',
        description: 'Could not connect to the API server. Please check your connection and try again.',
        stage: MaterialStage.IDEA,
        status: MaterialStatus.DRAFT,
        keywords: [],
        feedback: [],
        generated_images: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        company_id: 'error',
        user_id: 'error',
        api_error: true
      };
    }
    throw error;
  }
}

export async function createMaterial(data: MaterialCreationFormData): Promise<Material> {
  try {
    const payload = {
      ...data,
      stage: MaterialStage.IDEA,
      status: MaterialStatus.DRAFT,
    };
    
    const response = await api.post('/materials', payload);
    return response.data;
  } catch (error) {
    console.error('Error creating material:', error);
    
    // Special handling for the mock database error
    if (error.response?.status === 500 && 
        (error.response?.data?.detail?.includes("SimpleMockDatabase") || 
         error.response?.data?.detail?.includes("not subscriptable"))) {
      console.log('Detected mock database error - returning fake material for demo');
      // Create a fake material for demo purposes
      return {
        id: `mock-${Date.now()}`,
        title: data.title || 'Mock Material',
        description: data.description || 'Created in demonstration mode',
        campaign_objective: data.campaign_objective || 'Demo',
        target_audience: data.target_audience || 'Test users',
        keywords: data.keywords || ['mock', 'demo'],
        stage: MaterialStage.IDEA,
        status: MaterialStatus.DRAFT,
        feedback: [],
        generated_images: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        company_id: 'test_company',
        user_id: 'demo_user',
        api_error: true // Add a flag to indicate this is from an API error
      };
    }
    
    throw error;
  }
}

export async function updateMaterial(id: string, data: Partial<Material>): Promise<Material> {
  const response = await api.put(`/materials/${id}`, data);
  return response.data;
}

export async function addGeneratedImage(
  materialId: string, 
  url: string, 
  prompt: string, 
  aiProvider: string, 
  generationParams: Record<string, unknown>
): Promise<Material> {
  const response = await api.post(`/materials/${materialId}/images`, {
    url,
    prompt,
    ai_provider: aiProvider,
    generation_params: generationParams
  });
  return response.data;
}

export async function selectImage(materialId: string, imageUrl: string): Promise<Material> {
  const response = await api.post(`/materials/${materialId}/select-image`, {
    image_url: imageUrl
  });
  return response.data;
}

export async function addFeedback(materialId: string, comment: string): Promise<Material> {
  const response = await api.post(`/materials/${materialId}/feedback`, {
    comment
  });
  return response.data;
}

export async function updateStage(
  materialId: string, 
  stage: MaterialStage, 
  status: MaterialStatus = MaterialStatus.IN_PROGRESS
): Promise<Material> {
  const response = await api.post(`/materials/${materialId}/stage`, {
    stage,
    status
  });
  return response.data;
}
