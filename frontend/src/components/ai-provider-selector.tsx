"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Check, X } from "lucide-react";
import { AIProviderConfig, ConfigurationStep } from "@/types";
import { AIProviderValidator, ProviderValidationResult } from "@/services/ai-provider-validator";
import { MARKETING_AI_PROVIDERS, getProvidersByCapability, getConfiguredProviders } from "@/constants/marketing-ai-providers";

interface AIProviderSelectorProps {
  selectedProvider: string;
  onProviderSelect: (providerId: string) => void;
  requiredCapability?: keyof NonNullable<AIProviderConfig['marketingCapabilities']>;
  className?: string;
}

export const AIProviderSelector: React.FC<AIProviderSelectorProps> = ({
  selectedProvider,
  onProviderSelect,
  requiredCapability = 'imageGeneration',
  className
}) => {
  const [providers, setProviders] = useState<AIProviderConfig[]>([]);
  const [validationResults, setValidationResults] = useState<Map<string, ProviderValidationResult>>(new Map());
  const [isValidating, setIsValidating] = useState(false);
  const [showConfigDialog, setShowConfigDialog] = useState(false);
  const [selectedProviderForConfig, setSelectedProviderForConfig] = useState<AIProviderConfig | null>(null);

  useEffect(() => {
    // Filter providers by required capability
    const filteredProviders = requiredCapability 
      ? getProvidersByCapability(requiredCapability)
      : MARKETING_AI_PROVIDERS;
    
    setProviders(filteredProviders);
    validateProviders(filteredProviders);
  }, [requiredCapability]);

  const validateProviders = async (providersToValidate: AIProviderConfig[]) => {
    setIsValidating(true);
    const results = new Map();
    
    for (const provider of providersToValidate) {
      try {
        const result = await AIProviderValidator.validateProvider(provider);
        results.set(provider.id, result);
      } catch (error) {
        console.error(`Error validating provider ${provider.id}:`, error);
      }
    }
    
    setValidationResults(results);
    setIsValidating(false);
  };

  const getProviderIcon = (provider: AIProviderConfig) => {
    const tier = provider.pricing?.tier || 'free';
    switch (tier) {
      case 'free':
        return <span className="text-green-500">✓</span>;
      case 'freemium':
        return <span className="text-blue-500">⚡</span>;
      case 'paid':
        return <span className="text-purple-500">★</span>;
      default:
        return null;
    }
  };

  const getStatusBadge = (provider: AIProviderConfig, validation?: ProviderValidationResult) => {
    if (!validation) {
      return <Badge variant="secondary">Checking...</Badge>;
    }

    switch (validation.status) {
      case 'configured':
        return <Badge variant="default" className="bg-green-500">Ready</Badge>;
      case 'partial':
        return <Badge variant="secondary" className="bg-yellow-500">Partial</Badge>;
      case 'not_configured':
        return <Badge variant="destructive">Setup Required</Badge>;
      case 'error':
        return <Badge variant="destructive">Error</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  const openConfigurationDialog = (provider: AIProviderConfig) => {
    setSelectedProviderForConfig(provider);
    setShowConfigDialog(true);
  };

  const ConfigurationDialog = () => {
    if (!selectedProviderForConfig) return null;

    const validation = validationResults.get(selectedProviderForConfig.id);
    const guidance = AIProviderValidator.getConfigurationGuidance(selectedProviderForConfig);

    return (
      <Dialog open={showConfigDialog} onOpenChange={setShowConfigDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {getProviderIcon(selectedProviderForConfig)}
              Configure {selectedProviderForConfig.name}
            </DialogTitle>
            <DialogDescription>
              {guidance.description}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Configuration Progress */}
            {selectedProviderForConfig.configurationSteps && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">Setup Progress</h4>
                  <span className="text-sm text-muted-foreground">
                    {guidance.estimatedTime} • {guidance.difficulty} setup
                  </span>
                </div>
                
                <div className="space-y-3">
                  {selectedProviderForConfig.configurationSteps.map((step, index) => (
                    <div key={step.id} className="flex items-start gap-3">
                      <div className={`flex items-center justify-center w-6 h-6 rounded-full text-xs font-medium ${
                        step.isCompleted 
                          ? 'bg-green-500 text-white' 
                          : index === 0 
                            ? 'bg-blue-500 text-white' 
                            : 'bg-gray-200 text-gray-600'
                      }`}>
                        {step.isCompleted ? '✓' : index + 1}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h5 className="font-medium">{step.title}</h5>
                          {step.isRequired && <Badge variant="secondary" className="text-xs">Required</Badge>}
                        </div>
                        <p className="text-sm text-muted-foreground">{step.description}</p>
                        {step.helpUrl && (
                          <Button variant="link" size="sm" className="p-0 h-auto" asChild>
                            <a href={step.helpUrl} target="_blank" rel="noopener noreferrer">
                              View Guide <span className="ml-1">→</span>
                            </a>
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Validation Errors/Warnings */}
            {validation && (validation.errors.length > 0 || validation.warnings.length > 0) && (
              <div className="space-y-3">
                {validation.errors.length > 0 && (
                  <Alert variant="destructive">
                    <span className="text-red-500">⚠</span>
                    <AlertTitle>Configuration Issues</AlertTitle>
                    <AlertDescription>
                      <ul className="list-disc list-inside space-y-1">
                        {validation.errors.map((error, index) => (
                          <li key={index}>{error}</li>
                        ))}
                      </ul>
                    </AlertDescription>
                  </Alert>
                )}

                {validation.warnings.length > 0 && (
                  <Alert>
                    <span className="text-yellow-500">⚠</span>
                    <AlertTitle>Recommendations</AlertTitle>
                    <AlertDescription>
                      <ul className="list-disc list-inside space-y-1">
                        {validation.warnings.map((warning, index) => (
                          <li key={index}>{warning}</li>
                        ))}
                      </ul>
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            )}

            {/* Pricing Information */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <span className="text-green-500">$</span>
                  Pricing
                </CardTitle>
              </CardHeader>
              <CardContent>
                {selectedProviderForConfig.pricing?.freeQuota && (
                  <div className="mb-4 p-3 bg-green-50 rounded-lg">
                    <h5 className="font-medium text-green-800">Free Tier</h5>
                    <p className="text-sm text-green-700">{selectedProviderForConfig.pricing?.freeQuota?.description}</p>
                  </div>
                )}
                
                {selectedProviderForConfig.pricing?.paidPlans && selectedProviderForConfig.pricing?.paidPlans?.length > 0 && (
                  <div className="space-y-2">
                    <h5 className="font-medium">Paid Plans</h5>
                    {selectedProviderForConfig.pricing?.paidPlans?.map((plan, index) => (
                      <div key={index} className="flex justify-between items-center p-2 border rounded">
                        <div>
                          <span className="font-medium">{plan.name}</span>
                          <p className="text-sm text-muted-foreground">{plan.description}</p>
                        </div>
                        <div className="text-right">
                          {plan.monthlyFee && <span className="font-bold">${plan.monthlyFee}/mo</span>}
                          {plan.pricePerImage && <span className="font-bold">${plan.pricePerImage}/image</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <Button 
                onClick={() => setShowConfigDialog(false)}
                variant="outline"
                className="flex-1"
              >
                Close
              </Button>
              {selectedProviderForConfig.pricing?.websiteUrl && (
                <Button asChild className="flex-1">
                  <a href={selectedProviderForConfig.pricing?.websiteUrl} target="_blank" rel="noopener noreferrer">
                    Get Started <span className="ml-2">→</span>
                  </a>
                </Button>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  };

  return (
    <div className={className}>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {providers.map((provider) => {
          const validation = validationResults.get(provider.id);
          const isSelected = selectedProvider === provider.id;
          const canGenerate = validation?.isValid || false;

          return (
            <Card 
              key={provider.id} 
              className={`cursor-pointer transition-all duration-200 ${
                isSelected 
                  ? 'ring-2 ring-blue-500 border-blue-500' 
                  : 'hover:shadow-md'
              } ${
                !canGenerate ? 'opacity-75' : ''
              }`}
              onClick={() => canGenerate && onProviderSelect(provider.id)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getProviderIcon(provider)}
                    <CardTitle className="text-lg">{provider.name}</CardTitle>
                  </div>
                  {getStatusBadge(provider, validation)}
                </div>
                
                {/* Capabilities */}
                <div className="flex flex-wrap gap-1">
                  {provider.supportedFeatures?.slice(0, 3).map((feature) => (
                    <Badge key={feature} variant="outline" className="text-xs">
                      {feature.replace('_', ' ')}
                    </Badge>
                  ))}
                  {provider.supportedFeatures && provider.supportedFeatures.length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{provider.supportedFeatures.length - 3} more
                    </Badge>
                  )}
                </div>
              </CardHeader>

              <CardContent className="pt-0">
                {/* Pricing Tier */}
                <div className="mb-3">
                  <Badge 
                    variant={provider.pricing?.tier === 'free' ? 'default' : 'secondary'}
                    className="capitalize"
                  >
                    {provider.pricing?.tier || 'free'}
                  </Badge>
                  {provider.pricing?.freeQuota && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {provider.pricing?.freeQuota?.description}
                    </p>
                  )}
                </div>

                {/* Configuration Status */}
                {validation && !validation.isValid && (
                  <Alert className="mb-3">
                    <span className="text-gray-500">⚙</span>
                    <AlertDescription className="text-sm">
                      {validation.nextAction?.description || 'Configuration required'}
                    </AlertDescription>
                  </Alert>
                )}

                {/* Action Buttons */}
                <div className="flex gap-2">
                  {canGenerate ? (
                    <Button 
                      variant={isSelected ? "default" : "outline"}
                      size="sm"
                      className="flex-1"
                      onClick={(e) => {
                        e.stopPropagation();
                        onProviderSelect(provider.id);
                      }}
                    >
                      {isSelected ? 'Selected' : 'Select'}
                    </Button>
                  ) : (
                    <Button 
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={(e) => {
                        e.stopPropagation();
                        openConfigurationDialog(provider);
                      }}
                    >
                      <span className="text-gray-500 mr-1">⚙</span>
                      Setup
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-6 p-4 bg-muted rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium">AI Providers Status</h4>
            <p className="text-sm text-muted-foreground">
              {getConfiguredProviders().length} of {providers.length} providers configured
            </p>
          </div>
          {isValidating && (
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
              <span className="text-sm">Validating...</span>
            </div>
          )}
        </div>
      </div>

      <ConfigurationDialog />
    </div>
  );
};
