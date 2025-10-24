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
// Using standard emoji/text instead of lucide-react icons for compatibility

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

  const isPortuguese = params.locale === "pt";

  useEffect(() => {
    loadProviders();
  }, []);

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
        throw new Error(isPortuguese ? "ID do provedor é obrigatório" : "Provider ID is required");
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
      alert(isPortuguese ? "Erro ao salvar provedor" : "Error saving provider");
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
      alert(isPortuguese ? "Erro ao deletar provedor" : "Error deleting provider");
    }
  };

  const handleTestConnection = async () => {
    try {
      setTesting(true);
      setTestResult(null);
      
      if (!editingProvider.apiKey || editingProvider.apiKey.includes("••••")) {
        setTestResult({
          success: false,
          message: isPortuguese ? "Por favor, insira uma chave de API" : "Please enter an API key"
        });
        return;
      }

      const result = await validateAPIKey(editingProvider.id!, editingProvider.apiKey);
      
      setTestResult({
        success: result.valid,
        message: result.message || (result.valid 
          ? (isPortuguese ? "Conexão bem-sucedida!" : "Connection successful!")
          : (isPortuguese ? "Falha na conexão" : "Connection failed")
        )
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: isPortuguese ? "Erro ao testar conexão" : "Error testing connection"
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">
            {isPortuguese ? "Carregando provedores..." : "Loading providers..."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {isPortuguese ? "Provedores de IA" : "AI Providers"}
          </h1>
          <p className="text-muted-foreground mt-1">
            {isPortuguese
              ? "Configure e gerencie seus provedores de IA"
              : "Configure and manage your AI providers"}
          </p>
        </div>
        <Button onClick={handleAddProvider} className="gap-2">
          <span>➕</span>
          {isPortuguese ? "Adicionar Provedor" : "Add Provider"}
        </Button>
      </div>

      {/* Info Card */}
      <Card className="bg-blue-50 border-blue-200 dark:bg-blue-950 dark:border-blue-800">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            💡 {isPortuguese ? "Dica" : "Tip"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {isPortuguese
              ? "Clique no botão de configurações para editar todas as opções do provedor. Use o botão de teste para verificar se sua chave de API está funcionando."
              : "Click the settings button to edit all provider options. Use the test button to verify your API key is working."}
          </p>
        </CardContent>
      </Card>

      {/* Providers Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {providers.map((provider) => {
          // A masked API key (••••) means an API key IS configured
          const hasApiKey = provider.apiKey && provider.apiKey.length > 0;
          const isConfigured = provider.isConfigured || hasApiKey;

          return (
            <Card
              key={provider.id}
              className={`hover:shadow-md transition-shadow ${
                provider.isActive ? "border-green-500" : ""
              }`}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {PROVIDER_LOGOS[provider.id] && (
                      <div className="w-10 h-10 relative">
                        <Image
                          src={PROVIDER_LOGOS[provider.id]}
                          alt={provider.name}
                          width={40}
                          height={40}
                          className="object-contain"
                        />
                      </div>
                    )}
                    <div>
                      <CardTitle className="text-lg">{provider.name}</CardTitle>
                      <p className="text-xs text-muted-foreground">
                        {provider.selectedModel || "No model selected"}
                      </p>
                    </div>
                  </div>
                  <Badge
                    className={
                      provider.isActive
                        ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100"
                        : "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100"
                    }
                  >
                    {provider.isActive
                      ? isPortuguese
                        ? "Ativo"
                        : "Active"
                      : isPortuguese
                      ? "Inativo"
                      : "Inactive"}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-3">
                {/* Configuration Status */}
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">
                    {isPortuguese ? "Status" : "Status"}:
                  </span>
                  <span className="font-medium">
                    {isConfigured ? (
                      <span className="text-green-600 flex items-center gap-1">
                        <span>✓</span>
                        {isPortuguese ? "Configurado" : "Configured"}
                      </span>
                    ) : (
                      <span className="text-red-600 flex items-center gap-1">
                        <span>✗</span>
                        {isPortuguese ? "Não Configurado" : "Not Configured"}
                      </span>
                    )}
                  </span>
                </div>

                {/* Configuration Details */}
                {isConfigured && (
                  <div className="text-xs text-muted-foreground space-y-1">
                    {provider.temperature !== undefined && (
                      <div>Temperature: {provider.temperature}</div>
                    )}
                    {provider.maxTokens !== undefined && (
                      <div>Max Tokens: {provider.maxTokens}</div>
                    )}
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-2 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleEditProvider(provider)}
                    className="flex-1 gap-2"
                  >
                    <span>⚙️</span>
                    {isPortuguese ? "Configurar" : "Configure"}
                  </Button>
                  {isConfigured && (
                    <Button
                      size="sm"
                      variant={provider.isActive ? "destructive" : "default"}
                      onClick={() => toggleActive(provider)}
                      className="gap-2"
                    >
                      {provider.isActive
                        ? isPortuguese
                          ? "Desativar"
                          : "Deactivate"
                        : isPortuguese
                        ? "Ativar"
                        : "Activate"}
                    </Button>
                  )}
                  {provider.id !== "openai" && provider.id !== "anthropic" && (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDelete(provider.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      {deleteConfirm === provider.id ? (
                        <span className="text-xs">
                          {isPortuguese ? "Confirmar?" : "Confirm?"}
                        </span>
                      ) : (
                        <span>🗑️</span>
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
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {selectedProvider
                ? isPortuguese
                  ? `Configurar ${selectedProvider.name}`
                  : `Configure ${selectedProvider.name}`
                : isPortuguese
                ? "Adicionar Novo Provedor"
                : "Add New Provider"}
            </DialogTitle>
            <DialogDescription>
              {isPortuguese
                ? "Configure as opções do provedor de IA"
                : "Configure AI provider options"}
            </DialogDescription>
          </DialogHeader>

          <Tabs defaultValue="basic" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="basic">
                {isPortuguese ? "Básico" : "Basic"}
              </TabsTrigger>
              <TabsTrigger value="advanced">
                {isPortuguese ? "Avançado" : "Advanced"}
              </TabsTrigger>
              <TabsTrigger value="test">
                {isPortuguese ? "Testar" : "Test"}
              </TabsTrigger>
            </TabsList>

            {/* Basic Tab */}
            <TabsContent value="basic" className="space-y-4 mt-4">
              {!selectedProvider && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="provider-id">
                      {isPortuguese ? "ID do Provedor" : "Provider ID"}
                    </Label>
                    <Input
                      id="provider-id"
                      value={editingProvider.id || ""}
                      onChange={(e) =>
                        setEditingProvider({ ...editingProvider, id: e.target.value })
                      }
                      placeholder="e.g., custom-provider"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="provider-name">
                      {isPortuguese ? "Nome do Provedor" : "Provider Name"}
                    </Label>
                    <Input
                      id="provider-name"
                      value={editingProvider.name || ""}
                      onChange={(e) =>
                        setEditingProvider({ ...editingProvider, name: e.target.value })
                      }
                      placeholder="e.g., Custom AI Provider"
                    />
                  </div>
                </>
              )}

              <div className="space-y-2">
                <Label htmlFor="api-key">
                  {isPortuguese ? "Chave de API" : "API Key"}
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
                        ? isPortuguese
                          ? "✓ API Key configurada - Digite para alterar"
                          : "✓ API Key configured - Enter to change"
                        : isPortuguese
                        ? "Digite sua API Key"
                        : "Enter your API Key"
                    }
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3"
                    onClick={() => setShowApiKey(!showApiKey)}
                  >
                    {showApiKey ? <span>🙈</span> : <span>👁️</span>}
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="model">
                  {isPortuguese ? "Modelo" : "Model"}
                </Label>
                <Select
                  value={editingProvider.selectedModel || ""}
                  onValueChange={(value) =>
                    setEditingProvider({ ...editingProvider, selectedModel: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder={isPortuguese ? "Selecione um modelo" : "Select a model"} />
                  </SelectTrigger>
                  <SelectContent>
                    {(availableModels.length > 0 ? availableModels : editingProvider.modelOptions || []).map((model) => (
                      <SelectItem key={model} value={model}>
                        {model}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>

            {/* Advanced Tab */}
            <TabsContent value="advanced" className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="temperature">
                  {isPortuguese ? "Temperatura" : "Temperature"}: {editingProvider.temperature || 0.7}
                </Label>
                <Slider
                  id="temperature"
                  min={0}
                  max={2}
                  step={0.1}
                  value={[editingProvider.temperature || 0.7]}
                  onValueChange={(value) =>
                    setEditingProvider({ ...editingProvider, temperature: value[0] })
                  }
                />
                <p className="text-xs text-muted-foreground">
                  {isPortuguese
                    ? "Controla a aleatoriedade da saída. Valores mais altos geram saídas mais criativas."
                    : "Controls output randomness. Higher values make output more creative."}
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="max-tokens">
                  {isPortuguese ? "Máximo de Tokens" : "Max Tokens"}
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
                />
                <p className="text-xs text-muted-foreground">
                  {isPortuguese
                    ? "Limite máximo de tokens para geração"
                    : "Maximum token limit for generation"}
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="base-url">
                  {isPortuguese ? "URL Base (Opcional)" : "Base URL (Optional)"}
                </Label>
                <Input
                  id="base-url"
                  value={editingProvider.baseUrl || ""}
                  onChange={(e) =>
                    setEditingProvider({ ...editingProvider, baseUrl: e.target.value })
                  }
                  placeholder="https://api.example.com/v1"
                />
                <p className="text-xs text-muted-foreground">
                  {isPortuguese
                    ? "Para APIs customizadas ou auto-hospedadas"
                    : "For custom or self-hosted APIs"}
                </p>
              </div>
            </TabsContent>

            {/* Test Tab */}
            <TabsContent value="test" className="space-y-4 mt-4">
              <Alert>
                <AlertDescription>
                  {isPortuguese
                    ? "Teste a conexão com o provedor de IA para verificar se a chave de API está válida."
                    : "Test the connection to the AI provider to verify your API key is valid."}
                </AlertDescription>
              </Alert>

              <Button
                onClick={handleTestConnection}
                disabled={testing || !editingProvider.apiKey}
                className="w-full gap-2"
              >
                <span>🧪</span>
                {testing
                  ? isPortuguese
                    ? "Testando..."
                    : "Testing..."
                  : isPortuguese
                  ? "Testar Conexão"
                  : "Test Connection"}
              </Button>

              {testResult && (
                <Alert
                  className={
                    testResult.success
                      ? "bg-green-50 border-green-200 text-green-800"
                      : "bg-red-50 border-red-200 text-red-800"
                  }
                >
                  <AlertDescription className="flex items-center gap-2">
                    {testResult.success ? <span>✓</span> : <span>✗</span>}
                    {testResult.message}
                  </AlertDescription>
                </Alert>
              )}
            </TabsContent>
          </Tabs>

          <div className="flex gap-3 justify-end pt-4 border-t">
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
              {isPortuguese ? "Cancelar" : "Cancel"}
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving
                ? isPortuguese
                  ? "Salvando..."
                  : "Saving..."
                : isPortuguese
                ? "Salvar"
                : "Save"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
