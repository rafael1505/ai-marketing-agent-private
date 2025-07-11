"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getAvailableProviders, generateMultipleImages, type AIProvider, type ProviderConfig, saveProviderConfiguration, updateProviderConfiguration, testProviderConfiguration, getProviderConfigurations } from "@/services/ai-providers";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import ProviderConfigForm from "@/components/ai-providers/provider-config-form";
// Remove lucide-react import since many icons are not available

export default function AIProvidersPage() {
  const [providers, setProviders] = useState<AIProvider[]>([]);
  const [providerConfigs, setProviderConfigs] = useState<ProviderConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [testResults, setTestResults] = useState<Record<string, any>>({});
  const [testPrompt, setTestPrompt] = useState("A modern office building with solar panels and green technology");
  const [selectedProvider, setSelectedProvider] = useState("free-test-provider");
  const [testSize, setTestSize] = useState("512x512");
  const [testVariations, setTestVariations] = useState(2);
  const [isTesting, setIsTesting] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [savingConfig, setSavingConfig] = useState<string | null>(null);
  const [testingConfig, setTestingConfig] = useState<string | null>(null);

  // Helper function to safely get pricing info
  const getPricingDisplay = (provider: AIProvider): string => {
    try {
      if (!provider || !provider.pricing || typeof provider.pricing !== 'object') {
        return 'Free';
      }
      const values = Object.values(provider.pricing);
      if (values.length === 0) {
        return 'Free';
      }
      const price = values[0];
      return typeof price === 'number' ? `$${price.toFixed(2)}` : 'Free';
    } catch (error) {
      console.error('Error getting pricing for provider:', provider?.id, error);
      return 'Free';
    }
  };

  useEffect(() => {
    loadProviders();
    loadProviderConfigs();
    
    // Listen for provider config updates from localStorage changes
    const handleConfigUpdate = (event: CustomEvent) => {
      console.log('AI Provider config updated, reloading configs...');
      loadProviderConfigs();
    };
    
    // Listen for the custom event we dispatch when configs are updated
    window.addEventListener('aiProviderConfigUpdated', handleConfigUpdate as EventListener);
    
    // Also listen for localStorage changes from other tabs
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === 'ai-provider-configurations') {
        console.log('localStorage changed, reloading configs...');
        loadProviderConfigs();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('aiProviderConfigUpdated', handleConfigUpdate as EventListener);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  // Update selected provider when providers and configs are loaded
  useEffect(() => {
    if (providers.length > 0 && providerConfigs.length >= 0) {
      const activeProviders = providers.filter(provider => {
        const config = getProviderConfig(provider.id);
        const isConfigured = config.apiKey && config.apiKey.length > 0;
        const isActivated = config.isActive === true;
        return isConfigured && isActivated;
      });
      
      // Set the first active provider as default, or fall back to first available
      if (activeProviders.length > 0) {
        setSelectedProvider(activeProviders[0].id);
      } else {
        const availableProvider = providers.find(p => p.available);
        if (availableProvider) {
          setSelectedProvider(availableProvider.id);
        }
      }
    }
  }, [providers, providerConfigs]);

  const loadProviders = async () => {
    setLoading(true);
    try {
      const providerList = await getAvailableProviders();
      console.log("Loaded providers:", providerList);
      setProviders(providerList);
    } catch (error) {
      console.error("Failed to load providers:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadProviderConfigs = async () => {
    try {
      const configs = await getProviderConfigurations();
      console.log("Loaded provider configs:", configs);
      setProviderConfigs(configs);
    } catch (error) {
      console.error("Failed to load provider configurations:", error);
    }
  };

  const handleSaveConfig = async (config: ProviderConfig): Promise<void> => {
    console.log('Parent: handleSaveConfig called with', config);
    setSavingConfig(config.id);
    try {
      // Check if config exists, update or create accordingly
      const existingConfig = providerConfigs.find(c => c.id === config.id);
      console.log('Parent: existingConfig', existingConfig);
      console.log('Parent: current providerConfigs state', providerConfigs);
      
      let savedConfig;
      
      if (existingConfig) {
        console.log('Parent: updating existing config');
        savedConfig = await updateProviderConfiguration(config.id, config);
      } else {
        console.log('Parent: saving new config');
        savedConfig = await saveProviderConfiguration(config);
      }
      
      console.log('Parent: savedConfig from API', savedConfig);
      
      // Update local state
      setProviderConfigs(prev => {
        const filtered = prev.filter(c => c.id !== config.id);
        const newConfigs = [...filtered, savedConfig];
        console.log('Parent: old providerConfigs', prev);
        console.log('Parent: updating providerConfigs to', newConfigs);
        return newConfigs;
      });
      
      // Reload providers to get updated status
      console.log('Parent: reloading providers...');
      await loadProviders();
      
      // NOTE: Removed loadProviderConfigs() call here because:
      // 1. We already have the latest config from the save operation
      // 2. Calling getProviderConfigurations() again could interfere with localStorage
      // 3. We've already updated the React state above
      console.log('Parent: config saved and state updated successfully');
      
    } catch (error) {
      console.error('Parent: error in handleSaveConfig', error);
      throw error;
    } finally {
      setSavingConfig(null);
    }
  };

  const handleTestConfig = async (config: ProviderConfig): Promise<boolean> => {
    setTestingConfig(config.id);
    try {
      return await testProviderConfiguration(config);
    } finally {
      setTestingConfig(null);
    }
  };

  const getProviderConfig = (providerId: string): ProviderConfig => {
    const existingConfig = providerConfigs.find(c => c.id === providerId);
    const provider = providers.find(p => p.id === providerId);
    
    console.log(`getProviderConfig(${providerId}):`, {
      existingConfig,
      provider,
      allProviderConfigs: providerConfigs
    });
    
    const config = existingConfig || {
      id: providerId,
      name: provider?.name || providerId,
      isActive: false,
    };
    
    console.log(`getProviderConfig(${providerId}) returning:`, config);
    return config;
  };

  const testProvider = async (providerId: string) => {
    setIsTesting(true);
    try {
      console.log(`Testing provider: ${providerId}`);
      
      const result = await generateMultipleImages(
        "Test image generation for AI provider validation",
        providerId,
        1,
        "512x512"
      );
      
      setTestResults(prev => ({
        ...prev,
        [providerId]: {
          success: result.success,
          error: result.error,
          model: result.model,
          cost: result.cost,
          timestamp: new Date().toISOString(),
        }
      }));
      
      console.log(`Test result for ${providerId}:`, result);
    } catch (error) {
      console.error(`Test failed for ${providerId}:`, error);
      setTestResults(prev => ({
        ...prev,
        [providerId]: {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString(),
        }
      }));
    } finally {
      setIsTesting(false);
    }
  };

  const runImageTest = async () => {
    if (!selectedProvider) return;
    
    setIsTesting(true);
    try {
      const result = await generateMultipleImages(
        testPrompt,
        selectedProvider,
        testVariations,
        testSize
      );
      
      setTestResults(prev => ({
        ...prev,
        [selectedProvider]: {
          success: result.success,
          error: result.error,
          model: result.model,
          cost: result.cost,
          images: result.images,
          timestamp: new Date().toISOString(),
        }
      }));
    } catch (error) {
      console.error("Image test failed:", error);
      setTestResults(prev => ({
        ...prev,
        [selectedProvider]: {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString(),
        }
      }));
    } finally {
      setIsTesting(false);
    }
  };

  const getProviderStatus = (provider: AIProvider) => {
    const config = getProviderConfig(provider.id);
    
    // Check if provider is configured with API key and is activated
    const isConfigured = config.apiKey && config.apiKey.length > 0;
    const isActivated = config.isActive === true;
    
    if (isConfigured && isActivated) {
      return { status: "active", color: "bg-green-500", text: "Active" };
    } else if (isConfigured && !isActivated) {
      return { status: "configured", color: "bg-yellow-500", text: "Configured (Inactive)" };
    } else if (provider.available) {
      return { status: "available", color: "bg-blue-500", text: "Available" };
    } else {
      return { status: "unavailable", color: "bg-red-500", text: "Not Configured" };
    }
  };

  const getStatusColor = (provider: AIProvider) => {
    return getProviderStatus(provider).color;
  };

  const getStatusText = (provider: AIProvider) => {
    return getProviderStatus(provider).text;
  };

  const getActiveProviders = () => {
    return providers.filter(provider => {
      const status = getProviderStatus(provider);
      return status.status === "active";
    });
  };

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading AI providers...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI Provider Configuration</h1>
          <p className="text-gray-600 mt-2">Manage and test your AI image generation providers</p>
        </div>
        <Button onClick={loadProviders} variant="outline">
          Refresh Providers
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Provider Overview</TabsTrigger>
          <TabsTrigger value="test">Test Generation</TabsTrigger>
          <TabsTrigger value="configuration">Configuration</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {providers.map((provider) => (
              <Card key={provider.id} className="relative">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{provider.name}</CardTitle>
                    <Badge className={`${getStatusColor(provider)} text-white`}>
                      {getStatusText(provider)}
                    </Badge>
                  </div>
                  <CardDescription className="text-sm">
                    Model: {provider.model}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="text-blue-500 font-bold">📸</span>
                      <span>Max: {provider.max_variations}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-green-500 font-bold">$</span>
                      <span>
                        {getPricingDisplay(provider)}
                      </span>
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-600">
                    <p>Sizes: {provider.supported_sizes?.slice(0, 3).join(", ") || "N/A"}</p>
                  </div>

                  {testResults[provider.id] && (
                    <div className={`p-3 rounded text-sm ${
                      testResults[provider.id].success 
                        ? 'bg-green-50 text-green-800 border border-green-200' 
                        : 'bg-red-50 text-red-800 border border-red-200'
                    }`}>
                      <div className="flex items-center gap-2 mb-1">
                        {testResults[provider.id].success ? (
                          <span className="text-green-500 font-bold">✓</span>
                        ) : (
                          <span className="text-red-500 font-bold">⚠</span>
                        )}
                        <span className="font-medium">
                          {testResults[provider.id].success ? 'Test Passed' : 'Test Failed'}
                        </span>
                      </div>
                      {testResults[provider.id].error && (
                        <p className="text-xs mt-1">{testResults[provider.id].error}</p>
                      )}
                      {testResults[provider.id].cost !== undefined && (
                        <p className="text-xs mt-1">Cost: ${testResults[provider.id].cost.toFixed(4)}</p>
                      )}
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => testProvider(provider.id)}
                      disabled={isTesting || getProviderStatus(provider).status !== "active"}
                      className="flex-1"
                    >
                      {isTesting ? "Testing..." : "Quick Test"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="test" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-xl">⚡</span>
                Image Generation Test
              </CardTitle>
              <CardDescription>
                Test image generation with different providers and settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {getActiveProviders().length === 0 ? (
                <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                  <h3 className="font-medium text-yellow-900 mb-2">No Active Providers</h3>
                  <p className="text-sm text-yellow-800 mb-3">
                    You need to configure and activate at least one AI provider to test image generation.
                  </p>
                  <p className="text-sm text-yellow-800">
                    Go to the <strong>Configuration</strong> tab to set up your providers with API keys and activate them.
                  </p>
                </div>
              ) : (
                <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-4">
                  <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                    <h3 className="font-medium text-yellow-900 mb-2">🧪 Demo Mode</h3>
                    <div className="text-sm text-yellow-800 space-y-2">
                      <p><strong>This is a test/demo environment:</strong></p>
                      <ul className="list-disc list-inside space-y-1 ml-4">
                        <li>SVG placeholder images are generated instead of real AI images</li>
                        <li>No actual API calls are made to AI providers</li>
                        <li>Costs shown are mock calculations for demonstration</li>
                        <li>Configuration settings (model, style, quality) are correctly passed through</li>
                      </ul>
                      <p className="font-medium">In production, this would generate real images using your configured provider and model.</p>
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="test-prompt">Test Prompt</Label>
                    <Textarea
                      id="test-prompt"
                      value={testPrompt}
                      onChange={(e) => setTestPrompt(e.target.value)}
                      placeholder="Describe the image you want to generate..."
                      className="min-h-[100px]"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="test-provider">Provider</Label>
                      <Select value={selectedProvider} onValueChange={setSelectedProvider}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select provider" />
                        </SelectTrigger>
                        <SelectContent>
                          {getActiveProviders().map((provider) => (
                            <SelectItem key={provider.id} value={provider.id}>
                              {provider.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="test-size">Image Size</Label>
                      <Select value={testSize} onValueChange={setTestSize}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="512x512">512x512</SelectItem>
                          <SelectItem value="1024x1024">1024x1024</SelectItem>
                          <SelectItem value="1024x1792">1024x1792</SelectItem>
                          <SelectItem value="1792x1024">1792x1024</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="test-variations">Number of Variations</Label>
                    <Select value={testVariations.toString()} onValueChange={(v) => setTestVariations(parseInt(v))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1 Image</SelectItem>
                        <SelectItem value="2">2 Images</SelectItem>
                        <SelectItem value="3">3 Images</SelectItem>
                        <SelectItem value="4">4 Images</SelectItem>
                        <SelectItem value="5">5 Images</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <Button 
                    onClick={runImageTest} 
                    disabled={isTesting || !selectedProvider}
                    className="w-full"
                  >
                    {isTesting ? "Generating..." : "Generate Test Images"}
                  </Button>
                </div>
                
                <div className="space-y-4">
                  {testResults[selectedProvider] && (
                    <div className="border rounded-lg p-4">
                      <h3 className="font-medium mb-3">Test Results</h3>
                      
                      <div className={`p-3 rounded mb-4 ${
                        testResults[selectedProvider].success 
                          ? 'bg-green-50 text-green-800 border border-green-200' 
                          : 'bg-red-50 text-red-800 border border-red-200'
                      }`}>
                        <div className="flex items-center gap-2 mb-2">
                          {testResults[selectedProvider].success ? (
                            <span className="text-green-500 font-bold">✓</span>
                          ) : (
                            <span className="text-red-500 font-bold">⚠</span>
                          )}
                          <span className="font-medium">
                            {testResults[selectedProvider].success ? 'Generation Successful' : 'Generation Failed'}
                          </span>
                        </div>
                        
                        {testResults[selectedProvider].model && (
                          <p className="text-sm">Model: {testResults[selectedProvider].model}</p>
                        )}
                        
                        {testResults[selectedProvider].cost !== undefined && (
                          <p className="text-sm">Cost: ${testResults[selectedProvider].cost.toFixed(4)} (Demo calculation)</p>
                        )}
                        
                        {testResults[selectedProvider].metadata && (
                          <div className="text-sm mt-2 space-y-1">
                            {testResults[selectedProvider].metadata.style && (
                              <p>Style: {testResults[selectedProvider].metadata.style}</p>
                            )}
                            {testResults[selectedProvider].metadata.quality && (
                              <p>Quality: {testResults[selectedProvider].metadata.quality}</p>
                            )}
                            {testResults[selectedProvider].metadata.size && (
                              <p>Size: {testResults[selectedProvider].metadata.size}</p>
                            )}
                            {testResults[selectedProvider].metadata.note && (
                              <p className="italic text-gray-600">{testResults[selectedProvider].metadata.note}</p>
                            )}
                          </div>
                        )}
                        
                        {testResults[selectedProvider].error && (
                          <p className="text-sm mt-2 font-mono bg-white bg-opacity-50 p-2 rounded">
                            {testResults[selectedProvider].error}
                          </p>
                        )}
                      </div>
                      
                      {testResults[selectedProvider].images && (
                        <div>
                          <h4 className="font-medium mb-2">Generated Images:</h4>
                          <div className="grid grid-cols-2 gap-2">
                            {testResults[selectedProvider].images.map((imageUrl: string, index: number) => (
                              <div key={index} className="aspect-square border rounded overflow-hidden">
                                <img 
                                  src={imageUrl} 
                                  alt={`Generated ${index + 1}`}
                                  className="w-full h-full object-cover cursor-pointer"
                                  onClick={() => window.open(imageUrl, '_blank')}
                                />
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="configuration" className="space-y-6">
          <div className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
              <h3 className="font-medium text-blue-900 mb-2">Configuration Instructions</h3>
              <div className="text-sm text-blue-800 space-y-2">
                <p>Configure your AI provider settings below:</p>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li><strong>OpenAI:</strong> Configure DALL-E 3 with API key, model, quality, and size settings</li>
                  <li><strong>Stability AI:</strong> Set up Stable Diffusion with custom CFG scale and steps</li>
                  <li><strong>Replicate:</strong> Configure inference steps and guidance scale</li>
                  <li><strong>HuggingFace:</strong> Enable caching for faster responses</li>
                </ul>
                <p className="mt-3 font-medium">API keys are stored securely and encrypted.</p>
              </div>
            </div>
            
            <div className="space-y-6">
              {providers.map((provider) => {
                const config = getProviderConfig(provider.id);
                return (
                  <ProviderConfigForm
                    key={provider.id}
                    provider={{
                      id: provider.id,
                      name: provider.name,
                      apiKey: config.apiKey,
                      selectedModel: config.selectedModel || provider.model,
                      modelOptions: [],
                      maxTokens: config.maxTokens || 1000,
                      temperature: config.temperature || 0.7,
                      quality: config.quality,
                      size: config.size,
                      style: config.style,
                      isActive: config.isActive,
                      customOptions: config.customOptions || {}
                    }}
                    onSave={async (updatedConfig) => {
                      await handleSaveConfig(updatedConfig);
                    }}
                    onTest={async (configToTest) => {
                      return await handleTestConfig(configToTest);
                    }}
                    saving={savingConfig === provider.id}
                    testing={testingConfig === provider.id}
                  />
                );
              })}
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
