import { AIProviderConfig, ConfigurationStep } from "@/types";

export interface ProviderValidationResult {
  isValid: boolean;
  status: 'not_configured' | 'partial' | 'configured' | 'error';
  missingSteps: ConfigurationStep[];
  errors: string[];
  warnings: string[];
  nextAction?: {
    type: 'api_key' | 'model_selection' | 'connection_test' | 'feature_setup';
    title: string;
    description: string;
    helpUrl?: string;
  };
}

export class AIProviderValidator {
  /**
   * Validates a provider's configuration for marketing material generation
   */
  static async validateProvider(provider: AIProviderConfig): Promise<ProviderValidationResult> {
    const result: ProviderValidationResult = {
      isValid: false,
      status: 'not_configured',
      missingSteps: [],
      errors: [],
      warnings: []
    };

    // Special handling for free test provider
    if (provider.id === 'free-test-provider') {
      result.isValid = true;
      result.status = 'configured';
      return result;
    }

    // Check basic requirements
    if (!provider.apiKey && provider.id !== 'ollama' && provider.id !== 'lmstudio') {
      result.errors.push('API key is required');
      result.missingSteps.push({
        id: 'api_key',
        title: 'Add API Key',
        description: `Enter your ${provider.name} API key`,
        isCompleted: false,
        isRequired: true,
        action: 'api_key'
      });
    }

    // Check model selection for image generation
    if (provider.marketingCapabilities?.imageGeneration && !provider.selectedModel && !provider.defaultModel) {
      result.errors.push('Model selection is required for image generation');
      result.missingSteps.push({
        id: 'model_selection',
        title: 'Select Model',
        description: 'Choose an appropriate model for image generation',
        isCompleted: false,
        isRequired: true,
        action: 'model_selection'
      });
    }

    // Provider-specific validations
    switch (provider.id) {
      case 'dalle3':
        await this.validateOpenAI(provider, result);
        break;
      case 'midjourney':
        await this.validateMidjourney(provider, result);
        break;
      case 'stability':
        await this.validateStabilityAI(provider, result);
        break;
      case 'leonardo':
        await this.validateLeonardoAI(provider, result);
        break;
      case 'replicate':
        await this.validateReplicate(provider, result);
        break;
      case 'huggingface':
        await this.validateHuggingFace(provider, result);
        break;
    }

    // Determine overall status
    if (result.errors.length === 0) {
      if (result.warnings.length === 0) {
        result.status = 'configured';
        result.isValid = true;
      } else {
        result.status = 'partial';
        result.isValid = true;
      }
    } else {
      result.status = result.missingSteps.length > 0 ? 'not_configured' : 'error';
    }

    // Set next action
    if (result.missingSteps.length > 0) {
      const nextStep = result.missingSteps[0];
      result.nextAction = {
        type: nextStep.action!,
        title: nextStep.title,
        description: nextStep.description,
        helpUrl: nextStep.helpUrl
      };
    }

    return result;
  }

  private static async validateOpenAI(provider: AIProviderConfig, result: ProviderValidationResult) {
    if (provider.apiKey) {
      // Test API key format
      if (!provider.apiKey.startsWith('sk-')) {
        result.errors.push('Invalid OpenAI API key format. Should start with "sk-"');
      } else {
        try {
          // Test connection (mock for now)
          const isValid = await this.testOpenAIConnection(provider.apiKey);
          if (!isValid) {
            result.errors.push('API key authentication failed');
          }
        } catch (error) {
          result.warnings.push('Could not verify API key. Please test manually.');
        }
      }
    }

    // Check model availability
    if (provider.selectedModel && !['dall-e-3', 'dall-e-2'].includes(provider.selectedModel)) {
      result.warnings.push('Selected model may not be optimal for marketing materials');
    }
  }

  private static async validateMidjourney(provider: AIProviderConfig, result: ProviderValidationResult) {
    // Midjourney requires Discord integration
    if (!provider.apiKey) {
      result.errors.push('Discord bot token required for Midjourney integration');
    }

    result.warnings.push('Midjourney requires a subscription for commercial use');
  }

  private static async validateStabilityAI(provider: AIProviderConfig, result: ProviderValidationResult) {
    if (provider.apiKey) {
      if (!provider.apiKey.startsWith('sk-')) {
        result.errors.push('Invalid Stability AI API key format');
      }
    }

    // Check credits/quota
    result.warnings.push('Check your Stability AI credit balance before generating');
  }

  private static async validateLeonardoAI(provider: AIProviderConfig, result: ProviderValidationResult) {
    if (provider.apiKey) {
      // Leonardo uses different token format
      if (provider.apiKey.length < 20) {
        result.warnings.push('API token seems unusually short');
      }
    }
  }

  private static async validateReplicate(provider: AIProviderConfig, result: ProviderValidationResult) {
    if (provider.apiKey) {
      if (!provider.apiKey.startsWith('r8_')) {
        result.errors.push('Invalid Replicate API token format. Should start with "r8_"');
      }
    }
  }

  private static async validateHuggingFace(provider: AIProviderConfig, result: ProviderValidationResult) {
    if (provider.apiKey) {
      if (!provider.apiKey.startsWith('hf_')) {
        result.errors.push('Invalid Hugging Face token format. Should start with "hf_"');
      }
    }
  }

  /**
   * Mock connection test - in production, this would make actual API calls
   */
  private static async testOpenAIConnection(apiKey: string): Promise<boolean> {
    // Simulate API test
    return new Promise(resolve => {
      setTimeout(() => {
        // Mock: 80% success rate for demo
        resolve(Math.random() > 0.2);
      }, 1000);
    });
  }

  /**
   * Get user-friendly guidance for configuration
   */
  static getConfigurationGuidance(provider: AIProviderConfig): {
    title: string;
    description: string;
    steps: string[];
    estimatedTime: string;
    difficulty: 'easy' | 'medium' | 'hard';
  } {
    switch (provider.id) {
      case 'dalle3':
        return {
          title: 'Set up DALL-E 3 for Marketing',
          description: 'DALL-E 3 creates high-quality marketing images with precise text rendering',
          steps: [
            'Sign up for OpenAI account',
            'Add billing information', 
            'Generate API key',
            'Test with sample marketing prompt'
          ],
          estimatedTime: '5 minutes',
          difficulty: 'easy'
        };

      case 'stability':
        return {
          title: 'Configure Stability AI',
          description: 'Stable Diffusion XL for professional marketing visuals',
          steps: [
            'Create Stability AI account',
            'Verify email and add payment method',
            'Generate API key from dashboard',
            'Test image generation'
          ],
          estimatedTime: '10 minutes',
          difficulty: 'easy'
        };

      case 'midjourney':
        return {
          title: 'Setup Midjourney Integration',
          description: 'Premium AI art generator with exceptional quality',
          steps: [
            'Subscribe to Midjourney ($10+ plan required)',
            'Join Midjourney Discord server',
            'Set up Discord bot integration',
            'Configure API access'
          ],
          estimatedTime: '20 minutes',
          difficulty: 'hard'
        };

      default:
        return {
          title: `Configure ${provider.name}`,
          description: 'Set up your AI provider for marketing material generation',
          steps: [
            'Create account with provider',
            'Generate API key',
            'Configure settings',
            'Test connection'
          ],
          estimatedTime: '10 minutes',
          difficulty: 'medium'
        };
    }
  }
}
