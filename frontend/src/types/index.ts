export enum MaterialStage {
  IDEA = 'idea',
  REFINEMENT = 'refinement',
  FINALIZATION = 'finalization',
}

export enum MaterialStatus {
  DRAFT = 'draft',
  IN_PROGRESS = 'in_progress',
  READY_FOR_REVIEW = 'ready_for_review',
  COMPLETED = 'completed',
  ARCHIVED = 'archived',
}

export interface GeneratedImage {
  url: string;
  prompt: string;
  ai_provider: string;
  generation_params: Record<string, unknown>;
  created_at: string;
}

export interface Material {
  id: string;
  title: string;
  description?: string;
  target_audience?: string;
  campaign_objective?: string;
  keywords: string[];
  stage: MaterialStage;
  status: MaterialStatus;
  company_id: string;
  created_by?: string; // Make optional for error cases
  user_id?: string;    // Alternative to created_by
  created_at: string;
  updated_at: string;
  generated_images: GeneratedImage[];
  selected_image?: string;
  feedback: Feedback[];
  version_history?: VersionHistory[]; // Make optional for error cases
  api_error?: boolean; // Flag to indicate API connection error
}

export interface Feedback {
  user_id: string;
  comment: string;
  created_at: string;
}

export interface VersionHistory {
  version: number;
  changes: Record<string, unknown>;
  changed_by: string;
  changed_at: string;
}

export interface Company {
  id: string;
  name: string;
  description?: string;
  logo_url?: string;
  logo_file?: File; // Added for handling file uploads
  brand_colors: string[];
  active: boolean;
  created_at?: string;
  updated_at?: string;
  api_error?: boolean; // Flag to indicate API connection error
}

export interface User {
  id: string;
  email: string;
  name: string;
  company_id: string;
  role: 'admin' | 'user';
  active: boolean;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface MaterialCreationFormData {
  title: string;
  description?: string;
  target_audience?: string;
  campaign_objective?: string;
  keywords: string[];
}

export interface AIProviderConfig {
  name: string;
  id: string;
  logo?: string;
  apiKey?: string;
  baseUrl?: string;
  models?: string[];
  defaultModel?: string;
  isConfigured?: boolean;
  modelOptions?: string[];
  selectedModel?: string;
  maxTokens?: number;
  temperature?: number;
  isActive?: boolean;
  isEnabled?: boolean;
  priority?: number;
  supportedFeatures?: string[];
  rateLimit?: {
    requestsPerMinute: number;
    tokensPerMinute: number;
  };
  pricing: {
    tier: 'free' | 'freemium' | 'paid';
    freeQuota?: {
      requestsPerMonth?: number;
      tokensPerMonth?: number;
      description?: string;
    };
    paidPlans?: {
      name: string;
      pricePerToken?: number;
      pricePerRequest?: number;
      monthlyFee?: number;
      currency: string;
      description?: string;
    }[];
    websiteUrl?: string;
  };
}

export interface ConnectionInfo {
  isOnline: boolean;
  apiAccessible: boolean;
  apiConnected: boolean;
  apiPort: number | null;
  authWorking: boolean;
  lastChecked: Date;
  error: string | null;
}

export interface APIStatus {
  status: 'connected' | 'disconnected' | 'offline' | 'wrong-port' | 'auth-issue';
  statusText: string;
  statusColor: string;
  message: string;
}

export interface IdeaGenerationFormData {
  title: string;
  description: string;
  target_audience: string;
  campaign_objective: string;
  keywords: string[];
}

export interface RefinementFormData {
  prompt: string;
  aiProvider: string;
  generationParams: Record<string, unknown>;
}

export interface FinalizationFormData {
  selectedImage: string;
  finalFeedback: string;
}
