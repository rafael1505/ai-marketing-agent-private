"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  Check,
  X
} from "lucide-react";
import { AIProviderConfig } from "@/types";
import { InlineEditableProviderCard } from "./InlineEditableProviderCard";
import { getUserAIProviders, saveAIProvider } from "@/services/ai-providers";

interface ProviderMasterviewProps {
  className?: string;
}

export const ProviderMasterview: React.FC<ProviderMasterviewProps> = ({ className }) => {
  const [providers, setProviders] = useState<AIProviderConfig[]>([]);
  const [filteredProviders, setFilteredProviders] = useState<AIProviderConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [tierFilter, setTierFilter] = useState<'all' | 'free' | 'freemium' | 'paid'>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'configured' | 'unconfigured' | 'active'>('all');
  const [showStats, setShowStats] = useState(true);

  useEffect(() => {
    loadProviders();
  }, []);

  useEffect(() => {
    filterProviders();
  }, [providers, searchTerm, tierFilter, statusFilter]);

    const loadProviders = async () => {
    try {
      setLoading(true);
      const userProviders = await getUserAIProviders();
      
      if (userProviders && userProviders.length > 0) {
        setProviders(userProviders);
        setError('');
        console.log(`Loaded ${userProviders.length} providers from backend:`, userProviders.map(p => p.name));
      } else {
        setProviders([]);
        setError('No AI providers available from backend');
        console.error('Backend returned empty provider list');
      }
    } catch (error) {
      console.error('Failed to load providers:', error);
      setError(`Failed to load AI providers: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setProviders([]);
    } finally {
      setLoading(false);
    }
  };

  const filterProviders = () => {
    let filtered = [...providers];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(provider => 
        provider.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        provider.id.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Tier filter
    if (tierFilter !== 'all') {
      filtered = filtered.filter(provider => provider.pricing?.tier === tierFilter);
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(provider => {
        switch (statusFilter) {
          case 'configured':
            return provider.isConfigured;
          case 'unconfigured':
            return !provider.isConfigured;
          case 'active':
            return provider.isActive;
          default:
            return true;
        }
      });
    }

    setFilteredProviders(filtered);
  };

  const handleProviderUpdate = (updatedProvider: AIProviderConfig) => {
    setProviders(prev => prev.map(p => p.id === updatedProvider.id ? updatedProvider : p));
  };

  const handleAddProvider = async () => {
    // For now, we'll add a generic template that the user can customize
    const newProvider: AIProviderConfig = {
      id: `custom-provider-${Date.now()}`,
      name: "New Provider",
      apiKey: "",
      isConfigured: false,
      isActive: false,
      modelOptions: [],
      selectedModel: "",
      maxTokens: 1000,
      temperature: 0.7,
      pricing: {
        tier: 'paid',
        websiteUrl: ''
      }
    };

    try {
      await saveAIProvider(newProvider);
      setProviders(prev => [...prev, newProvider]);
    } catch (error) {
      console.error("Error adding provider:", error);
      // Add locally for now if API fails
      setProviders(prev => [...prev, newProvider]);
    }
  };

  const getStats = () => {
    const total = providers.length;
    const configured = providers.filter(p => p.isConfigured).length;
    const active = providers.filter(p => p.isActive).length;
    const free = providers.filter(p => p.pricing?.tier === 'free').length;
    
    return { total, configured, active, free };
  };

  const stats = getStats();

      if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <span className="w-8 h-8 animate-spin text-blue-500 text-2xl">⏳</span>
        <span className="ml-2 text-lg">Loading providers...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <span className="w-16 h-16 text-red-500 text-4xl mb-4">⚠️</span>
        <h3 className="text-lg font-semibold mb-2 text-red-600">Error Loading Providers</h3>
        <p className="text-muted-foreground mb-4 max-w-md">{error}</p>
        <Button onClick={loadProviders} className="flex items-center gap-2">
          <span>🔄</span>
          Retry
        </Button>
      </div>
    );
  }  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with Quick Stats */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">AI Providers</h2>
          <p className="text-muted-foreground">
            Manage your AI provider configurations for marketing content generation
          </p>
        </div>
        <Button onClick={handleAddProvider} className="flex items-center gap-2">
          <span>➕</span>
          Add Provider
        </Button>
      </div>

      {/* Quick Stats Dashboard */}
      {showStats && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Providers</CardTitle>
              <span className="h-4 w-4 text-muted-foreground">⚡</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
              <p className="text-xs text-muted-foreground">
                Available in your workspace
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Configured</CardTitle>
              <span className="h-4 w-4 text-green-500">✅</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.configured}</div>
              <p className="text-xs text-muted-foreground">
                Ready to use ({Math.round((stats.configured / stats.total) * 100)}%)
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active</CardTitle>
              <span className="h-4 w-4 text-blue-500">🔵</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.active}</div>
              <p className="text-xs text-muted-foreground">
                Currently enabled
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Free Providers</CardTitle>
              <span className="h-4 w-4 text-purple-500">💰</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{stats.free}</div>
              <p className="text-xs text-muted-foreground">
                No cost options
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Filter & Search</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4">🔍</span>
                <Input
                  placeholder="Search providers..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Tier Filter */}
            <Select value={tierFilter} onValueChange={(value: any) => setTierFilter(value)}>
              <SelectTrigger className="w-full sm:w-[140px]">
                <SelectValue placeholder="Pricing" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Tiers</SelectItem>
                <SelectItem value="free">Free</SelectItem>
                <SelectItem value="freemium">Freemium</SelectItem>
                <SelectItem value="paid">Paid</SelectItem>
              </SelectContent>
            </Select>

            {/* Status Filter */}
            <Select value={statusFilter} onValueChange={(value: any) => setStatusFilter(value)}>
              <SelectTrigger className="w-full sm:w-[140px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="configured">Configured</SelectItem>
                <SelectItem value="unconfigured">Setup Needed</SelectItem>
                <SelectItem value="active">Active</SelectItem>
              </SelectContent>
            </Select>

            {/* Refresh Button */}
            <Button
              variant="outline"
              onClick={loadProviders}
              className="flex items-center gap-2"
            >
              <span className="w-4 h-4">🔄</span>
              Refresh
            </Button>
          </div>

          {/* Filter Summary */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span className="w-4 h-4">🔍</span>
            <span>
              Showing {filteredProviders.length} of {providers.length} providers
            </span>
            {(searchTerm || tierFilter !== 'all' || statusFilter !== 'all') && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearchTerm('');
                  setTierFilter('all');
                  setStatusFilter('all');
                }}
                className="h-auto p-1 text-blue-600 hover:text-blue-700"
              >
                Clear filters
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Provider Grid */}
      {filteredProviders.length === 0 ? (
        <Card className="p-12 text-center">
          <span className="w-12 h-12 text-gray-400 mx-auto mb-4 block text-4xl">❌</span>
          <h3 className="text-lg font-semibold mb-2">No providers found</h3>
          <p className="text-muted-foreground mb-4">
            {searchTerm || tierFilter !== 'all' || statusFilter !== 'all'
              ? "Try adjusting your filters or search terms"
              : "Get started by adding your first AI provider"
            }
          </p>
          {!(searchTerm || tierFilter !== 'all' || statusFilter !== 'all') && (
            <Button onClick={handleAddProvider} className="flex items-center gap-2 mx-auto">
              <span>➕</span>
              Add Your First Provider
            </Button>
          )}
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-2">
          {filteredProviders.map((provider) => (
            <InlineEditableProviderCard
              key={provider.id}
              provider={provider}
              onUpdate={handleProviderUpdate}
              onDelete={(id) => setProviders(prev => prev.filter(p => p.id !== id))}
            />
          ))}
        </div>
      )}

      {/* Quick Actions Footer */}
      {filteredProviders.length > 0 && (
        <Card className="bg-muted/30">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="w-5 h-5 text-muted-foreground">📊</span>
                <div>
                  <p className="font-medium">Provider Health</p>
                  <p className="text-sm text-muted-foreground">
                    {stats.configured} configured • {stats.active} active • {stats.total - stats.configured} need setup
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  Export Config
                </Button>
                <Button variant="outline" size="sm">
                  Test All
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};