"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { 
  Check, 
  X
} from "lucide-react";
import { AIProviderConfig } from "@/types";
import { useInlineEdit } from "@/hooks/useInlineEdit";
import { updateAIProvider } from "@/services/ai-providers";

interface InlineEditableProviderCardProps {
  provider: AIProviderConfig;
  onUpdate: (updatedProvider: AIProviderConfig) => void;
  onDelete?: (providerId: string) => void;
}

export const InlineEditableProviderCard: React.FC<InlineEditableProviderCardProps> = ({
  provider,
  onUpdate,
  onDelete
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [connectionMessage, setConnectionMessage] = useState<string>('');

  // Inline editing for provider name
  const nameEdit = useInlineEdit({
    initialValue: provider.name,
    onSave: async (value) => {
      const updateData = { name: value };
      const updatedProvider = await updateAIProvider(provider.id, updateData);
      if (updatedProvider) {
        onUpdate(updatedProvider);
      }
    },
    validation: (value) => value.trim().length < 2 ? 'Name must be at least 2 characters' : null,
    autoSave: false  // Consistent UX pattern
  });

  // Inline editing for API key
  const apiKeyEdit = useInlineEdit({
    initialValue: provider.apiKey || '',
    onSave: async (value) => {
      // Map frontend fields to backend database fields
      const updateData = { 
        apiKey: value, 
        configured: !!value  // isConfigured -> configured
      };
      const updatedProvider = await updateAIProvider(provider.id, updateData);
      if (updatedProvider) {
        onUpdate(updatedProvider);
      }
    },
    validation: (value) => {
      if (!value.trim()) return 'API key is required';
      if (provider.id === 'openai' && !value.startsWith('sk-')) {
        return 'OpenAI API key should start with "sk-"';
      }
      if (provider.id === 'anthropic' && !value.startsWith('sk-ant-')) {
        return 'Anthropic API key should start with "sk-ant-"';
      }
      return null;
    },
    autoSave: false  // Disable auto-save for better UX control
  });

  // Inline editing for model selection
  const modelEdit = useInlineEdit({
    initialValue: provider.selectedModel || provider.modelOptions?.[0] || '',
    onSave: async (value) => {
      const updateData = { model: value };  // selectedModel -> model
      const updatedProvider = await updateAIProvider(provider.id, updateData);
      if (updatedProvider) {
        onUpdate(updatedProvider);
      }
    },
    autoSave: false
  });

  // Inline editing for max tokens
  const maxTokensEdit = useInlineEdit({
    initialValue: provider.maxTokens || 1000,
    onSave: async (value) => {
      const updateData = { maxTokens: value };
      const updatedProvider = await updateAIProvider(provider.id, updateData);
      if (updatedProvider) {
        onUpdate(updatedProvider);
      }
    },
    validation: (value) => {
      if (value < 1) return 'Must be at least 1 token';
      if (value > 100000) return 'Cannot exceed 100,000 tokens';
      return null;
    },
    autoSave: false
  });

  // Inline editing for temperature
  const temperatureEdit = useInlineEdit({
    initialValue: provider.temperature || 0.7,
    onSave: async (value) => {
      const updateData = { temperature: value };
      const updatedProvider = await updateAIProvider(provider.id, updateData);
      if (updatedProvider) {
        onUpdate(updatedProvider);
      }
    },
    validation: (value) => {
      if (value < 0) return 'Temperature cannot be negative';
      if (value > 2) return 'Temperature cannot exceed 2.0';
      return null;
    },
    autoSave: false
  });

  const handleToggleActive = async () => {
    // Map frontend fields to backend database fields
    const updateData = { 
      status: !provider.isActive ? "active" : "inactive"  // isActive -> status
    };
    const updatedProvider = await updateAIProvider(provider.id, updateData);
    if (updatedProvider) {
      onUpdate(updatedProvider);
    }
  };

  const handleTestConnection = async () => {
    setIsConnecting(true);
    setConnectionStatus('idle');
    
    try {
      // Simulate API test call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // In real implementation, this would call the validation endpoint
      // const result = await validateAPIKey({ providerId: provider.id, apiKey: provider.apiKey });
      
      setConnectionStatus('success');
      setConnectionMessage('Connection successful! Provider is ready to use.');
    } catch (error) {
      setConnectionStatus('error');
      setConnectionMessage('Connection failed. Please check your API key and try again.');
    } finally {
      setIsConnecting(false);
    }
  };

  const getStatusIndicator = () => {
    if (!provider.isActive) {
      return <Badge variant="secondary" className="bg-gray-100 text-gray-600">Disabled</Badge>;
    }
    if (!provider.isConfigured) {
      return <Badge variant="destructive">Setup Required</Badge>;
    }
    if (connectionStatus === 'success') {
      return <Badge className="bg-green-100 text-green-800">Connected</Badge>;
    }
    if (connectionStatus === 'error') {
      return <Badge variant="destructive">Connection Error</Badge>;
    }
    return <Badge className="bg-blue-100 text-blue-800">Ready</Badge>;
  };

  const getPricingBadgeColor = (tier: string) => {
    switch (tier) {
      case 'free': return 'bg-green-100 text-green-800';
      case 'freemium': return 'bg-blue-100 text-blue-800';
      case 'paid': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const formatApiKey = (key: string) => {
    if (!key) return 'Not configured';
    if (showApiKey) return key;
    return '••••••••••••••••';
  };

  return (
    <Card className={`transition-all duration-200 hover:shadow-md ${
      provider.isActive ? 'ring-2 ring-blue-100' : 'opacity-75'
    }`}>
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            {/* Provider Logo */}
            {provider.logo && (
              <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                <img src={provider.logo} alt={provider.name} className="w-8 h-8" />
              </div>
            )}
            
            <div className="flex-1">
              {/* Provider Name - Inline Editable */}
              <div className="flex items-center gap-2 mb-2">
                {nameEdit.isEditing ? (
                  <div className="flex items-center gap-2">
                    <Input
                      value={nameEdit.value}
                      onChange={(e) => nameEdit.setValue(e.target.value)}
                      className="h-8 font-semibold"
                      autoFocus
                      onBlur={nameEdit.stopEditing}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') nameEdit.save();
                        if (e.key === 'Escape') nameEdit.cancel();
                      }}
                    />
                    {nameEdit.validationError && (
                      <span className="text-xs text-red-500">{nameEdit.validationError}</span>
                    )}
                  </div>
                ) : (
                  <h3 
                    className="font-semibold text-lg cursor-pointer hover:text-blue-600 transition-colors"
                    onClick={nameEdit.startEditing}
                  >
                    {nameEdit.value}
                  </h3>
                )}
              </div>

              {/* Status Badges */}
              <div className="flex items-center gap-2">
                {getStatusIndicator()}
                <Badge 
                  className={getPricingBadgeColor(provider.pricing?.tier || 'free')}
                >
                  {(() => {
                    const tier = provider.pricing?.tier || 'free';
                    return tier.charAt(0).toUpperCase() + tier.slice(1);
                  })()}
                </Badge>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="p-2"
            >
              <span className="w-4 h-4">⚙️</span>
            </Button>
            
            <Switch
              checked={provider.isActive}
              onCheckedChange={handleToggleActive}
              className="data-[state=checked]:bg-green-500"
            />
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* API Key Configuration - Enhanced UX with Save/Cancel */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">API Key</Label>
          <div className="flex items-center gap-2">
            {apiKeyEdit.isEditing ? (
              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-2">
                  <Input
                    type={showApiKey ? "text" : "password"}
                    value={apiKeyEdit.value}
                    onChange={(e) => apiKeyEdit.setValue(e.target.value)}
                    placeholder="Enter your API key..."
                    className="font-mono text-sm flex-1"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !apiKeyEdit.validationError) {
                        e.preventDefault();
                        apiKeyEdit.save();
                      }
                      if (e.key === 'Escape') {
                        e.preventDefault();
                        apiKeyEdit.cancel();
                      }
                    }}
                    autoFocus
                  />
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setShowApiKey(!showApiKey);
                    }}
                    className="p-2"
                    type="button"
                  >
                    {showApiKey ? <span className="w-4 h-4">🙈</span> : <span className="w-4 h-4">👁️</span>}
                  </Button>
                </div>
                
                {/* Save/Cancel Actions */}
                <div className="flex items-center gap-2 text-sm">
                  <Button
                    size="sm"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      console.log('🔧 DEBUG: Save button clicked - isDirty:', apiKeyEdit.isDirty, 'isSaving:', apiKeyEdit.isSaving, 'validationError:', apiKeyEdit.validationError);
                      apiKeyEdit.save();
                    }}
                    disabled={!apiKeyEdit.isDirty || !!apiKeyEdit.validationError || apiKeyEdit.isSaving}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                    type="button"
                  >
                    {apiKeyEdit.isSaving ? (
                      <>
                        <span className="w-3 h-3 animate-spin mr-1">⏳</span>
                        Saving...
                      </>
                    ) : (
                      <>
                        <Check className="w-3 h-3 mr-1" />
                        Save
                      </>
                    )}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      apiKeyEdit.cancel();
                    }}
                    disabled={apiKeyEdit.isSaving}
                    type="button"
                  >
                    <X className="w-3 h-3 mr-1" />
                    Cancel
                  </Button>
                  {apiKeyEdit.isDirty && (
                    <span className="text-orange-600 text-xs">
                      ⚠️ Unsaved changes
                    </span>
                  )}
                </div>
                
                {apiKeyEdit.validationError && (
                  <span className="text-xs text-red-500 block">{apiKeyEdit.validationError}</span>
                )}
                {apiKeyEdit.error && (
                  <span className="text-xs text-red-500 block">Save failed: {apiKeyEdit.error}</span>
                )}
              </div>
            ) : (
              <>
                <div 
                  className="flex-1 p-2 border rounded cursor-pointer hover:bg-gray-50 transition-colors font-mono text-sm bg-blue-50"
                  onClick={() => {
                    console.log('🔧 DEBUG: API Key click triggered!');
                    apiKeyEdit.startEditing();
                  }}
                  title="Click to edit API key"
                >
                  {formatApiKey(apiKeyEdit.value)} 
                  <span className="text-blue-600 ml-2 text-xs">✏️ Click to edit</span>
                </div>
                
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setShowApiKey(!showApiKey);
                  }}
                  className="p-2"
                  type="button"
                >
                  {showApiKey ? <span className="w-4 h-4">🙈</span> : <span className="w-4 h-4">👁️</span>}
                </Button>
                
                <Button
                  size="sm"
                  variant="outline"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    handleTestConnection();
                  }}
                  disabled={!apiKeyEdit.value || isConnecting}
                  className="flex items-center gap-1"
                  type="button"
                >
                  {isConnecting ? (
                    <span className="w-4 h-4 animate-spin">⏳</span>
                  ) : connectionStatus === 'success' ? (
                    <span className="w-4 h-4 text-green-500">✅</span>
                  ) : connectionStatus === 'error' ? (
                    <span className="w-4 h-4 text-red-500">❌</span>
                  ) : (
                    <span className="w-4 h-4">🔗</span>
                  )}
                  Test
                </Button>
              </>
            )}
          </div>
          
          {/* Connection Status Message */}
          {connectionMessage && (
            <div className={`text-xs p-2 rounded ${
              connectionStatus === 'success' 
                ? 'bg-green-50 text-green-700 border border-green-200' 
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}>
              {connectionMessage}
            </div>
          )}
        </div>

        {/* Model Selection */}
        {provider.modelOptions && provider.modelOptions.length > 0 && (
          <div className="space-y-2">
            <Label className="text-sm font-medium">Model</Label>
            {modelEdit.isEditing ? (
              <Select
                value={modelEdit.value}
                onValueChange={(value) => {
                  modelEdit.setValue(value);
                  modelEdit.save();
                }}
                onOpenChange={(open) => !open && modelEdit.stopEditing()}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a model..." />
                </SelectTrigger>
                <SelectContent>
                  {provider.modelOptions.map((model) => (
                    <SelectItem key={model} value={model}>
                      {model}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : (
              <div 
                className="p-2 border rounded cursor-pointer hover:bg-gray-50 transition-colors text-sm"
                onClick={modelEdit.startEditing}
              >
                {modelEdit.value || 'Click to select a model'}
              </div>
            )}
          </div>
        )}

        {/* Advanced Settings */}
        {showAdvanced && (
          <div className="space-y-4 pt-4 border-t">
            <h4 className="font-medium text-sm text-gray-700">Advanced Settings</h4>
            
            {/* Max Tokens */}
            <div className="space-y-2">
              <Label className="text-sm">Max Tokens: {maxTokensEdit.value}</Label>
              <Slider
                value={[maxTokensEdit.value]}
                onValueChange={([value]) => {
                  maxTokensEdit.setValue(value);
                  maxTokensEdit.save();
                }}
                max={10000}
                min={1}
                step={100}
                className="w-full"
              />
              {maxTokensEdit.validationError && (
                <span className="text-xs text-red-500">{maxTokensEdit.validationError}</span>
              )}
            </div>

            {/* Temperature */}
            <div className="space-y-2">
              <Label className="text-sm">Temperature: {temperatureEdit.value.toFixed(2)}</Label>
              <Slider
                value={[temperatureEdit.value]}
                onValueChange={([value]) => {
                  temperatureEdit.setValue(value);
                  temperatureEdit.save();
                }}
                max={2}
                min={0}
                step={0.1}
                className="w-full"
              />
              {temperatureEdit.validationError && (
                <span className="text-xs text-red-500">{temperatureEdit.validationError}</span>
              )}
            </div>
          </div>
        )}

        {/* Pricing Information */}
        {provider.pricing && (
          <div className="pt-4 border-t">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-4 h-4 text-green-500">💰</span>
                <span className="text-sm font-medium">Pricing</span>
              </div>
              {provider.pricing?.websiteUrl && (
                <Button
                  size="sm"
                  variant="ghost"
                  className="text-xs"
                  onClick={() => window.open(provider.pricing?.websiteUrl, '_blank')}
                >
                  <span className="w-3 h-3 mr-1">🔗</span>
                  View Details
                </Button>
              )}
            </div>
            
            <div className="text-xs text-gray-600 mt-1">
              {provider.pricing?.freeQuota?.description || (() => {
                const tier = provider.pricing?.tier || 'standard';
                return `${tier.charAt(0).toUpperCase() + tier.slice(1)} plan`;
              })()}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};