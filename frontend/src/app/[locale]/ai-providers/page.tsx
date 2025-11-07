"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { getUserAIProviders, updateAIProvider, deleteAIProvider, saveAIProvider, validateAPIKey, getProviderOptions } from "@/services/ai-providers";
import { AIProviderConfig } from "@/types";
import Image from "next/image";
import { getTranslations } from "@/i18n";
import { Check, X } from "lucide-react";

// Icon components for consistent styling
const PlusIcon = () => <span className="text-lg">➕</span>;
const SettingsIcon = () => <span className="text-lg">⚙️</span>;
const PowerIcon = () => <span className="text-lg">⚡</span>;
const TrashIcon = () => <span className="text-lg">🗑️</span>;
const EyeIcon = () => <span className="text-lg">👁️</span>;
const EyeOffIcon = () => <span className="text-lg">🙈</span>;
const LightbulbIcon = () => <span className="text-lg">💡</span>;
const TestTubeIcon = () => <span className="text-lg">🧪</span>;
const LoaderIcon = () => (
  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current inline-block" />
);

interface AIProvidersPageProps {
  params: {
    locale: string;
  };
}

const PROVIDER_LOGOS: Record<string, string> = {
  openai: "/ai-providers/openai.svg",
  anthropic: "/ai-providers/anthropic.svg",
  "google-ai": "/ai-providers/colab.svg",
  huggingface: "/ai-providers/huggingface.svg",
  replicate: "/ai-providers/replicate.svg",
  stability: "/ai-providers/stability.svg",
  midjourney: "/ai-providers/midjourney.svg",
  ollama: "/ai-providers/ollama.svg",
  lmstudio: "/ai-providers/lmstudio.svg",
};

// Helper function to safely get nested translation keys (pure function, no hooks)
function getTranslationValue(t: Record<string, any>, key: string, replacements?: Record<string, string>): string {
  const keys = key.split('.');
  let value: any = t;
  
  for (const k of keys) {
    if (value && typeof value === 'object') {
      value = value[k];
    } else {
      return key; // Return key if translation not found
    }
  }
  
  if (typeof value === 'string' && replacements) {
    // Replace placeholders like {{name}}
    return Object.entries(replacements).reduce(
      (str, [k, v]) => str.replace(new RegExp(`{{${k}}}`, 'g'), v),
      value
    );
  }
  
  return typeof value === 'string' ? value : key;
}

export default function AIProvidersPage({ params }: AIProvidersPageProps) {
  // ALL HOOKS AT TOP LEVEL - NO EXCEPTIONS
  const locale = params.locale || "en";
  const [t, setT] = useState<Record<string, any>>({});
  const [translationsLoaded, setTranslationsLoaded] = useState(false);
  const [providers, setProviders] = useState<AIProviderConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<AIProviderConfig | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingProvider, setEditingProvider] = useState<Partial<AIProviderConfig>>({});
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [showApiKey, setShowApiKey] = useState(false);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  // Helper function (uses state, so defined as useCallback)
  const getT = useCallback((key: string, replacements?: Record<string, string>): string => {
    return getTranslationValue(t, key, replacements);
  }, [t]);

  // Load translations effect
  useEffect(() => {
    const loadTranslations = async () => {
      try {
        const translations = await getTranslations(locale === "pt" ? "pt" : "en");
        setT(translations);
        setTranslationsLoaded(true);
      } catch (error) {
        console.error("Error loading translations:", error);
        setError("Failed to load translations");
        setTranslationsLoaded(true); // Prevent infinite loading
      }
    };
    loadTranslations();
  }, [locale]);

  // Load providers effect
  useEffect(() => {
    const loadProviders = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getUserAIProviders();
        
        if (data && Array.isArray(data)) {
          setProviders(data);
        } else {
          setProviders([]);
          console.warn("getUserAIProviders returned invalid data:", data);
        }
      } catch (error) {
        console.error("Error loading providers:", error);
        setError("Failed to load AI providers");
        setProviders([]);
      } finally {
        setLoading(false);
      }
    };

    // Only load providers after translations are loaded
    if (translationsLoaded) {
      loadProviders();
    }
  }, [translationsLoaded]);

  // Handler functions (all defined with useCallback for optimization)
  const handleEditProvider = useCallback(async (provider: AIProviderConfig) => {
    setSelectedProvider(provider);
    setEditingProvider({
      ...provider,
      apiKey: provider.apiKey?.includes("••••") ? "" : provider.apiKey,
    });
    setShowApiKey(false);
    setTestResult(null);
    
    try {
      const options = await getProviderOptions(provider.id);
      setAvailableModels(options.models || provider.modelOptions || []);
    } catch (error) {
      console.error("Error loading models:", error);
      setAvailableModels(provider.modelOptions || []);
    }
    
    setIsDialogOpen(true);
  }, []);

  const handleAddProvider = useCallback(() => {
    setSelectedProvider(null);
    setEditingProvider({});
    setShowApiKey(false);
    setTestResult(null);
    setAvailableModels([]);
    setIsDialogOpen(true);
  }, []);

  const handleSaveProvider = useCallback(async () => {
    if (!editingProvider.id) {
      alert(getTranslationValue(t, "settings.ai_providers.errors.provider_id_required"));
      return;
    }

    try {
      setSaving(true);
      
      // Check if API key is masked (not changed)
      const isMaskedKey = editingProvider.apiKey?.includes("••••");
      
      // Don't send masked API key to backend
      const providerData = {
        ...editingProvider,
        apiKey: isMaskedKey ? undefined : editingProvider.apiKey,
      };

      await saveAIProvider(providerData as AIProviderConfig);
      setIsDialogOpen(false);
      
      // Reload providers
      const data = await getUserAIProviders();
      if (data && Array.isArray(data)) {
        setProviders(data);
      }
    } catch (error) {
      console.error("Error saving provider:", error);
      alert(getTranslationValue(t, "settings.ai_providers.errors.saving"));
    } finally {
      setSaving(false);
    }
  }, [editingProvider, t]);

  const handleDeleteProvider = useCallback(async (providerId: string) => {
    if (deleteConfirm !== providerId) {
      setDeleteConfirm(providerId);
      setTimeout(() => setDeleteConfirm(null), 3000);
      return;
    }

    try {
      await deleteAIProvider(providerId);
      setDeleteConfirm(null);
      
      // Reload providers
      const data = await getUserAIProviders();
      if (data && Array.isArray(data)) {
        setProviders(data);
      }
    } catch (error) {
      console.error("Error deleting provider:", error);
      alert(getTranslationValue(t, "settings.ai_providers.errors.deleting"));
    }
  }, [deleteConfirm, t]);

  const handleTestConnection = useCallback(async () => {
    try {
      setTesting(true);
      setTestResult(null);
      
      if (!editingProvider.apiKey || editingProvider.apiKey.includes("••••")) {
        setTestResult({
          success: false,
          message: getTranslationValue(t, "settings.ai_providers.dialog.enter_api_key")
        });
        return;
      }

      const result = await validateAPIKey(editingProvider.id!, editingProvider.apiKey);
      
      setTestResult({
        success: result.valid,
        message: result.message || (result.valid 
          ? getTranslationValue(t, "settings.ai_providers.dialog.connection_successful")
          : getTranslationValue(t, "settings.ai_providers.dialog.connection_failed")
        )
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: getTranslationValue(t, "settings.ai_providers.dialog.error_testing")
      });
    } finally {
      setTesting(false);
    }
  }, [editingProvider, t]);

  const toggleActive = useCallback(async (provider: AIProviderConfig) => {
    try {
      await updateAIProvider(provider.id, {
        ...provider,
        isActive: !provider.isActive,
      });
      
      // Reload providers
      const data = await getUserAIProviders();
      if (data && Array.isArray(data)) {
        setProviders(data);
      }
    } catch (error) {
      console.error("Error toggling provider:", error);
    }
  }, []);

  // Loading state - show before translations and providers are loaded
  if (loading || !translationsLoaded) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto" />
          <p className="text-base text-gray-500">
            {locale === "pt" ? "Carregando..." : "Loading..."}
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <Alert className="rounded-2xl border-red-200 bg-red-50">
          <AlertDescription className="text-red-700">
            {error}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-semibold tracking-tight text-gray-900">
            {getT("settings.ai_providers.title")}
          </h1>
          <p className="text-base text-gray-500 leading-relaxed">
            {getT("settings.ai_providers.subtitle")}
          </p>
        </div>
        <Button 
          onClick={handleAddProvider} 
          className="bg-blue-500 hover:bg-blue-600 text-white rounded-xl px-4 py-2 transition-all ease-in-out duration-200 flex items-center gap-2"
        >
          <PlusIcon />
          {getT("settings.ai_providers.add")}
        </Button>
      </div>

      {/* Info Card */}
      <Card className="rounded-2xl bg-blue-50 border border-blue-100 shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-medium flex items-center gap-2 text-blue-900">
            <LightbulbIcon />
            {getT("settings.ai_providers.tip_title")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-blue-700 leading-relaxed">
            {getT("settings.ai_providers.tip_description")}
          </p>
        </CardContent>
      </Card>

      {/* Providers Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {providers.map((provider) => {
          const hasApiKey = provider.apiKey && provider.apiKey.length > 0;
          const isConfigured = provider.isConfigured || hasApiKey;

          return (
            <Card
              key={provider.id}
              className={`rounded-2xl bg-white shadow-sm border transition-all ease-in-out duration-200 hover:shadow-md ${
                provider.isActive ? "border-green-200" : "border-gray-100"
              }`}
            >
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {PROVIDER_LOGOS[provider.id] && (
                      <Image
                        src={PROVIDER_LOGOS[provider.id]}
                        alt={provider.name}
                        width={32}
                        height={32}
                        className="rounded"
                      />
                    )}
                    <CardTitle className="text-lg font-medium">{provider.name}</CardTitle>
                  </div>
                  <Badge
                    variant={provider.isActive ? "default" : "secondary"}
                    className={`rounded-full px-3 py-1 text-xs font-medium ${
                      provider.isActive
                        ? "bg-green-100 text-green-700 hover:bg-green-100"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-100"
                    }`}
                  >
                    {provider.isActive ? getT("settings.ai_providers.active") : getT("settings.ai_providers.inactive")}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-500">{getT("settings.ai_providers.status")}:</span>
                  {isConfigured ? (
                    <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 rounded-full">
                      <Check className="w-3 h-3 mr-1" />
                      {getT("settings.ai_providers.configured")}
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="bg-gray-50 text-gray-600 border-gray-200 rounded-full">
                      <X className="w-3 h-3 mr-1" />
                      {getT("settings.ai_providers.not_configured")}
                    </Badge>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button
                    onClick={() => handleEditProvider(provider)}
                    variant="outline"
                    size="sm"
                    className="flex-1 rounded-xl border-gray-200 hover:bg-gray-50 transition-all"
                  >
                    <SettingsIcon />
                    {getT("settings.ai_providers.configure")}
                  </Button>
                  
                  {isConfigured && (
                    <Button
                      onClick={() => toggleActive(provider)}
                      variant="outline"
                      size="sm"
                      className={`rounded-xl transition-all ${
                        provider.isActive
                          ? "border-green-200 bg-green-50 hover:bg-green-100 text-green-700"
                          : "border-gray-200 hover:bg-gray-50"
                      }`}
                    >
                      <PowerIcon />
                    </Button>
                  )}
                  
                  <Button
                    onClick={() => handleDeleteProvider(provider.id)}
                    variant="outline"
                    size="sm"
                    className={`rounded-xl transition-all ${
                      deleteConfirm === provider.id
                        ? "border-red-200 bg-red-50 hover:bg-red-100 text-red-700"
                        : "border-gray-200 hover:bg-gray-50"
                    }`}
                  >
                    {deleteConfirm === provider.id ? getT("settings.ai_providers.confirm_delete") : <TrashIcon />}
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Configuration Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl rounded-2xl">
          <DialogHeader>
            <DialogTitle className="text-2xl font-semibold">
              {selectedProvider
                ? getT("settings.ai_providers.dialog.edit_title", { name: selectedProvider.name })
                : getT("settings.ai_providers.dialog.add_title")}
            </DialogTitle>
            <DialogDescription className="text-gray-500">
              {getT("settings.ai_providers.dialog.description")}
            </DialogDescription>
          </DialogHeader>

          <Tabs defaultValue="basic" className="w-full">
            <TabsList className="grid w-full grid-cols-3 rounded-xl bg-gray-100 p-1">
              <TabsTrigger value="basic" className="rounded-lg">
                {getT("settings.ai_providers.dialog.tabs.basic")}
              </TabsTrigger>
              <TabsTrigger value="advanced" className="rounded-lg">
                {getT("settings.ai_providers.dialog.tabs.advanced")}
              </TabsTrigger>
              <TabsTrigger value="test" className="rounded-lg">
                {getT("settings.ai_providers.dialog.tabs.test")}
              </TabsTrigger>
            </TabsList>

            {/* Basic Tab */}
            <TabsContent value="basic" className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="provider-id" className="text-sm font-medium">
                  {getT("settings.ai_providers.dialog.provider_id")}
                </Label>
                <Input
                  id="provider-id"
                  value={editingProvider.id || ""}
                  onChange={(e) => setEditingProvider({ ...editingProvider, id: e.target.value })}
                  disabled={!!selectedProvider}
                  className="rounded-xl border-gray-300 focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="provider-name" className="text-sm font-medium">
                  {getT("settings.ai_providers.dialog.provider_name")}
                </Label>
                <Input
                  id="provider-name"
                  value={editingProvider.name || ""}
                  onChange={(e) => setEditingProvider({ ...editingProvider, name: e.target.value })}
                  className="rounded-xl border-gray-300 focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="api-key" className="text-sm font-medium">
                  {getT("settings.ai_providers.api_key")}
                </Label>
                <div className="relative">
                  <Input
                    id="api-key"
                    type={showApiKey ? "text" : "password"}
                    value={editingProvider.apiKey || ""}
                    onChange={(e) => setEditingProvider({ ...editingProvider, apiKey: e.target.value })}
                    placeholder={
                      selectedProvider?.apiKey?.includes("••••")
                        ? getT("settings.ai_providers.dialog.api_key_configured")
                        : getT("settings.ai_providers.dialog.api_key_placeholder")
                    }
                    className="rounded-xl border-gray-300 focus:ring-2 focus:ring-blue-500 pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute right-2 top-1/2 -translate-y-1/2"
                  >
                    {showApiKey ? <EyeOffIcon /> : <EyeIcon />}
                  </Button>
                </div>
              </div>

              {availableModels.length > 0 && (
                <div className="space-y-2">
                  <Label htmlFor="model" className="text-sm font-medium">
                    {getT("settings.ai_providers.dialog.model")}
                  </Label>
                  <Select
                    value={editingProvider.model || ""}
                    onValueChange={(value) => setEditingProvider({ ...editingProvider, model: value })}
                  >
                    <SelectTrigger className="rounded-xl border-gray-300">
                      <SelectValue placeholder={getT("settings.ai_providers.dialog.select_model")} />
                    </SelectTrigger>
                    <SelectContent>
                      {availableModels.map((model) => (
                        <SelectItem key={model} value={model}>
                          {model}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </TabsContent>

            {/* Advanced Tab */}
            <TabsContent value="advanced" className="space-y-4 mt-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="temperature" className="text-sm font-medium">
                    {getT("settings.ai_providers.dialog.temperature")}
                  </Label>
                  <span className="text-sm text-gray-500">{editingProvider.temperature || 0.7}</span>
                </div>
                <Slider
                  id="temperature"
                  min={0}
                  max={2}
                  step={0.1}
                  value={[editingProvider.temperature || 0.7]}
                  onValueChange={([value]) => setEditingProvider({ ...editingProvider, temperature: value })}
                  className="w-full"
                />
                <p className="text-xs text-gray-500">
                  {getT("settings.ai_providers.dialog.temperature_description")}
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="max-tokens" className="text-sm font-medium">
                  {getT("settings.ai_providers.dialog.max_tokens")}
                </Label>
                <Input
                  id="max-tokens"
                  type="number"
                  value={editingProvider.maxTokens || ""}
                  onChange={(e) => setEditingProvider({ ...editingProvider, maxTokens: parseInt(e.target.value) })}
                  className="rounded-xl border-gray-300 focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500">
                  {getT("settings.ai_providers.dialog.max_tokens_description")}
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="base-url" className="text-sm font-medium">
                  {getT("settings.ai_providers.dialog.base_url")}
                </Label>
                <Input
                  id="base-url"
                  value={editingProvider.baseUrl || ""}
                  onChange={(e) => setEditingProvider({ ...editingProvider, baseUrl: e.target.value })}
                  placeholder="https://api.example.com"
                  className="rounded-xl border-gray-300 focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500">
                  {getT("settings.ai_providers.dialog.base_url_description")}
                </p>
              </div>
            </TabsContent>

            {/* Test Tab */}
            <TabsContent value="test" className="space-y-4 mt-4">
              <p className="text-sm text-gray-600">
                {getT("settings.ai_providers.dialog.test_description")}
              </p>

              <Button
                onClick={handleTestConnection}
                disabled={testing || !editingProvider.apiKey || editingProvider.apiKey.includes("••••")}
                className="w-full bg-blue-500 hover:bg-blue-600 text-white rounded-xl transition-all"
              >
                {testing ? (
                  <>
                    <LoaderIcon />
                    {getT("settings.ai_providers.dialog.testing")}
                  </>
                ) : (
                  <>
                    <TestTubeIcon />
                    {getT("settings.ai_providers.dialog.test_connection")}
                  </>
                )}
              </Button>

              {testResult && (
                <Alert
                  className={`rounded-2xl ${
                    testResult.success
                      ? "border-green-200 bg-green-50"
                      : "border-red-200 bg-red-50"
                  }`}
                >
                  <AlertDescription
                    className={testResult.success ? "text-green-700" : "text-red-700"}
                  >
                    {testResult.success ? <Check className="w-4 h-4 inline mr-2" /> : <X className="w-4 h-4 inline mr-2" />}
                    {testResult.message}
                  </AlertDescription>
                </Alert>
              )}
            </TabsContent>
          </Tabs>

          <div className="flex gap-3 mt-6">
            <Button
              variant="outline"
              onClick={() => setIsDialogOpen(false)}
              className="flex-1 rounded-xl border-gray-300 hover:bg-gray-50"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSaveProvider}
              disabled={saving || !editingProvider.id}
              className="flex-1 bg-blue-500 hover:bg-blue-600 text-white rounded-xl transition-all"
            >
              {saving ? (
                <>
                  <LoaderIcon />
                  {getT("settings.ai_providers.dialog.saving")}
                </>
              ) : (
                getT("settings.ai_providers.save")
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
