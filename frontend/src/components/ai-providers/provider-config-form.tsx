"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface ProviderConfig {
  id: string;
  name: string;
  apiKey?: string;
  selectedModel?: string;
  modelOptions?: string[];
  maxTokens?: number;
  temperature?: number;
  quality?: string;
  size?: string;
  style?: string;
  isActive?: boolean;
  customOptions?: Record<string, any>;
}

interface ProviderConfigFormProps {
  provider: ProviderConfig;
  onSave: (config: ProviderConfig) => Promise<void>;
  onTest: (config: ProviderConfig) => Promise<boolean>;
  saving?: boolean;
  testing?: boolean;
}

const OPENAI_MODELS = [
  "dall-e-3",
  "dall-e-2"
];

const OPENAI_SIZES = {
  "dall-e-3": ["1024x1024", "1024x1792", "1792x1024"],
  "dall-e-2": ["256x256", "512x512", "1024x1024"]
};

const OPENAI_QUALITIES = ["standard", "hd"];
const OPENAI_STYLES = ["vivid", "natural"];

const STABILITY_MODELS = [
  "stable-diffusion-xl-1024-v1-0",
  "stable-diffusion-v1-6",
  "stable-diffusion-xl-beta-v2-2-2"
];

const STABILITY_SIZES = ["1024x1024", "1152x896", "896x1152", "1216x832", "832x1216"];

const REPLICATE_MODELS = [
  "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
  "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478"
];

const HUGGINGFACE_MODELS = [
  "runwayml/stable-diffusion-v1-5",
  "stabilityai/stable-diffusion-xl-base-1.0",
  "CompVis/stable-diffusion-v1-4"
];

export default function ProviderConfigForm({ 
  provider, 
  onSave, 
  onTest, 
  saving = false, 
  testing = false 
}: ProviderConfigFormProps) {
  const [config, setConfig] = useState<ProviderConfig>(provider);
  const [showApiKey, setShowApiKey] = useState(false);
  const [validationResult, setValidationResult] = useState<{ success?: boolean; error?: string } | null>(null);
  const [apiKeyChanged, setApiKeyChanged] = useState(false);
  const [originalApiKey, setOriginalApiKey] = useState(provider.apiKey);
  const [realApiKey, setRealApiKey] = useState<string | undefined>(provider.apiKey);

  useEffect(() => {
    console.log('ProviderConfigForm: provider prop changed', provider);
    setConfig(provider);
    setOriginalApiKey(provider.apiKey);
    setApiKeyChanged(false);
    
    // Only update realApiKey if the incoming provider has a non-masked API key
    if (provider.apiKey && !isMaskedApiKey(provider.apiKey)) {
      setRealApiKey(provider.apiKey);
    }
  }, [provider]);

  const updateConfig = (key: keyof ProviderConfig, value: any) => {
    if (key === 'apiKey') {
      setApiKeyChanged(true);
      setRealApiKey(value); // Store the real API key
    }
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const isMaskedApiKey = (apiKey: string | undefined): boolean => {
    return apiKey !== undefined && apiKey.includes('••••');
  };

  const getDisplayApiKey = (): string => {
    if (!config.apiKey) return '';
    if (isMaskedApiKey(config.apiKey) && !apiKeyChanged) {
      // If showing the masked key and user hasn't changed it, show empty when visible
      return showApiKey ? '' : config.apiKey;
    }
    return config.apiKey;
  };

  const getApiKeyPlaceholder = (providerId: string): string => {
    if (isMaskedApiKey(originalApiKey) && !apiKeyChanged) {
      return showApiKey ? 'Enter new API key to change' : '••••••••••••••••';
    }
    
    switch (providerId) {
      case 'openai':
        return 'sk-...';
      case 'stability':
        return 'sk-...';
      case 'replicate':
        return 'r8_...';
      case 'huggingface':
        return 'hf_...';
      default:
        return 'Enter your API key';
    }
  };

  const handleSave = async () => {
    try {
      console.log('ProviderConfigForm: saving config', config);
      
      // Create config with real API key
      const configToSave = { ...config };
      if (realApiKey) {
        configToSave.apiKey = realApiKey;
      }
      
      console.log('ProviderConfigForm: saving config with real API key');
      const savedConfig = await onSave(configToSave);
      console.log('ProviderConfigForm: save successful, result:', savedConfig);
      setValidationResult({ success: true });
      setApiKeyChanged(false); // Reset the changed flag after successful save
      
      // Update local state with the saved configuration
      if (savedConfig) {
        console.log('ProviderConfigForm: updating local config state');
        setConfig(prev => ({
          ...prev,
          ...savedConfig,
          // Keep the real API key in our local state, but don't show it in the display
          apiKey: isMaskedApiKey(savedConfig.apiKey) ? prev.apiKey : savedConfig.apiKey
        }));
      }
    } catch (error) {
      console.log('ProviderConfigForm: save failed', error);
      setValidationResult({ 
        success: false, 
        error: error instanceof Error ? error.message : 'Save failed' 
      });
    }
  };

  const handleTest = async () => {
    try {
      // Create test config with real API key
      const configToTest = { ...config };
      if (realApiKey) {
        configToTest.apiKey = realApiKey;
      }
      
      console.log('ProviderConfigForm: testing config with real API key');
      const success = await onTest(configToTest);
      setValidationResult({ 
        success, 
        error: success ? undefined : 'Test failed - check your configuration' 
      });
    } catch (error) {
      setValidationResult({ 
        success: false, 
        error: error instanceof Error ? error.message : 'Test failed' 
      });
    }
  };

  const renderProviderSpecificFields = () => {
    switch (config.id) {
      case "openai":
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="model">Model</Label>
              <Select 
                value={config.selectedModel || "dall-e-3"} 
                onValueChange={(value) => updateConfig('selectedModel', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent>
                  {OPENAI_MODELS.map(model => (
                    <SelectItem key={model} value={model}>{model}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="size">Image Size</Label>
              <Select 
                value={config.size || "1024x1024"} 
                onValueChange={(value) => updateConfig('size', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select size" />
                </SelectTrigger>
                <SelectContent>
                  {(OPENAI_SIZES[config.selectedModel as keyof typeof OPENAI_SIZES] || OPENAI_SIZES["dall-e-3"]).map(size => (
                    <SelectItem key={size} value={size}>{size}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="quality">Quality</Label>
              <Select 
                value={config.quality || "standard"} 
                onValueChange={(value) => updateConfig('quality', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select quality" />
                </SelectTrigger>
                <SelectContent>
                  {OPENAI_QUALITIES.map(quality => (
                    <SelectItem key={quality} value={quality}>
                      {quality} {quality === "hd" ? "(2x cost)" : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="style">Style</Label>
              <Select 
                value={config.style || "vivid"} 
                onValueChange={(value) => updateConfig('style', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select style" />
                </SelectTrigger>
                <SelectContent>
                  {OPENAI_STYLES.map(style => (
                    <SelectItem key={style} value={style}>{style}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        );

      case "stability":
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="model">Model</Label>
              <Select 
                value={config.selectedModel || STABILITY_MODELS[0]} 
                onValueChange={(value) => updateConfig('selectedModel', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent>
                  {STABILITY_MODELS.map(model => (
                    <SelectItem key={model} value={model}>{model}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="size">Image Size</Label>
              <Select 
                value={config.size || "1024x1024"} 
                onValueChange={(value) => updateConfig('size', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select size" />
                </SelectTrigger>
                <SelectContent>
                  {STABILITY_SIZES.map(size => (
                    <SelectItem key={size} value={size}>{size}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="cfg_scale">CFG Scale</Label>
              <Input
                type="number"
                min="1"
                max="35"
                value={config.customOptions?.cfg_scale || 7}
                onChange={(e) => updateConfig('customOptions', { 
                  ...config.customOptions, 
                  cfg_scale: parseFloat(e.target.value) 
                })}
              />
              <p className="text-sm text-gray-500">
                How strictly the diffusion process adheres to the prompt text (1-35)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="steps">Steps</Label>
              <Input
                type="number"
                min="10"
                max="150"
                value={config.customOptions?.steps || 30}
                onChange={(e) => updateConfig('customOptions', { 
                  ...config.customOptions, 
                  steps: parseInt(e.target.value) 
                })}
              />
              <p className="text-sm text-gray-500">
                Number of diffusion steps to run (10-150)
              </p>
            </div>
          </div>
        );

      case "replicate":
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="model">Model</Label>
              <Select 
                value={config.selectedModel || REPLICATE_MODELS[0]} 
                onValueChange={(value) => updateConfig('selectedModel', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent>
                  {REPLICATE_MODELS.map(model => (
                    <SelectItem key={model} value={model}>
                      {model.split('/')[1]?.split(':')[0] || model}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="num_inference_steps">Inference Steps</Label>
              <Input
                type="number"
                min="1"
                max="100"
                value={config.customOptions?.num_inference_steps || 20}
                onChange={(e) => updateConfig('customOptions', { 
                  ...config.customOptions, 
                  num_inference_steps: parseInt(e.target.value) 
                })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="guidance_scale">Guidance Scale</Label>
              <Input
                type="number"
                min="1"
                max="20"
                step="0.1"
                value={config.customOptions?.guidance_scale || 7.5}
                onChange={(e) => updateConfig('customOptions', { 
                  ...config.customOptions, 
                  guidance_scale: parseFloat(e.target.value) 
                })}
              />
            </div>
          </div>
        );

      case "huggingface":
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="model">Model</Label>
              <Select 
                value={config.selectedModel || HUGGINGFACE_MODELS[0]} 
                onValueChange={(value) => updateConfig('selectedModel', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent>
                  {HUGGINGFACE_MODELS.map(model => (
                    <SelectItem key={model} value={model}>{model}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="use_cache">Use Cache</Label>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="use_cache"
                  checked={config.customOptions?.use_cache !== false}
                  onChange={(e) => updateConfig('customOptions', { 
                    ...config.customOptions, 
                    use_cache: e.target.checked 
                  })}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <Label htmlFor="use_cache" className="text-sm">
                  Use cached results for faster response
                </Label>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const getSetupInstructions = (providerId: string) => {
    const instructions = {
      openai: {
        url: "https://platform.openai.com/api-keys",
        steps: [
          "Go to OpenAI Platform",
          "Sign in to your account",
          "Navigate to API Keys",
          "Click 'Create new secret key'",
          "Copy and paste the key below"
        ]
      },
      stability: {
        url: "https://platform.stability.ai/account/keys",
        steps: [
          "Go to Stability AI Platform",
          "Sign in to your account",
          "Navigate to API Keys",
          "Generate a new API key",
          "Copy and paste the key below"
        ]
      },
      replicate: {
        url: "https://replicate.com/account/api-tokens",
        steps: [
          "Go to Replicate",
          "Sign in to your account",
          "Navigate to API tokens",
          "Create a new token",
          "Copy and paste the token below"
        ]
      },
      huggingface: {
        url: "https://huggingface.co/settings/tokens",
        steps: [
          "Go to Hugging Face",
          "Sign in to your account",
          "Navigate to Access Tokens",
          "Create a new token with 'read' role",
          "Copy and paste the token below"
        ]
      }
    };

    return instructions[providerId as keyof typeof instructions];
  };

  const setupInstructions = getSetupInstructions(config.id);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>{config.name} Configuration</span>
          <Badge variant={config.isActive ? "default" : "secondary"}>
            {config.isActive ? "Active" : "Inactive"}
          </Badge>
        </CardTitle>
        <CardDescription>
          Configure your {config.name} settings and API credentials
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Setup Instructions */}
        {setupInstructions && (
          <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">Setup Instructions</h4>
            <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800 mb-3">
              {setupInstructions.steps.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ol>
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.open(setupInstructions.url, '_blank')}
            >
              📄 Open {config.name} Dashboard
            </Button>
          </div>
        )}

        {/* API Key */}
        <div className="space-y-2">
          <Label htmlFor="apiKey">API Key *</Label>
          <div className="flex space-x-2">
            <div className="flex-1">
              <Input
                id="apiKey"
                type={showApiKey ? "text" : "password"}
                placeholder={getApiKeyPlaceholder(config.id)}
                value={getDisplayApiKey()}
                onChange={(e) => updateConfig('apiKey', e.target.value)}
              />
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setShowApiKey(!showApiKey)}
            >
              {showApiKey ? "👁️" : "🙈"}
            </Button>
          </div>
          <div className="flex items-center space-x-2">
            <p className="text-sm text-gray-500">
              Your API key is stored securely and never shared
            </p>
            {isMaskedApiKey(originalApiKey) && !apiKeyChanged && (
              <Badge variant="secondary" className="text-xs">
                Configured
              </Badge>
            )}
          </div>
        </div>

        {/* Provider-specific configuration */}
        {renderProviderSpecificFields()}

        {/* Active Toggle */}
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="isActive"
            checked={config.isActive !== false}
            onChange={(e) => updateConfig('isActive', e.target.checked)}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <Label htmlFor="isActive">
            Enable this provider for image generation
          </Label>
        </div>

        {/* Validation Result */}
        {validationResult && (
          <Alert className={validationResult.success ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"}>
            <AlertDescription className={validationResult.success ? "text-green-800" : "text-red-800"}>
              {validationResult.success ? (
                <span className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Configuration saved successfully!
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <span className="text-red-500">⚠</span>
                  {validationResult.error}
                </span>
              )}
            </AlertDescription>
          </Alert>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-3 pt-4">
          <Button
            onClick={handleTest}
            variant="outline"
            disabled={testing || !config.apiKey}
          >
            {testing ? "🔄 Testing..." : "🧪 Test Connection"}
          </Button>
          <Button
            onClick={handleSave}
            disabled={saving || !config.apiKey}
          >
            {saving ? "💾 Saving..." : "💾 Save Configuration"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
