"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AIProviderConfig } from "@/types";
import { X, Check } from "lucide-react";
import { validateAPIKey, getProviderOptions } from "@/services/ai-providers";
import { ValidationMessage } from "@/components/ui/validation-message";
import { PricingBadge } from "@/components/ui/pricing-badge";

interface AIProviderDialogProps {
  provider: AIProviderConfig | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (provider: AIProviderConfig) => Promise<void>;
  translations: Record<string, any>;
}

// Simple modal component without external dependencies
const SimpleDialog = ({ 
  open, 
  onClose, 
  children 
}: { 
  open: boolean; 
  onClose: () => void; 
  children: React.ReactNode;
}) => {
  if (!open) return null;
  
  return (
    <div className="fixed inset-0 z-50">
      <div 
        className="fixed inset-0 bg-black/80" 
        onClick={onClose}
      />
      <div className="fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border border-gray-200 bg-white p-6 shadow-lg sm:rounded-lg md:w-full">
        {children}
      </div>
    </div>
  );
};

export function AIProviderDialog({
  provider,
  isOpen,
  onClose,
  onSave,
  translations
}: AIProviderDialogProps) {
  const t = translations;
  const [formData, setFormData] = useState<AIProviderConfig>({
    name: "",
    id: "",
    logo: "",
    apiKey: "",
    baseUrl: "",
    models: [],
    defaultModel: "",
    isEnabled: true,
    priority: 1,
    maxTokens: 4096,
    temperature: 0.7,
    supportedFeatures: [],
    rateLimit: {
      requestsPerMinute: 60,
      tokensPerMinute: 60000
    },
    pricing: {
      tier: 'paid',
      websiteUrl: ""
    }
  });

  const [validationStatus, setValidationStatus] = useState<{
    checked: boolean;
    valid: boolean;
    message: string;
  }>({
    checked: false,
    valid: false,
    message: ""
  });

  const [isValidating, setIsValidating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [fetchingModels, setFetchingModels] = useState(false);

  // Load form data when provider changes
  useEffect(() => {
    if (provider) {
      setFormData(provider);
    } else {
      // Reset form for new provider
      setFormData({
        name: "",
        id: "",
        logo: "",
        apiKey: "",
        baseUrl: "",
        models: [],
        defaultModel: "",
        isEnabled: true,
        priority: 1,
        maxTokens: 4096,
        temperature: 0.7,
        supportedFeatures: [],
        rateLimit: {
          requestsPerMinute: 60,
          tokensPerMinute: 60000
        },
        pricing: {
          tier: 'paid',
          websiteUrl: ""
        }
      });
    }
    setValidationStatus({
      checked: false,
      valid: false,
      message: ""
    });
  }, [provider]);

  const validateKey = async () => {
    if (!formData.apiKey || !formData.name) {
      setValidationStatus({
        checked: true,
        valid: false,
        message: "API key and provider name are required"
      });
      return;
    }

    setIsValidating(true);
    try {
      const result = await validateAPIKey(formData.name, formData.apiKey);
      setValidationStatus({
        checked: true,
        valid: result.valid,
        message: result.message || (result.valid ? "API key is valid" : "API key validation failed")
      });

      // If validation successful, try to fetch models
      if (result.valid) {
        setFetchingModels(true);
        try {
          const providerOptions = await getProviderOptions(formData.name);
          if (providerOptions.models && providerOptions.models.length > 0) {
            setFormData(prev => ({
              ...prev,
              models: providerOptions.models,
              defaultModel: prev.defaultModel || providerOptions.models[0]
            }));
          }
        } catch (error) {
          console.warn("Could not fetch models:", error);
        } finally {
          setFetchingModels(false);
        }
      }
    } catch (error) {
      setValidationStatus({
        checked: true,
        valid: false,
        message: error instanceof Error ? error.message : "Validation failed"
      });
    } finally {
      setIsValidating(false);
    }
  };

  const handleSave = async () => {
    if (!validationStatus.valid) {
      return;
    }

    setIsSaving(true);
    try {
      await onSave(formData);
      onClose();
    } catch (error) {
      console.error("Failed to save provider:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleFieldChange = (field: keyof AIProviderConfig, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Reset validation when API key changes
    if (field === 'apiKey' || field === 'baseUrl') {
      setValidationStatus({
        checked: false,
        valid: false,
        message: ""
      });
    }
  };

  return (
    <SimpleDialog open={isOpen} onClose={onClose}>
      <div className="flex flex-col space-y-1.5 text-center sm:text-left">
        <h2 className="text-lg font-semibold leading-none tracking-tight">
          {provider ? 
            (t.settings?.ai_providers?.edit_provider || "Edit AI Provider") : 
            (t.settings?.ai_providers?.add_provider || "Add AI Provider")
          }
        </h2>
        <p className="text-sm text-gray-600">
          {t.settings?.ai_providers?.dialog_description || "Configure your AI provider settings"}
        </p>
      </div>

      <div className="grid gap-4 py-4">
        {/* Pricing Information */}
        {provider?.pricing && (
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <PricingBadge tier={provider.pricing.tier} />
              <h4 className="font-medium">Pricing Information</h4>
            </div>
            
            {provider.pricing.tier === 'free' && (
              <p className="text-sm text-green-700">
                ✅ This provider is completely free to use!
              </p>
            )}
            
            {provider.pricing.tier === 'freemium' && (
              <div className="text-sm space-y-1">
                <p className="text-blue-700">
                  💎 Free tier available: {provider.pricing.freeQuota?.description}
                </p>
                <p className="text-gray-600">
                  Paid plans available for higher usage
                </p>
              </div>
            )}
            
            {provider.pricing.tier === 'paid' && (
              <div className="text-sm space-y-1">
                <p className="text-purple-700">
                  💳 This is a paid service
                </p>
                <p className="text-gray-600">
                  Starting from: {provider.pricing.paidPlans?.[0]?.description}
                </p>
              </div>
            )}
            
            {provider.pricing.websiteUrl && (
              <a 
                href={provider.pricing.websiteUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline text-sm inline-flex items-center gap-1 mt-2"
              >
                View Pricing Details →
              </a>
            )}
          </div>
        )}

        {/* Provider Name */}
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="provider-name" className="text-right">
            {t.settings?.ai_providers?.provider_name || "Name"}
          </Label>
          <Input
            id="provider-name"
            value={formData.name}
            onChange={(e) => handleFieldChange('name', e.target.value)}
            className="col-span-3"
            placeholder="OpenAI, Anthropic, etc."
          />
        </div>

        {/* API Key */}
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="api-key" className="text-right">
            {t.settings?.ai_providers?.api_key || "API Key"}
          </Label>
          <div className="col-span-3 space-y-2">
            <Input
              id="api-key"
              type="password"
              value={formData.apiKey}
              onChange={(e) => handleFieldChange('apiKey', e.target.value)}
              placeholder="Enter your API key"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={validateKey}
              disabled={isValidating || !formData.apiKey}
            >
              {isValidating ? (
                <X className="h-4 w-4 mr-1 animate-spin" />
              ) : (
                validationStatus.checked ? (
                  validationStatus.valid ? (
                    <Check className="h-4 w-4 mr-1 text-green-500" />
                  ) : (
                    <X className="h-4 w-4 mr-1 text-red-500" />
                  )
                ) : null
              )}
              {t.settings?.ai_providers?.validate_key || "Validate"}
            </Button>
            {validationStatus.checked && (
              <ValidationMessage
                type={validationStatus.valid ? "success" : "error"}
                message={validationStatus.message}
              />
            )}
          </div>
        </div>

        {/* Base URL */}
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="base-url" className="text-right">
            {t.settings?.ai_providers?.base_url || "Base URL"}
          </Label>
          <Input
            id="base-url"
            value={formData.baseUrl}
            onChange={(e) => handleFieldChange('baseUrl', e.target.value)}
            className="col-span-3"
            placeholder="https://api.openai.com/v1"
          />
        </div>

        {/* Model Selection */}
        {formData.models && formData.models.length > 0 && (
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="default-model" className="text-right">
              {t.settings?.ai_providers?.default_model || "Default Model"}
            </Label>
            <Select
              value={formData.defaultModel}
              onValueChange={(value) => handleFieldChange('defaultModel', value)}
            >
              <SelectTrigger className="col-span-3">
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                {formData.models.map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
                
                {fetchingModels && (
                  <div className="flex items-center justify-center py-2">
                    <X className="h-4 w-4 mr-1 animate-spin" />
                    <span>Loading models...</span>
                  </div>
                )}
              </SelectContent>
            </Select>
          </div>
        )}

        {/* Max Tokens */}
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="max-tokens" className="text-right">
            {t.settings?.ai_providers?.max_tokens || "Max Tokens"}
          </Label>
          <Input
            id="max-tokens"
            type="number"
            value={formData.maxTokens}
            onChange={(e) => handleFieldChange('maxTokens', parseInt(e.target.value))}
            className="col-span-3"
            min="1"
            max="100000"
          />
        </div>

        {/* Temperature */}
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="temperature" className="text-right">
            {t.settings?.ai_providers?.temperature || "Temperature"}
          </Label>
          <Input
            id="temperature"
            type="number"
            step="0.1"
            min="0"
            max="2"
            value={formData.temperature}
            onChange={(e) => handleFieldChange('temperature', parseFloat(e.target.value))}
            className="col-span-3"
          />
        </div>
      </div>

      <div className="flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2">
        <Button variant="outline" onClick={onClose}>
          {t.common?.cancel || "Cancel"}
        </Button>
        <Button 
          onClick={handleSave} 
          disabled={isSaving || !validationStatus.valid}
        >
          {isSaving && <X className="h-4 w-4 mr-1 animate-spin" />}
          {t.common?.save || "Save"}
        </Button>
      </div>
    </SimpleDialog>
  );
}
