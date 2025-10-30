"use client";

import React, { useState, useEffect } from "react";
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

export default function AIProvidersPage({ params }: AIProvidersPageProps) {
  const locale = params.locale || "en";
  const [t, setT] = useState<Record<string, any>>({});
  const [translationsLoaded, setTranslationsLoaded] = useState(false);
  const [providers, setProviders] = useState<AIProviderConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProvider, setSelectedProvider] = useState<AIProviderConfig | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingProvider, setEditingProvider] = useState<Partial<AIProviderConfig>>({});
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [showApiKey, setShowApiKey] = useState(false);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  useEffect(() => {
    const loadTranslations = async () => {
      try {
        const translations = await getTranslations(locale === "pt" ? "pt" : "en");
        setT(translations);
        setTranslationsLoaded(true);
      } catch (error) {
        console.error("Error loading translations:", error);
        setTranslationsLoaded(true); // Set to true even on error to prevent infinite loading
      }
    };
    loadTranslations();
    loadProviders();
  }, [locale]);

  // Helper function to safely get nested translation keys
  const getT = (key: string, replacements?: Record<string, string>): string => {
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
  };

  const loadProviders = async () => {
    try {
      setLoading(true);
      const data = await getUserAIProviders();
      
      // Use only database-driven providers - no fallback, no merge
      if (data && Array.isArray(data)) {
        setProviders(data);
      } else {
        // If API returns invalid data, show empty state
        setProviders([]);
        console.warn("getUserAIProviders returned invalid data:", data);
      }
    } catch (error) {
      console.error("Error loading providers:", error);
      // On error, show empty state - no fallback
      setProviders([]);
    } finally {
      setLoading(false);
    }
  };

  const handleEditProvider = async (provider: AIProviderConfig) => {
    setSelectedProvider(provider);
    setEditingProvider({
      ...provider,
      // Don't pre-fill API key if it's masked
      apiKey: provider.apiKey?.includes("••••") ? "" : provider.apiKey,
    });
    setShowApiKey(false);
    setTestResult(null);
    
    // Load available models for this provider
    try {
      const options = await getProviderOptions(provider.id);
      setAvailableModels(options.models || provider.modelOptions || []);
    } catch (error) {
      console.error("Error loading models:", error);
      setAvailableModels(provider.modelOptions || []);
    }
    
    setIsDialogOpen(true);
  };

  const handleAddProvider = () => {
    setSelectedProvider(null);
    setEditingProvider({
      id: "",
      name: "",
      apiKey: "",
      isActive: false,
      selectedModel: "",
      temperature: 0.7,
      maxTokens: 1000,
    });
    setShowApiKey(false);
    setTestResult(null);
    setAvailableModels([]);
    setIsDialogOpen(true);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      if (!editingProvider.id) {
        throw new Error(getT("pages.ai_providers.errors.provider_id_required"));
      }

      // Only send API key if it was actually changed
      const updates: any = {
        ...editingProvider,
      };

      // Don't send empty or masked API keys
      if (!updates.apiKey || updates.apiKey.includes("••••")) {
        delete updates.apiKey;
      }

      if (selectedProvider) {
        // Update existing provider
        await updateAIProvider(selectedProvider.id, updates);
      } else {
        // Create new provider
        await saveAIProvider(updates as AIProviderConfig);
      }
      
      setIsDialogOpen(false);
      await loadProviders();
    } catch (error) {
      console.error("Error saving provider:", error);
      alert(getT("pages.ai_providers.errors.saving"));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (providerId: string) => {
    if (deleteConfirm !== providerId) {
      setDeleteConfirm(providerId);
      setTimeout(() => setDeleteConfirm(null), 3000);
      return;
    }

    try {
      await deleteAIProvider(providerId);
      setDeleteConfirm(null);
      await loadProviders();
    } catch (error) {
      console.error("Error deleting provider:", error);
      alert(getT("pages.ai_providers.errors.deleting"));
    }
  };

  const handleTestConnection = async () => {
    try {
      setTesting(true);
      setTestResult(null);
      
      if (!editingProvider.apiKey || editingProvider.apiKey.includes("••••")) {
        setTestResult({
          success: false,
          message: getT("pages.ai_providers.dialog.enter_api_key")
        });
        return;
      }

      const result = await validateAPIKey(editingProvider.id!, editingProvider.apiKey);
      
      setTestResult({
        success: result.valid,
        message: result.message || (result.valid 
          ? getT("pages.ai_providers.dialog.connection_successful")
          : getT("pages.ai_providers.dialog.connection_failed")
        )
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: getT("pages.ai_providers.dialog.error_testing")
      });
    } finally {
      setTesting(false);
    }
  };

  const toggleActive = async (provider: AIProviderConfig) => {
    try {
      await updateAIProvider(provider.id, {
        isActive: !provider.isActive,
      });
      
      await loadProviders();
    } catch (error) {
      console.error("Error toggling provider:", error);
    }
  };

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

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-semibold tracking-tight text-gray-900">
            {getT("pages.ai_providers.title")}
          </h1>
          <p className="text-base text-gray-500 leading-relaxed">
            {getT("pages.ai_providers.subtitle")}
          </p>
        </div>
        <Button 
          onClick={handleAddProvider} 
          className="bg-blue-500 hover:bg-blue-600 text-white rounded-xl px-4 py-2 transition-all ease-in-out duration-200 flex items-center gap-2"
        >
          <PlusIcon />
          {getT("pages.ai_providers.add")}
        </Button>
      </div>

      {/* Info Card */}
      <Card className="rounded-2xl bg-blue-50 border border-blue-100 shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-medium flex items-center gap-2 text-blue-900">
            <LightbulbIcon />
            {getT("pages.ai_providers.tip_title")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-blue-700 leading-relaxed">
            {getT("pages.ai_providers.tip_description")}
          </p>
        </CardContent>
      </Card>

      {/* Providers Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {providers.map((provider) => {
          // A masked API key (••••) means an API key IS configured
          const hasApiKey = provider.apiKey && provider.apiKey.length > 0;
          const isConfigured = provider.isConfigured || hasApiKey;

          return (
            <Card
              key={provider.id}
              className={`rounded-2xl bg-white shadow-sm border transition-all ease-in-out duration-200 hover:shadow-md ${
                provider.isActive ? "border-green-200" : "border-gray-100"
              }`}
            >
              <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {PROVIDER_LOGOS[provider.id] && (
                      <div className="w-10 h-10 relative flex-shrink-0">
                        <Image
                          src={PROVIDER_LOGOS[provider.id]}
                          alt={provider.name}
                          width={40}
                          height={40}
                          className="object-contain"
                        />
                      </div>
                    )}
                    <div className="min-w-0">
                      <CardTitle className="text-lg font-medium text-gray-900 truncate">
                        {provider.name}
                      </CardTitle>
                      <p className="text-xs text-gray-500 truncate">
                        {provider.selectedModel || "No model selected"}
                      </p>
                    </div>
                  </div>
                  <Badge
                    className={
                      provider.isActive
                        ? "bg-green-100 text-green-700 border-green-200"
                        : "bg-gray-100 text-gray-600 border-gray-200"
                    }
                  >
                    {provider.isActive
                      ? getT("pages.ai_providers.active")
                      : getT("pages.ai_providers.inactive")}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Configuration Status */}
                <div className="flex items-center justify-between text-sm py-2 px-3 bg-gray-50 rounded-xl">
                  <span className="text-gray-600 font-medium">
                    {getT("pages.ai_providers.status")}:
                  </span>
                  <span className="flex items-center gap-1.5">
                    {isConfigured ? (
                      <>
                        <Check className="h-4 w-4 text-green-600" />
                        <span className="text-green-700 font-medium">
                          {getT("pages.ai_providers.configured")}
                        </span>
                      </>
                    ) : (
                      <>
                        <X className="h-4 w-4 text-red-600" />
                        <span className="text-red-700 font-medium">
                          {getT("pages.ai_providers.not_configured")}
                        </span>
                      </>
                    )}
                  </span>
                </div>

                {/* Configuration Details */}
                {isConfigured && (
                  <div className="text-xs text-gray-500 space-y-1 px-3">
                    {provider.temperature !== undefined && (
                      <div className="flex justify-between">
                        <span>Temperature:</span>
                        <span className="font-medium">{provider.temperature}</span>
                      </div>
                    )}
                    {provider.maxTokens !== undefined && (
                      <div className="flex justify-between">
                        <span>Max Tokens:</span>
                        <span className="font-medium">{provider.maxTokens}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-2 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleEditProvider(provider)}
                    className="flex-1 gap-2 rounded-xl transition-all"
                  >
                    <SettingsIcon />
                    {getT("pages.ai_providers.configure")}
                  </Button>
                  {isConfigured && (
                    <Button
                      size="sm"
                      variant={provider.isActive ? "destructive" : "default"}
                      onClick={() => toggleActive(provider)}
                      className="gap-2 rounded-xl transition-all"
                    >
                      <PowerIcon />
                      {provider.isActive
                        ? getT("pages.ai_providers.deactivate")
                        : getT("pages.ai_providers.activate")}
                    </Button>
                  )}
                  {provider.id !== "openai" && provider.id !== "anthropic" && (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDelete(provider.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50 rounded-xl transition-all"
                    >
                      {deleteConfirm === provider.id ? (
                        <span className="text-xs font-medium">
                          {getT("pages.ai_providers.confirm_delete")}
                        </span>
                      ) : (
                        <TrashIcon />
                      )}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Edit Provider Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl">
          <DialogHeader className="space-y-2">
            <DialogTitle className="text-2xl font-semibold text-gray-900">
              {selectedProvider
                ? getT("pages.ai_providers.dialog.edit_title", { name: selectedProvider.name })
                : getT("pages.ai_providers.dialog.add_title")}
            </DialogTitle>
            <DialogDescription className="text-base text-gray-500">
              {getT("pages.ai_providers.dialog.description")}
            </DialogDescription>
          </DialogHeader>

          <Tabs defaultValue="basic" className="w-full mt-6">
            <TabsList className="grid w-full grid-cols-3 bg-gray-100 rounded-xl p-1">
              <TabsTrigger value="basic" className="rounded-lg transition-all">
                {getT("pages.ai_providers.dialog.tabs.basic")}
              </TabsTrigger>
              <TabsTrigger value="advanced" className="rounded-lg transition-all">
                {getT("pages.ai_providers.dialog.tabs.advanced")}
              </TabsTrigger>
              <TabsTrigger value="test" className="rounded-lg transition-all">
                {getT("pages.ai_providers.dialog.tabs.test")}
              </TabsTrigger>
            </TabsList>

            {/* Basic Tab */}
            <TabsContent value="basic" className="space-y-6 mt-6">
              {!selectedProvider && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="provider-id" className="text-sm font-medium text-gray-700">
                      {getT("pages.ai_providers.dialog.provider_id")}
                    </Label>
                    <Input
                      id="provider-id"
                      value={editingProvider.id || ""}
                      onChange={(e) =>
                        setEditingProvider({ ...editingProvider, id: e.target.value })
                      }
                      placeholder="e.g., custom-provider"
                      className="border-gray-300 rounded-xl px-3 py-2 focus:ring-2 focus:ring-blue-500 transition-all"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="provider-name" className="text-sm font-medium text-gray-700">
                      {getT("pages.ai_providers.dialog.provider_name")}
                    </Label>
                    <Input
                      id="provider-name"
                      value={editingProvider.name || ""}
                      onChange={(e) =>
                        setEditingProvider({ ...editingProvider, name: e.target.value })
                      }
                      placeholder="e.g., Custom AI Provider"
                      className="border-gray-300 rounded-xl px-3 py-2 focus:ring-2 focus:ring-blue-500 transition-all"
                    />
                  </div>
                </>
              )}

              <div className="space-y-2">
                <Label htmlFor="api-key" className="text-sm font-medium text-gray-700">
                  {getT("pages.ai_providers.api_key")}
                </Label>
                <div className="relative">
                  <Input
                    id="api-key"
                    type={showApiKey ? "text" : "password"}
                    value={editingProvider.apiKey || ""}
                    onChange={(e) =>
                      setEditingProvider({ ...editingProvider, apiKey: e.target.value })
                    }
                    placeholder={
                      selectedProvider?.apiKey?.includes("••••")
                        ? getT("pages.ai_providers.dialog.api_key_configured")
                        : getT("pages.ai_providers.dialog.api_key_placeholder")
                    }
                    className="border-gray-300 rounded-xl px-3 py-2 pr-12 focus:ring-2 focus:ring-blue-500 transition-all"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                    onClick={() => setShowApiKey(!showApiKey)}
                  >
                    {showApiKey ? <EyeOffIcon /> : <EyeIcon />}
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="model" className="text-sm font-medium text-gray-700">
                  {getT("pages.ai_providers.dialog.model")}
                </Label>
                <Select
                  value={editingProvider.selectedModel || ""}
                  onValueChange={(value) =>
                    setEditingProvider({ ...editingProvider, selectedModel: value })
                  }
                >
                  <SelectTrigger className="rounded-xl border-gray-300 focus:ring-2 focus:ring-blue-500">
                    <SelectValue placeholder={getT("pages.ai_providers.dialog.select_model")} />
                  </SelectTrigger>
                  <SelectContent className="rounded-xl">
                    {(availableModels.length > 0 ? availableModels : editingProvider.modelOptions || []).map((model) => (
                      <SelectItem key={model} value={model} className="rounded-lg">
                        {model}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>

            {/* Advanced Tab */}
            <TabsContent value="advanced" className="space-y-6 mt-6">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label htmlFor="temperature" className="text-sm font-medium text-gray-700">
                    {getT("pages.ai_providers.dialog.temperature")}
                  </Label>
                  <span className="text-sm font-semibold text-blue-600">
                    {editingProvider.temperature || 0.7}
                  </span>
                </div>
                <Slider
                  id="temperature"
                  min={0}
                  max={2}
                  step={0.1}
                  value={[editingProvider.temperature || 0.7]}
                  onValueChange={(value) =>
                    setEditingProvider({ ...editingProvider, temperature: value[0] })
                  }
                  className="py-2"
                />
                <p className="text-xs text-gray-500 leading-relaxed">
                  {getT("pages.ai_providers.dialog.temperature_description")}
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="max-tokens" className="text-sm font-medium text-gray-700">
                  {getT("pages.ai_providers.dialog.max_tokens")}
                </Label>
                <Input
                  id="max-tokens"
                  type="number"
                  value={editingProvider.maxTokens || 1000}
                  onChange={(e) =>
                    setEditingProvider({
                      ...editingProvider,
                      maxTokens: parseInt(e.target.value) || 1000,
                    })
                  }
                  min={1}
                  max={32000}
                  className="border-gray-300 rounded-xl px-3 py-2 focus:ring-2 focus:ring-blue-500 transition-all"
                />
                <p className="text-xs text-gray-500 leading-relaxed">
                  {getT("pages.ai_providers.dialog.max_tokens_description")}
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="base-url" className="text-sm font-medium text-gray-700">
                  {getT("pages.ai_providers.dialog.base_url")}
                </Label>
                <Input
                  id="base-url"
                  value={editingProvider.baseUrl || ""}
                  onChange={(e) =>
                    setEditingProvider({ ...editingProvider, baseUrl: e.target.value })
                  }
                  placeholder="https://api.example.com/v1"
                  className="border-gray-300 rounded-xl px-3 py-2 focus:ring-2 focus:ring-blue-500 transition-all"
                />
                <p className="text-xs text-gray-500 leading-relaxed">
                  {getT("pages.ai_providers.dialog.base_url_description")}
                </p>
              </div>
            </TabsContent>

            {/* Test Tab */}
            <TabsContent value="test" className="space-y-6 mt-6">
              <Alert className="rounded-xl bg-blue-50 border-blue-100">
                <AlertDescription className="text-sm text-blue-700 leading-relaxed">
                  {getT("pages.ai_providers.dialog.test_description")}
                </AlertDescription>
              </Alert>

              <Button
                onClick={handleTestConnection}
                disabled={testing || !editingProvider.apiKey}
                className="w-full gap-2 rounded-xl bg-blue-500 hover:bg-blue-600 text-white transition-all"
              >
                {testing ? (
                  <>
                    <LoaderIcon />
                    {getT("pages.ai_providers.dialog.testing")}
                  </>
                ) : (
                  <>
                    <TestTubeIcon />
                    {getT("pages.ai_providers.dialog.test_connection")}
                  </>
                )}
              </Button>

              {testResult && (
                <Alert
                  className={
                    testResult.success
                      ? "rounded-xl bg-green-50 border-green-200"
                      : "rounded-xl bg-red-50 border-red-200"
                  }
                >
                  <AlertDescription className={`flex items-center gap-2 text-sm font-medium ${
                    testResult.success ? "text-green-700" : "text-red-700"
                  }`}>
                    {testResult.success ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <X className="h-4 w-4" />
                    )}
                    {testResult.message}
                  </AlertDescription>
                </Alert>
              )}
            </TabsContent>
          </Tabs>

          <div className="flex gap-3 justify-end pt-6 mt-6 border-t border-gray-100">
            <Button 
              variant="outline" 
              onClick={() => setIsDialogOpen(false)}
              className="rounded-xl px-6 transition-all"
            >
              {getT("common.cancel")}
            </Button>
            <Button 
              onClick={handleSave} 
              disabled={saving}
              className="rounded-xl px-6 bg-blue-500 hover:bg-blue-600 text-white transition-all flex items-center gap-2"
            >
              {saving ? (
                <>
                  <LoaderIcon />
                  {getT("pages.ai_providers.dialog.saving")}
                </>
              ) : (
                getT("common.save")
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
