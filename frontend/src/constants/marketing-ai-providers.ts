import { AIProviderConfig, MarketingFeature } from "@/types";

// Curated AI providers specifically optimized for marketing material generation
export const MARKETING_AI_PROVIDERS: AIProviderConfig[] = [
  // 🎨 TOP TIER - IMAGE GENERATION SPECIALISTS
  {
    name: "DALL-E 3 (OpenAI)",
    id: "dalle3",
    logo: "/ai-providers/openai.svg",
    isConfigured: false,
    isActive: false,
    priority: 1,
    supportedFeatures: ['image_generation', 'text_generation', 'social_media', 'banner_ads'],
    marketingCapabilities: {
      imageGeneration: true,
      textGeneration: true,
      logoDesign: true,
      socialMediaAssets: true,
      bannerAds: true,
      productShots: true,
      brandConsistency: true,
    },
    configurationStatus: 'not_configured',
    configurationSteps: [
      {
        id: 'api_key',
        title: 'Add API Key',
        description: 'Enter your OpenAI API key to enable DALL-E 3',
        isCompleted: false,
        isRequired: true,
        helpUrl: 'https://platform.openai.com/api-keys',
        action: 'api_key'
      },
      {
        id: 'model_selection',
        title: 'Select Model',
        description: 'Choose DALL-E 3 for best marketing image quality',
        isCompleted: false,
        isRequired: true,
        action: 'model_selection'
      },
      {
        id: 'connection_test',
        title: 'Test Connection',
        description: 'Verify your setup with a test image generation',
        isCompleted: false,
        isRequired: true,
        action: 'connection_test'
      }
    ],
    models: ['dall-e-3', 'dall-e-2'],
    defaultModel: 'dall-e-3',
    pricing: {
      tier: 'paid',
      paidPlans: [
        {
          name: "DALL-E 3 HD",
          pricePerImage: 0.08,
          currency: "USD",
          description: "$0.08 per image (1024×1024, HD quality)"
        },
        {
          name: "DALL-E 3 Standard",
          pricePerImage: 0.04,
          currency: "USD",
          description: "$0.04 per image (1024×1024, standard quality)"
        }
      ],
      websiteUrl: "https://openai.com/pricing"
    }
  },
  
  {
    name: "Midjourney",
    id: "midjourney",
    logo: "/ai-providers/midjourney.svg",
    isConfigured: false,
    isActive: false,
    priority: 2,
    supportedFeatures: ['image_generation', 'logo_design', 'social_media', 'brand_consistency'],
    marketingCapabilities: {
      imageGeneration: true,
      textGeneration: false,
      logoDesign: true,
      socialMediaAssets: true,
      bannerAds: true,
      productShots: true,
      brandConsistency: true,
    },
    configurationStatus: 'not_configured',
    configurationSteps: [
      {
        id: 'subscription',
        title: 'Subscribe to Midjourney',
        description: 'Get a Midjourney subscription for commercial use',
        isCompleted: false,
        isRequired: true,
        helpUrl: 'https://docs.midjourney.com/docs/plans',
        action: 'api_key'
      },
      {
        id: 'discord_setup',
        title: 'Discord Integration',
        description: 'Set up Discord bot integration for API access',
        isCompleted: false,
        isRequired: true,
        action: 'feature_setup'
      }
    ],
    pricing: {
      tier: 'paid',
      paidPlans: [
        {
          name: "Basic Plan",
          monthlyFee: 10,
          currency: "USD",
          description: "$10/month for ~200 image generations"
        },
        {
          name: "Standard Plan",
          monthlyFee: 30,
          currency: "USD",
          description: "$30/month for ~900 image generations"
        },
        {
          name: "Pro Plan",
          monthlyFee: 60,
          currency: "USD",
          description: "$60/month for ~1800 generations + stealth mode"
        }
      ],
      websiteUrl: "https://docs.midjourney.com/docs/plans"
    }
  },

  {
    name: "Stability AI (SDXL)",
    id: "stability",
    logo: "/ai-providers/stability.svg",
    isConfigured: false,
    isActive: false,
    priority: 3,
    supportedFeatures: ['image_generation', 'product_photography', 'banner_ads'],
    marketingCapabilities: {
      imageGeneration: true,
      textGeneration: false,
      logoDesign: true,
      socialMediaAssets: true,
      bannerAds: true,
      productShots: true,
      brandConsistency: false,
    },
    configurationStatus: 'not_configured',
    configurationSteps: [
      {
        id: 'api_key',
        title: 'Get API Key',
        description: 'Sign up for Stability AI API access',
        isCompleted: false,
        isRequired: true,
        helpUrl: 'https://platform.stability.ai/account/keys',
        action: 'api_key'
      },
      {
        id: 'model_selection',
        title: 'Choose Model',
        description: 'Select SDXL 1.0 for best marketing results',
        isCompleted: false,
        isRequired: true,
        action: 'model_selection'
      }
    ],
    models: ['stable-diffusion-xl-1024-v1-0', 'stable-diffusion-v1-6'],
    defaultModel: 'stable-diffusion-xl-1024-v1-0',
    pricing: {
      tier: 'freemium',
      freeQuota: {
        imagesPerMonth: 25,
        description: "25 free images per month for new users"
      },
      paidPlans: [
        {
          name: "Starter",
          pricePerImage: 0.04,
          currency: "USD",
          description: "$0.04 per image generation"
        },
        {
          name: "Professional",
          monthlyFee: 20,
          currency: "USD",
          description: "$20/month for 3,000 images"
        }
      ],
      websiteUrl: "https://stability.ai/pricing"
    }
  },

  // 🚀 FREEMIUM OPTIONS
  {
    name: "Leonardo AI",
    id: "leonardo",
    logo: "/ai-providers/leonardo.svg",
    isConfigured: false,
    isActive: false,
    priority: 4,
    supportedFeatures: ['image_generation', 'social_media', 'product_photography'],
    marketingCapabilities: {
      imageGeneration: true,
      textGeneration: false,
      logoDesign: true,
      socialMediaAssets: true,
      bannerAds: true,
      productShots: true,
      brandConsistency: false,
    },
    configurationStatus: 'not_configured',
    configurationSteps: [
      {
        id: 'account_setup',
        title: 'Create Account',
        description: 'Sign up for free Leonardo AI account',
        isCompleted: false,
        isRequired: true,
        helpUrl: 'https://leonardo.ai/auth/sign-up',
        action: 'api_key'
      },
      {
        id: 'api_access',
        title: 'API Access',
        description: 'Generate API key from your dashboard',
        isCompleted: false,
        isRequired: true,
        action: 'api_key'
      }
    ],
    pricing: {
      tier: 'freemium',
      freeQuota: {
        imagesPerMonth: 150,
        description: "150 free tokens daily (≈30 images)"
      },
      paidPlans: [
        {
          name: "Apprentice",
          monthlyFee: 10,
          currency: "USD",
          description: "$10/month for 8,500 tokens monthly"
        },
        {
          name: "Artisan",
          monthlyFee: 24,
          currency: "USD",
          description: "$24/month for 25,000 tokens monthly"
        }
      ],
      websiteUrl: "https://leonardo.ai/pricing"
    }
  },

  {
    name: "Replicate",
    id: "replicate",
    logo: "/ai-providers/replicate.svg",
    isConfigured: false,
    isActive: false,
    priority: 5,
    supportedFeatures: ['image_generation', 'batch_processing'],
    marketingCapabilities: {
      imageGeneration: true,
      textGeneration: true,
      logoDesign: false,
      socialMediaAssets: true,
      bannerAds: false,
      productShots: true,
      brandConsistency: false,
    },
    configurationStatus: 'not_configured',
    configurationSteps: [
      {
        id: 'api_token',
        title: 'Get API Token',
        description: 'Create account and generate API token',
        isCompleted: false,
        isRequired: true,
        helpUrl: 'https://replicate.com/account/api-tokens',
        action: 'api_key'
      },
      {
        id: 'model_selection',
        title: 'Select Models',
        description: 'Choose from SDXL, FLUX, or other image models',
        isCompleted: false,
        isRequired: true,
        action: 'model_selection'
      }
    ],
    models: ['stability-ai/sdxl', 'black-forest-labs/flux-schnell', 'lucataco/realistic-vision-v5.1'],
    defaultModel: 'stability-ai/sdxl',
    pricing: {
      tier: 'freemium',
      freeQuota: {
        description: "Free trial credits for new users"
      },
      paidPlans: [
        {
          name: "Pay-per-use",
          pricePerRequest: 0.0023,
          currency: "USD",
          description: "Starting at $0.0023 per prediction"
        }
      ],
      websiteUrl: "https://replicate.com/pricing"
    }
  },

  // 💡 BUDGET-FRIENDLY OPTIONS
  {
    name: "Hugging Face",
    id: "huggingface",
    logo: "/ai-providers/huggingface.svg",
    isConfigured: false,
    isActive: false,
    priority: 6,
    supportedFeatures: ['image_generation', 'text_generation'],
    marketingCapabilities: {
      imageGeneration: true,
      textGeneration: true,
      logoDesign: false,
      socialMediaAssets: true,
      bannerAds: false,
      productShots: false,
      brandConsistency: false,
    },
    configurationStatus: 'not_configured',
    configurationSteps: [
      {
        id: 'account_creation',
        title: 'Create Account',
        description: 'Sign up for free Hugging Face account',
        isCompleted: false,
        isRequired: true,
        helpUrl: 'https://huggingface.co/join',
        action: 'api_key'
      },
      {
        id: 'api_token',
        title: 'Generate Token',
        description: 'Create access token for API usage',
        isCompleted: false,
        isRequired: true,
        action: 'api_key'
      }
    ],
    models: ['stabilityai/stable-diffusion-xl-base-1.0', 'runwayml/stable-diffusion-v1-5'],
    defaultModel: 'stabilityai/stable-diffusion-xl-base-1.0',
    pricing: {
      tier: 'freemium',
      freeQuota: {
        requestsPerMonth: 1000,
        description: "1,000 free API requests per month"
      },
      paidPlans: [
        {
          name: "Pro",
          monthlyFee: 9,
          currency: "USD",
          description: "$9/month for unlimited requests"
        }
      ],
      websiteUrl: "https://huggingface.co/pricing"
    }
  },

  // 🆓 FREE/TESTING PROVIDERS
  {
    name: "Basic Test Provider",
    id: "free-test-provider",
    logo: "/ai-providers/test.svg",
    isConfigured: true,  // Pre-configured for testing
    isActive: true,      // Always active
    priority: 11,        // Lower priority
    supportedFeatures: ['image_generation', 'text_generation'],
    marketingCapabilities: {
      imageGeneration: true,
      textGeneration: true,
      logoDesign: false,
      socialMediaAssets: true,
      bannerAds: true,
      productShots: false,
      brandConsistency: false,
    },
    configurationStatus: 'configured',
    configurationSteps: [
      {
        id: 'ready',
        title: 'Ready to Use',
        description: 'Basic test provider with random images',
        isCompleted: true,
        isRequired: false,
        action: 'none'
      }
    ],
    pricing: {
      tier: 'free',
      freeQuota: {
        imagesPerMonth: 1000,
        description: 'Unlimited basic test images for development'
      },
      websiteUrl: '#'
    }
  },

  {
    name: "Context-Aware Test Provider",
    id: "context-aware-test-provider",
    logo: "/ai-providers/context-aware.svg",
    isConfigured: true,  // Pre-configured for testing
    isActive: true,      // Always active
    priority: 10,        // Higher priority than basic
    supportedFeatures: ['image_generation', 'social_media', 'banner_ads'],
    marketingCapabilities: {
      imageGeneration: true,
      textGeneration: false,
      logoDesign: true,
      socialMediaAssets: true,
      bannerAds: true,
      productShots: true,
      brandConsistency: true,
    },
    configurationStatus: 'configured',
    configurationSteps: [
      {
        id: 'ready',
        title: 'Ready to Use',
        description: 'Advanced test provider with brand color and context integration',
        isCompleted: true,
        isRequired: false,
        action: 'connection_test'
      }
    ],
    pricing: {
      tier: 'free',
      freeQuota: {
        imagesPerMonth: 1000,
        description: 'Unlimited context-aware test images with brand integration'
      },
      websiteUrl: '#'
    }
  }
];

// Helper function to get providers by capability
export const getProvidersByCapability = (capability: keyof NonNullable<AIProviderConfig['marketingCapabilities']>) => {
  return MARKETING_AI_PROVIDERS.filter(provider => 
    provider.marketingCapabilities?.[capability] === true
  );
};

// Helper function to get configured providers only
export const getConfiguredProviders = () => {
  return MARKETING_AI_PROVIDERS.filter(provider => 
    provider.configurationStatus === 'configured'
  );
};

// Helper function to get providers by tier
export const getProvidersByTier = (tier: 'free' | 'freemium' | 'paid') => {
  return MARKETING_AI_PROVIDERS.filter(provider => 
    provider.pricing.tier === tier
  );
};
