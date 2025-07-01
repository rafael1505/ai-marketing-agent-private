"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { AIProviderConfig } from "@/types";
import { X, Check } from "lucide-react";
import { validateAPIKey, getProviderOptions } from "@/services/ai-providers";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { ValidationMessage } from "@/components/ui/validation-message";

interface AIProviderDialogProps {
  provider: AIProviderConfig | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (provider: AIProviderConfig) => Promise<void>;
  translations: Record<string, any>;
}

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
    isConfigured: false,
    modelOptions: [],
    selectedModel: "",
    maxTokens: 1000,
    temperature: 0.7,
    isActive: true
  });
  
  const [isNew, setIsNew] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [validationStatus, setValidationStatus] = useState<{
    checked: boolean;
    valid: boolean;
    message?: string;
  }>({ checked: false, valid: false });
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [fetchingModels, setFetchingModels] = useState(false);
  
  // Reset form when the dialog opens or provider changes
  useEffect(() => {
    if (isOpen && provider) {
      setFormData({
        ...provider,
        apiKey: provider.apiKey || ""
      });
      setIsNew(!provider.isConfigured);
      setValidationStatus({ 
        checked: Boolean(provider.isConfigured), 
        valid: Boolean(provider.isConfigured) 
      });
      
      // If provider is already configured, fetch available models
      if (provider.id && provider.isConfigured) {
        fetchModelOptions(provider.id);
      }
    }
  }, [isOpen, provider]);
  
  const fetchModelOptions = async (providerId: string) => {
    setFetchingModels(true);
    try {
      const options = await getProviderOptions(providerId);
      if (options && options.models) {
        setAvailableModels(options.models);
        
        // If we have models but no selected model, select the first one
        if (options.models.length > 0 && !formData.selectedModel) {
          setFormData(prev => ({
            ...prev,
            selectedModel: options.models[0]
          }));
        }
      }
    } catch (error) {
      console.error("Error fetching model options:", error);
    } finally {
      setFetchingModels(false);
    }
  };
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData({
        ...formData,
        [name]: checked
      });
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
    
    // Reset validation status if API key is changed
    if (name === 'apiKey') {
      setValidationStatus({ checked: false, valid: false });
    }
  };
  
  const handleModelChange = (value: string) => {
    setFormData({
      ...formData,
      selectedModel: value
    });
  };
  
  const handleTemperatureChange = (value: number[]) => {
    setFormData({
      ...formData,
      temperature: value[0]
    });
  };
  
  const handleMaxTokensChange = (value: number[]) => {
    setFormData({
      ...formData,
      maxTokens: value[0]
    });
  };
  
  const handleToggleActive = (checked: boolean) => {
    setFormData({
      ...formData,
      isActive: checked
    });
  };
  
  const validateKey = async () => {
    if (!formData.apiKey || !formData.id) return;
    
    setIsValidating(true);
    try {
      const result = await validateAPIKey(formData.id, formData.apiKey);
      setValidationStatus({
        checked: true,
        valid: result.valid,
        message: result.message
      });
      
      // If validation successful, fetch available models
      if (result.valid) {
        await fetchModelOptions(formData.id);
      }
    } catch (error) {
      console.error("Error validating API key:", error);
      setValidationStatus({
        checked: true,
        valid: false,
        message: "Error validating API key"
      });
    } finally {
      setIsValidating(false);
    }
  };
  
  const handleSave = async () => {
    if (!validationStatus.valid) {
      // If the form hasn't been validated yet, validate it first
      if (!validationStatus.checked) {
        await validateKey();
        return; // Don't save until validation is complete
      }
      return; // Don't save if validation failed
    }
    
    setIsSaving(true);
    try {
      await onSave({
        ...formData,
        isConfigured: true
      });
      onClose();
    } catch (error) {
      console.error("Error saving AI provider:", error);
    } finally {
      setIsSaving(false);
    }
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {isNew
              ? t.settings?.ai_providers?.configure_new || "Configure New Provider"
              : t.settings?.ai_providers?.configure || "Configure Provider"}
          </DialogTitle>
          <DialogDescription>
            {t.settings?.ai_providers?.configure_description || 
             "Configure your AI provider for image generation."}
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="name">
              {t.settings?.ai_providers?.name || "Provider Name"}
            </Label>
            <Input
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              disabled={!isNew}
            />
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <Label htmlFor="apiKey">
                {t.settings?.ai_providers?.api_key || "API Key"}
              </Label>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      type="button"
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
                  </TooltipTrigger>
                  <TooltipContent>
                    {validationStatus.checked
                      ? validationStatus.valid
                        ? validationStatus.message || "API key is valid"
                        : validationStatus.message || "API key is invalid"
                      : "Validate your API key to make sure it works"}
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            
            <Input
              id="apiKey"
              name="apiKey"
              type="password"
              value={formData.apiKey || ""}
              onChange={handleChange}
              placeholder="••••••••••••••••••••"
            />
            
            {validationStatus.checked && (
              <ValidationMessage 
                type={validationStatus.valid ? "success" : "error"}
                message={validationStatus.message || (validationStatus.valid 
                  ? "API key validated successfully" 
                  : "Invalid API key")}
              />
            )}
          </div>
          
          {/* Only show advanced settings if validated */}
          {validationStatus.valid && (
            <>
              <div className="space-y-2">
                <Label htmlFor="model">
                  {t.settings?.ai_providers?.model || "Model"}
                </Label>
                <Select 
                  value={formData.selectedModel} 
                  onValueChange={handleModelChange}
                  disabled={fetchingModels || availableModels.length === 0}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder={fetchingModels 
                      ? "Loading models..." 
                      : "Select a model"} 
                    />
                  </SelectTrigger>
                  <SelectContent>
                    {availableModels.map(model => (
                      <SelectItem key={model} value={model}>
                        {model}
                      </SelectItem>
                    ))}
                    
                    {availableModels.length === 0 && !fetchingModels && (
                      <SelectItem value="" disabled>
                        No models available
                      </SelectItem>
                    )}
                    
                    {fetchingModels && (
                      <div className="flex items-center justify-center py-2">
                        <X className="h-4 w-4 mr-1 animate-spin" />
                        <span>Loading models...</span>
                      </div>
                    )}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <Label htmlFor="temperature">
                    {t.settings?.ai_providers?.temperature || "Temperature"}
                  </Label>
                  <span className="text-sm text-muted-foreground">
                    {formData.temperature?.toFixed(1)}
                  </span>
                </div>
                <Slider
                  id="temperature"
                  min={0}
                  max={1}
                  step={0.1}
                  value={[formData.temperature || 0.7]}
                  onValueChange={handleTemperatureChange}
                />
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <Label htmlFor="maxTokens">
                    {t.settings?.ai_providers?.max_tokens || "Max Tokens"}
                  </Label>
                  <span className="text-sm text-muted-foreground">
                    {formData.maxTokens}
                  </span>
                </div>
                <Slider
                  id="maxTokens"
                  min={100}
                  max={4000}
                  step={100}
                  value={[formData.maxTokens || 1000]}
                  onValueChange={handleMaxTokensChange}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="isActive">
                  {t.settings?.ai_providers?.active || "Active"}
                </Label>
                <Switch
                  id="isActive"
                  name="isActive"
                  checked={formData.isActive}
                  onCheckedChange={handleToggleActive}
                />
              </div>
            </>
          )}
        </div>
        
        <DialogFooter>
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
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
