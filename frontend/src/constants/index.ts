import { AIProviderConfig } from "@/types";

// Default AI providers with popular market options across free, freemium, and paid tiers
export const DEFAULT_AI_PROVIDERS: AIProviderConfig[] = [
  // FREE PROVIDERS
  {
    name: "Ollama (Local)",
    id: "ollama",
    logo: "/ai-providers/ollama.svg",
    isConfigured: false,
    isActive: false,
    pricing: {
      tier: 'free',
      freeQuota: {
        description: "Completely free - runs locally on your machine. Supports Llama 2, Code Llama, Mistral, and other open-source models"
      },
      websiteUrl: "https://ollama.ai"
    }
  },
  {
    name: "LM Studio",
    id: "lmstudio",
    logo: "/ai-providers/lmstudio.svg",
    isConfigured: false,
    isActive: false,
    pricing: {
      tier: 'free',
      freeQuota: {
        description: "Free local LLM runtime. Run any open-source model on your hardware"
      },
      websiteUrl: "https://lmstudio.ai"
    }
  },
  
  // FREEMIUM PROVIDERS
  {
    name: "Hugging Face",
    id: "huggingface",
    logo: "/ai-providers/huggingface.svg",
    isConfigured: false,
    isActive: false,
    pricing: {
      tier: 'freemium',
      freeQuota: {
        requestsPerMonth: 1000,
        description: "1,000 requests/month free for Inference API"
      },
      paidPlans: [
        {
          name: "Pro",
          monthlyFee: 9,
          currency: "USD",
          description: "$9/month for unlimited requests and priority access"
        }
      ],
      websiteUrl: "https://huggingface.co/pricing"
    }
  },
  {
    name: "Google Colab",
    id: "colab",
    logo: "/ai-providers/colab.svg",
    isConfigured: false,
    isActive: false,
    pricing: {
      tier: 'freemium',
      freeQuota: {
        description: "Free GPU/TPU access with usage limits. Run Gemini, open-source models"
      },
      paidPlans: [
        {
          name: "Colab Pro",
          monthlyFee: 9.99,
          currency: "USD",
          description: "$9.99/month for faster GPUs and longer runtimes"
        },
        {
          name: "Colab Pro+",
          monthlyFee: 49.99,
          currency: "USD",
          description: "$49.99/month for premium GPUs and background execution"
        }
      ],
      websiteUrl: "https://colab.research.google.com/signup"
    }
  },
  {
    name: "Replicate",
    id: "replicate",
    logo: "/ai-providers/replicate.svg",
    isConfigured: false,
    isActive: false,
    pricing: {
      tier: 'freemium',
      freeQuota: {
        description: "Free tier with limited usage. Pay-per-use for additional requests"
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
  
  // PAID PROVIDERS
  {
    name: "OpenAI",
    id: "openai",
    logo: "/ai-providers/openai.svg",
    isConfigured: false,
    isActive: false,
    pricing: {
      tier: 'paid',
      paidPlans: [
        {
          name: "GPT-4o",
          pricePerToken: 0.000005,
          currency: "USD",
          description: "$5 per 1M input tokens, $15 per 1M output tokens"
        },
        {
          name: "GPT-4 Turbo",
          pricePerToken: 0.00001,
          currency: "USD",
          description: "$10 per 1M input tokens, $30 per 1M output tokens"
        },
        {
          name: "DALL-E 3",
          pricePerRequest: 0.04,
          currency: "USD",
          description: "$0.04 per image (1024×1024)"
        }
      ],
      websiteUrl: "https://openai.com/pricing"
    }
  },
  {
    name: "Anthropic Claude",
    id: "anthropic",
    logo: "/ai-providers/anthropic.svg",
    isConfigured: false,
    isActive: false,
    pricing: {
      tier: 'paid',
      paidPlans: [
        {
          name: "Claude 3 Haiku",
          pricePerToken: 0.00000025,
          currency: "USD",
          description: "$0.25 per 1M input tokens, $1.25 per 1M output tokens"
        },
        {
          name: "Claude 3 Sonnet",
          pricePerToken: 0.000003,
          currency: "USD",
          description: "$3 per 1M input tokens, $15 per 1M output tokens"
        },
        {
          name: "Claude 3 Opus",
          pricePerToken: 0.000015,
          currency: "USD",
          description: "$15 per 1M input tokens, $75 per 1M output tokens"
        }
      ],
      websiteUrl: "https://www.anthropic.com/pricing"
    }
  },
  {
    name: "Stability AI",
    id: "stability",
    logo: "/ai-providers/stability.svg",
    isConfigured: false,
    isActive: false,
    pricing: {
      tier: 'paid',
      paidPlans: [
        {
          name: "Starter",
          pricePerRequest: 0.04,
          currency: "USD",
          description: "$0.04 per image generation"
        },
        {
          name: "Professional",
          monthlyFee: 20,
          currency: "USD",
          description: "$20/month for 3,000 images"
        },
        {
          name: "Enterprise",
          monthlyFee: 100,
          currency: "USD",
          description: "$100/month for 15,000 images + priority support"
        }
      ],
      websiteUrl: "https://stability.ai/pricing"
    }
  },
  {
    name: "Midjourney",
    id: "midjourney",
    logo: "/ai-providers/midjourney.svg",
    isConfigured: false,
    isActive: false,
    pricing: {
      tier: 'paid',
      paidPlans: [
        {
          name: "Basic",
          monthlyFee: 10,
          currency: "USD",
          description: "$10/month for ~200 generations"
        },
        {
          name: "Standard",
          monthlyFee: 30,
          currency: "USD",
          description: "$30/month for ~900 generations"
        },
        {
          name: "Pro",
          monthlyFee: 60,
          currency: "USD",
          description: "$60/month for ~1800 generations + stealth mode"
        }
      ],
      websiteUrl: "https://docs.midjourney.com/docs/plans"
    }
  }
];

export const MATERIAL_CREATION_STEPS = [
  {
    id: "idea",
    title: "Idea Generation",
    description: "Define the concept and target audience"
  },
  {
    id: "refinement",
    title: "Refinement",
    description: "Generate and refine visual content"
  },
  {
    id: "finalization",
    title: "Finalization",
    description: "Select final content and complete"
  }
];
