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
  description?: string; // Legacy field for backward compatibility
  campaign_brief?: string; // New field: describes campaign strategy (what/who/why/when)
  target_audience?: string;
  campaign_objective?: string;
  creative_approach?: CreativeApproach; // Visual storytelling approach
  keywords: string[];
  campaign_date?: string | Date; // Target campaign date for seasonal context
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
  description?: string; // Legacy field for backward compatibility
  campaign_brief?: string; // New field: describes campaign strategy (what/who/why/when)
  target_audience?: string;
  campaign_objective?: string;
  creative_approach?: CreativeApproach; // Visual storytelling approach
  keywords: string[];
  campaign_date?: Date | string;
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
  
  // Marketing-specific capabilities
  supportedFeatures?: MarketingFeature[];
  marketingCapabilities?: {
    imageGeneration: boolean;
    textGeneration: boolean;
    logoDesign: boolean;
    socialMediaAssets: boolean;
    bannerAds: boolean;
    productShots: boolean;
    brandConsistency: boolean;
  };
  
  // Configuration status for UX guidance
  configurationStatus?: 'not_configured' | 'partial' | 'configured' | 'error';
  configurationSteps?: ConfigurationStep[];
  lastConnectionTest?: {
    status: 'success' | 'failed' | 'pending';
    timestamp: string;
    errorMessage?: string;
  };
  
  rateLimit?: {
    requestsPerMinute: number;
    tokensPerMinute: number;
  };
  pricing: {
    tier: 'free' | 'freemium' | 'paid';
    freeQuota?: {
      requestsPerMonth?: number;
      tokensPerMonth?: number;
      imagesPerMonth?: number;
      description?: string;
    };
    paidPlans?: {
      name: string;
      pricePerToken?: number;
      pricePerRequest?: number;
      pricePerImage?: number;
      monthlyFee?: number;
      currency: string;
      description?: string;
    }[];
    websiteUrl?: string;
  };
}

export type MarketingFeature = 
  | 'image_generation'
  | 'text_generation' 
  | 'logo_design'
  | 'social_media'
  | 'banner_ads'
  | 'product_photography'
  | 'brand_consistency'
  | 'batch_processing';

export interface ConfigurationStep {
  id: string;
  title: string;
  description: string;
  isCompleted: boolean;
  isRequired: boolean;
  helpUrl?: string;
  action?: 'api_key' | 'model_selection' | 'connection_test' | 'feature_setup';
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

// Creative approach for visual storytelling
export type CreativeApproach = 
  | "story_led"    // Show people in situations, tell stories through scenes
  | "concept_led"  // Show ideas through imagery, symbols, and clear visuals
  | "hybrid";      // Mix both approaches as needed (DEFAULT)

export interface IdeaGenerationFormData {
  title: string;
  description: string; // Legacy field for backward compatibility
  campaign_brief?: string; // New field: describes campaign strategy (what/who/why/when)
  target_audience: string;
  campaign_objective: string;
  creative_approach?: CreativeApproach; // Visual storytelling approach
  keywords: string[];
  campaign_date?: Date | string; // Target campaign date for seasonal context
}

// People preference modes for image generation
export type PeoplePreference = 
  | "auto"      // Let industry/context decide (DEFAULT)
  | "include"   // Force include people
  | "exclude"   // Force exclude people
  | "minimal";  // Product-focused with minimal people

// Conflict severity levels
export type ConflictSeverity = "none" | "low" | "medium" | "high";

// Conflict source information
export interface ConflictSource {
  source: "industry" | "material_context" | "seasonal" | "keywords" | "storytelling_approach";
  reason: string;
  suggestion: string;
  severity: ConflictSeverity;
}

// Conflict analysis result
export interface ConflictAnalysis {
  hasConflict: boolean;
  overallSeverity: ConflictSeverity;
  conflictingSources: ConflictSource[];
  recommendation: PeoplePreference;
}

// Refinement form data interface
export interface RefinementFormData {
  prompt: string;
  aiProvider: string;
  generationParams: Record<string, unknown>;
  peoplePreference?: PeoplePreference; // Smart 4-mode system (replaces includePeople)
}

export interface FinalizationFormData {
  selectedImage: string;
  finalFeedback: string;
}
