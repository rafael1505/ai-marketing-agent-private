"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AIProviderConfig, ConnectionInfo, APIStatus } from "@/types";
import { getUserAIProviders } from "@/services/ai-providers";
import { DEFAULT_AI_PROVIDERS } from "@/constants";
import { AIProviderDialog } from "@/components/dialogs/ai-provider-dialog";

export default function SettingsPage({
  params
}: {
  params: { locale: string }
}) {
  const [providers, setProviders] = useState<AIProviderConfig[]>([]);
  const [filteredProviders, setFilteredProviders] = useState<AIProviderConfig[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<AIProviderConfig | null>(null);
  const [isProviderDialogOpen, setIsProviderDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const [filterTier, setFilterTier] = useState<'all' | 'free' | 'freemium' | 'paid'>('all');
  const [apiConnectionStatus, setApiConnectionStatus] = useState<APIStatus>({
    status: 'disconnected',
    statusText: 'Disconnected',
    statusColor: '#dc3545',
    message: 'API connection not established'
  });
  const [companyInfo, setCompanyInfo] = useState({
    name: "Example Company",
    description: "A leading technology company",
    logo: "",
    logo_file: null as File | null,
    brandColors: ["#3B82F6", "#1E40AF", "#93C5FD"]
  });

  // Fix hydration error
  useEffect(() => {
    setMounted(true);
    loadProviders();
    checkApiConnection();
  }, []);

  // Filter providers when filter changes
  useEffect(() => {
    if (filterTier === 'all') {
      setFilteredProviders(providers);
    } else {
      setFilteredProviders(providers.filter(provider => provider.pricing.tier === filterTier));
    }
  }, [providers, filterTier]);

  const loadProviders = async () => {
    try {
      setLoading(true);
      const userProviders = await getUserAIProviders();
      setProviders(userProviders.length > 0 ? userProviders : DEFAULT_AI_PROVIDERS);
    } catch (error) {
      console.error("Error loading providers:", error);
      setProviders(DEFAULT_AI_PROVIDERS);
    } finally {
      setLoading(false);
    }
  };

  const checkApiConnection = async () => {
    try {
      const response = await fetch('/api/auth/verify');
      if (response.ok) {
        setApiConnectionStatus({
          status: 'connected',
          statusText: 'Connected',
          statusColor: '#28a745',
          message: 'API connection established successfully'
        });
      } else {
        setApiConnectionStatus({
          status: 'auth-issue',
          statusText: 'Authentication Issue',
          statusColor: '#ffc107',
          message: 'API accessible but authentication failed'
        });
      }
    } catch (error) {
      setApiConnectionStatus({
        status: 'offline',
        statusText: 'Offline',
        statusColor: '#dc3545',
        message: 'Unable to reach API server'
      });
    }
  };

  const handleCompanySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Company info saved:", companyInfo);
    alert("Company information saved successfully!");
  };

  const handleColorChange = (index: number, color: string) => {
    const newColors = [...companyInfo.brandColors];
    newColors[index] = color;
    setCompanyInfo({ ...companyInfo, brandColors: newColors });
  };

  const addBrandColor = () => {
    if (companyInfo.brandColors.length < 8) {
      setCompanyInfo({ 
        ...companyInfo, 
        brandColors: [...companyInfo.brandColors, "#000000"] 
      });
    }
  };

  const removeBrandColor = (index: number) => {
    if (companyInfo.brandColors.length > 1) {
      const newColors = companyInfo.brandColors.filter((_, i) => i !== index);
      setCompanyInfo({ ...companyInfo, brandColors: newColors });
    }
  };

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Create a local URL for preview
      const logoUrl = URL.createObjectURL(file);
      setCompanyInfo({ 
        ...companyInfo, 
        logo: logoUrl,
        logo_file: file 
      });
    }
  };

  const removeLogo = () => {
    if (companyInfo.logo && companyInfo.logo.startsWith('blob:')) {
      URL.revokeObjectURL(companyInfo.logo);
    }
    setCompanyInfo({ 
      ...companyInfo, 
      logo: "",
      logo_file: null 
    });
  };

  const handleAddProvider = () => {
    setSelectedProvider(null);
    setIsProviderDialogOpen(true);
  };

  const handleEditProvider = (provider: AIProviderConfig) => {
    setSelectedProvider(provider);
    setIsProviderDialogOpen(true);
  };

  const handleSaveProvider = async (provider: AIProviderConfig) => {
    try {
      // Update the providers list
      const updatedProviders = providers.map(p => 
        p.id === provider.id ? provider : p
      );
      
      // If it's a new provider, add it
      if (!providers.find(p => p.id === provider.id)) {
        updatedProviders.push(provider);
      }
      
      setProviders(updatedProviders);
      setIsProviderDialogOpen(false);
    } catch (error) {
      console.error("Error saving provider:", error);
    }
  };

  const getPricingBadgeColor = (tier: string) => {
    switch (tier) {
      case 'free': return 'bg-green-100 text-green-800';
      case 'freemium': return 'bg-blue-100 text-blue-800';
      case 'paid': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatPricing = (provider: AIProviderConfig) => {
    const { pricing } = provider;
    if (pricing.tier === 'free') {
      return pricing.freeQuota?.description || 'Free';
    }
    if (pricing.tier === 'freemium' && pricing.freeQuota) {
      const quota = pricing.freeQuota;
      if (quota.requestsPerMonth) {
        return `${quota.requestsPerMonth.toLocaleString()} requests/month free`;
      }
      return quota.description || 'Free tier available';
    }
    if (pricing.paidPlans && pricing.paidPlans.length > 0) {
      const plan = pricing.paidPlans[0];
      if (plan.monthlyFee) {
        return `From $${plan.monthlyFee}/month`;
      }
      if (plan.pricePerToken) {
        return `$${plan.pricePerToken}/token`;
      }
    }
    return 'Contact for pricing';
  };
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <h1 className="text-3xl font-bold mb-8">Settings</h1>
      
      <div className="grid gap-8 lg:grid-cols-2">
        {/* Left Column */}
        <div className="space-y-6">
          {/* Company Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                ⚙️ Company Settings
              </CardTitle>
              <CardDescription>
                Manage your company information and branding
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCompanySubmit} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="companyName">Company Name</Label>
                  <Input
                    id="companyName"
                    value={companyInfo.name}
                    onChange={(e) => setCompanyInfo({ ...companyInfo, name: e.target.value })}
                    placeholder="Enter your company name"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="companyDescription">Company Description</Label>
                  <textarea
                    id="companyDescription"
                    value={companyInfo.description}
                    onChange={(e) => setCompanyInfo({ ...companyInfo, description: e.target.value })}
                    placeholder="Describe your company..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    rows={3}
                  />
                </div>

                {/* Logo Upload Section */}
                <div className="space-y-3">
                  <Label>Company Logo</Label>
                  <div className="flex items-start gap-4">
                    {/* Logo Preview */}
                    <div className="flex-shrink-0">
                      {companyInfo.logo ? (
                        <div className="relative group">
                          <img
                            src={companyInfo.logo}
                            alt="Company Logo"
                            className="w-24 h-24 object-contain border-2 border-gray-200 rounded-lg bg-white p-2"
                          />
                          <button
                            type="button"
                            onClick={removeLogo}
                            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-red-600 transition-colors"
                          >
                            ×
                          </button>
                        </div>
                      ) : (
                        <div className="w-24 h-24 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center text-gray-400 bg-gray-50">
                          <span className="text-xs text-center">No Logo</span>
                        </div>
                      )}
                    </div>
                    
                    {/* Upload Controls */}
                    <div className="flex-1 space-y-2">
                      <div className="flex gap-2">
                        <input
                          type="file"
                          id="logoUpload"
                          accept="image/*"
                          onChange={handleLogoChange}
                          className="hidden"
                        />
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => document.getElementById('logoUpload')?.click()}
                        >
                          {companyInfo.logo ? 'Change Logo' : 'Upload Logo'}
                        </Button>
                        {companyInfo.logo && (
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={removeLogo}
                          >
                            Remove
                          </Button>
                        )}
                      </div>
                      <p className="text-xs text-gray-500">
                        Recommended: PNG or JPG, max 2MB, 200x200px optimal
                      </p>
                    </div>
                  </div>
                </div>

                {/* Enhanced Brand Colors Section */}
                <div className="space-y-3">
                  <Label>Brand Colors</Label>
                  <div className="space-y-3">
                    <div className="grid grid-cols-4 gap-3">
                      {companyInfo.brandColors.map((color, index) => (
                        <div key={index} className="space-y-2">
                          <div className="relative group">
                            <div 
                              className="w-full h-12 rounded-lg border-2 border-gray-200 cursor-pointer relative overflow-hidden shadow-sm hover:shadow-md transition-shadow"
                              style={{ backgroundColor: color }}
                              onClick={() => document.getElementById(`color-${index}`)?.click()}
                            >
                              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all duration-200 flex items-center justify-center">
                                <span className="text-white text-xs opacity-0 group-hover:opacity-100 transition-opacity">
                                  Click to change
                                </span>
                              </div>
                            </div>
                            <input
                              id={`color-${index}`}
                              type="color"
                              value={color}
                              onChange={(e) => handleColorChange(index, e.target.value)}
                              className="sr-only"
                            />
                            <button
                              type="button"
                              onClick={() => removeBrandColor(index)}
                              disabled={companyInfo.brandColors.length <= 1}
                              className={`absolute -top-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center text-xs transition-all ${
                                companyInfo.brandColors.length > 1 
                                  ? 'bg-red-500 text-white hover:bg-red-600 cursor-pointer' 
                                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                              }`}
                            >
                              ×
                            </button>
                          </div>
                          <div className="text-center">
                            <code className="text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded">
                              {color.toUpperCase()}
                            </code>
                          </div>
                        </div>
                      ))}
                      {companyInfo.brandColors.length < 8 && (
                        <div className="space-y-2">
                          <button
                            type="button"
                            onClick={addBrandColor}
                            className="w-full h-12 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all duration-200 flex items-center justify-center text-gray-500 hover:text-blue-600"
                          >
                            <span className="text-2xl">+</span>
                          </button>
                          <div className="text-center">
                            <span className="text-xs text-gray-400">Add Color</span>
                          </div>
                        </div>
                      )}
                    </div>
                    <p className="text-xs text-gray-500">
                      Click on colors to change them. You can have up to 8 brand colors.
                    </p>
                  </div>
                </div>
                
                <Button type="submit" className="w-full">
                  💾 Save Company Settings
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* API Diagnostics */}
          <Card>
            <CardHeader>
              <CardTitle>API Diagnostics</CardTitle>
              <CardDescription>
                Monitor API connection status and troubleshoot issues
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: apiConnectionStatus.statusColor }}
                  />
                  <span className="font-medium">
                    API Status: {apiConnectionStatus.statusText}
                  </span>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                  <div><strong>API URL:</strong> http://127.0.0.1:8088</div>
                  <div><strong>Last Updated:</strong> {mounted ? new Date().toLocaleString() : 'Loading...'}</div>
                  <div><strong>Response Time:</strong> ~50ms</div>
                </div>
                
                <Button 
                  onClick={() => window.open('/api-connection-test.html', '_blank')}
                  className="w-full"
                  variant="outline"
                >
                  Test API Connection
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* AI Providers */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    ⚡ AI Providers
                  </CardTitle>
                  <CardDescription>
                    Configure your AI providers for marketing content generation
                  </CardDescription>
                </div>
                <Button
                  onClick={handleAddProvider}
                  size="sm"
                  className="flex items-center gap-2"
                >
                  + Add Provider
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-4">Loading providers...</div>
              ) : (
                <>
                  {/* Filter Buttons */}
                  <div className="flex gap-2 mb-6">
                    <Button
                      variant={filterTier === 'all' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setFilterTier('all')}
                    >
                      All ({providers.length})
                    </Button>
                    <Button
                      variant={filterTier === 'free' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setFilterTier('free')}
                      className="flex items-center gap-1"
                    >
                      Free ({providers.filter(p => p.pricing.tier === 'free').length})
                    </Button>
                    <Button
                      variant={filterTier === 'freemium' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setFilterTier('freemium')}
                    >
                      Freemium ({providers.filter(p => p.pricing.tier === 'freemium').length})
                    </Button>
                    <Button
                      variant={filterTier === 'paid' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setFilterTier('paid')}
                    >
                      Paid ({providers.filter(p => p.pricing.tier === 'paid').length})
                    </Button>
                  </div>

                  {/* Provider Cards */}
                  <div className="space-y-4">
                    {filteredProviders.map((provider) => (
                      <Card 
                        key={provider.id} 
                        className={`cursor-pointer transition-all hover:shadow-md ${provider.isConfigured ? 'ring-2 ring-green-200' : ''}`}
                        onClick={() => handleEditProvider(provider)}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex items-start gap-3">
                              {provider.logo && (
                                <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                                  <img src={provider.logo} alt={provider.name} className="w-6 h-6" />
                                </div>
                              )}
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <h3 className="font-medium">{provider.name}</h3>
                                  <Badge 
                                    variant="secondary"
                                    className={getPricingBadgeColor(provider.pricing.tier)}
                                  >
                                    {provider.pricing.tier.charAt(0).toUpperCase() + provider.pricing.tier.slice(1)}
                                  </Badge>
                                  {provider.isConfigured && (
                                    <Badge className="bg-green-100 text-green-800">
                                      ✓ Configured
                                    </Badge>
                                  )}
                                </div>
                                
                                <p className="text-sm text-gray-600 mb-2">
                                  {formatPricing(provider)}
                                </p>
                                
                                {provider.pricing.freeQuota?.description && (
                                  <p className="text-xs text-gray-500">
                                    {provider.pricing.freeQuota.description}
                                  </p>
                                )}
                              </div>
                            </div>
                            
                            <div className="flex items-center gap-2">
                              {provider.pricing.websiteUrl && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    window.open(provider.pricing.websiteUrl, '_blank');
                                  }}
                                >
                                  💰
                                </Button>
                              )}
                              <div className={`w-3 h-3 rounded-full ${provider.isActive ? 'bg-green-500' : 'bg-gray-300'}`} />
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* AI Provider Dialog */}
      <AIProviderDialog
        provider={selectedProvider}
        isOpen={isProviderDialogOpen}
        onClose={() => setIsProviderDialogOpen(false)}
        onSave={handleSaveProvider}
        translations={{}} // Add translations as needed
      />
    </div>
  );
}
