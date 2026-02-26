import api from './api';
import { getErrorLogContext } from './api';
import { Material, MaterialCreationFormData, MaterialStage, MaterialStatus } from '@/types';

// In-memory cache for list response only (no localStorage). Short TTL to avoid stale data.
const CACHE_TTL_MS = 30_000;
let listCache: { data: Material[]; timestamp: number } | null = null;

function isListCacheValid(): boolean {
  return listCache !== null && Date.now() - listCache.timestamp < CACHE_TTL_MS;
}

function invalidateListCache(): void {
  listCache = null;
}

export async function getMaterials(
  stage?: MaterialStage,
  status?: MaterialStatus,
  skip = 0,
  limit = 100,
  forceRefresh = false
): Promise<Material[]> {
  const cacheKey = !stage && !status && skip === 0;
  if (!forceRefresh && cacheKey && isListCacheValid()) {
    return listCache!.data;
  }

  try {
    let url = `materials?skip=${skip}&limit=${limit}`;
    if (stage) url += `&stage=${stage}`;
    if (status) url += `&status=${status}`;

    const response = await api.get(url, { timeout: 30000 });
    const materialsData = Array.isArray(response.data) ? response.data : [];
    if (!Array.isArray(response.data)) {
      console.warn('[Materials Service] API returned non-array:', response.data);
    }

    if (cacheKey) {
      listCache = { data: materialsData, timestamp: Date.now() };
    }
    return materialsData;
  } catch (error: unknown) {
    const { correlation_id, user_message } = getErrorLogContext(error);
    console.error('[Materials Service] Error fetching materials:', user_message, correlation_id ? `(${correlation_id})` : '');
    throw error;
  }
}

export async function getMaterial(id: string): Promise<Material> {
  try {
    const response = await api.get(`materials/${id}`);
    return response.data;
  } catch (error: unknown) {
    const { correlation_id, user_message } = getErrorLogContext(error);
    console.error('[Materials Service] Error fetching material:', user_message, correlation_id ? `(${correlation_id})` : '');
    throw error;
  }
}

export async function createMaterial(data: MaterialCreationFormData): Promise<Material> {
  try {
    const materialData = {
      ...data,
      stage: MaterialStage.IDEA,
      status: MaterialStatus.DRAFT,
    };
    const response = await api.post('materials', materialData);
    invalidateListCache();
    return response.data;
  } catch (error: unknown) {
    const { correlation_id, user_message } = getErrorLogContext(error);
    console.error('[Materials Service] Error creating material:', user_message, correlation_id ? `(${correlation_id})` : '');
    throw error;
  }
}

export async function updateMaterial(id: string, data: Partial<Material>): Promise<Material> {
  try {
    const response = await api.put(`materials/${id}`, data);
    if (listCache) {
      const index = listCache.data.findIndex((m) => m.id === id);
      if (index >= 0) listCache.data[index] = response.data;
    }
    return response.data;
  } catch (error: unknown) {
    const { correlation_id, user_message } = getErrorLogContext(error);
    console.error('[Materials Service] Error updating material:', user_message, correlation_id ? `(${correlation_id})` : '');
    throw error;
  }
}

export async function deleteMaterial(id: string): Promise<void> {
  try {
    await api.delete(`materials/${id}`);
    invalidateListCache();
  } catch (error: unknown) {
    const { correlation_id, user_message } = getErrorLogContext(error);
    console.error('[Materials Service] Error deleting material:', user_message, correlation_id ? `(${correlation_id})` : '');
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
    const fullUrl = `materials/${materialId}/images?url=${encodeURIComponent(imageUrl)}&prompt=${encodeURIComponent(prompt)}&ai_provider=${encodeURIComponent(aiProvider)}&generation_params=${encodeURIComponent(JSON.stringify(generationParams))}`;
    const response = await api.post(fullUrl);
    invalidateListCache();
    return response.data;
  } catch (error: unknown) {
    const { correlation_id, user_message } = getErrorLogContext(error);
    console.error('[Materials Service] Error adding generated image:', user_message, correlation_id ? `(${correlation_id})` : '');
    throw error;
  }
}

// Select image for material
export async function selectImage(materialId: string, imageUrl: string): Promise<Material> {
  try {
    const response = await api.post(
      `materials/${materialId}/select-image?image_url=${encodeURIComponent(imageUrl)}`
    );
    invalidateListCache();
    return response.data;
  } catch (error: unknown) {
    const { correlation_id, user_message } = getErrorLogContext(error);
    console.error('[Materials Service] Error selecting image:', user_message, correlation_id ? `(${correlation_id})` : '');
    throw error;
  }
}

// Add feedback to material
export async function addFeedback(materialId: string, feedback: string): Promise<Material> {
  try {
    const response = await api.post(`materials/${materialId}/feedback`, { feedback });
    invalidateListCache();
    return response.data;
  } catch (error: unknown) {
    const { correlation_id, user_message } = getErrorLogContext(error);
    console.error('[Materials Service] Error adding feedback:', user_message, correlation_id ? `(${correlation_id})` : '');
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
    const response = await api.put(`materials/${materialId}`, { stage, status });
    invalidateListCache();
    if (listCache) {
      const index = listCache.data.findIndex((m) => m.id === materialId);
      if (index >= 0) listCache.data[index] = response.data;
    }
    return response.data;
  } catch (error: unknown) {
    const { correlation_id, user_message } = getErrorLogContext(error);
    console.error('[Materials Service] Error updating stage:', user_message, correlation_id ? `(${correlation_id})` : '');
    throw error;
  }
}
