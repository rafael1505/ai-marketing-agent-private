"use client";

import React from "react";
import Image from "next/image";
import { getTranslations } from "@/i18n";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { RefinementFormData, AIProviderConfig, GeneratedImage } from "@/types";
import { Loader } from "@/components/ui/loader";
import { MARKETING_AI_PROVIDERS, getConfiguredProviders } from "@/constants/marketing-ai-providers";

interface RefinementFormProps {
  onSubmit: (data: RefinementFormData) => void;
  onGenerateImage: (prompt: string, provider: string) => Promise<void>;
  aiProviders: AIProviderConfig[];
  generatedImages: GeneratedImage[];
  initialData?: Partial<RefinementFormData>;
  locale?: string;
}

export const EnhancedRefinementForm: React.FC<RefinementFormProps> = ({
  onSubmit,
  onGenerateImage,
  aiProviders,
  generatedImages,
  initialData = {},
  locale = "en"
}) => {
  const [t, setT] = React.useState<Record<string, any>>({});
  const [formData, setFormData] = React.useState<RefinementFormData>({
    prompt: initialData.prompt || "Create a professional marketing image for a modern tech product, featuring sleek design elements and vibrant colors",
    aiProvider: initialData.aiProvider || "",
    generationParams: initialData.generationParams || {},
  });
  
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [selectedProvider, setSelectedProvider] = React.useState<AIProviderConfig | null>(null);
  const [providerError, setProviderError] = React.useState<string>("");

  React.useEffect(() => {
    const loadTranslations = async () => {
      try {
        const translations = await getTranslations(locale === "pt" ? "pt" : "en");
        setT(translations);
      } catch (error) {
        console.error("Error loading translations:", error);
        setT({
          creation: {
            refinement: {
              title: "Content Refinement & Image Generation",
              description: "Generate professional marketing images using AI",
              form: {
                prompt: "Image Description",
                prompt_placeholder: "Describe the marketing image you want to create",
                ai_provider: "AI Provider",
                select_provider: "Select an AI Provider",
                generate_image: "Generate Image",
                generating: "Generating...",
                generated_images: "Generated Images",
                save: "Continue to Finalization",
                saving: "Saving...",
                no_providers: "No AI providers configured",
                configure_providers: "Configure AI Providers"
              }
            }
          }
        });
      }
    };
    loadTranslations();
  }, [locale]);

  // Update form data when provider changes
  React.useEffect(() => {
    if (selectedProvider) {
      setFormData(prev => ({ ...prev, aiProvider: selectedProvider.id }));
      setProviderError("");
    }
  }, [selectedProvider]);

  const configuredProviders = React.useMemo(() => {
    return MARKETING_AI_PROVIDERS.filter(provider => 
      provider.configurationStatus === 'configured' || 
      provider.pricing?.tier === 'free' ||
      provider.isConfigured === true ||
      provider.id === 'dalle3' // Always include DALL-E for demo
    );
  }, []);

  // Auto-select the free provider if no provider is selected
  React.useEffect(() => {
    if (configuredProviders.length > 0 && !selectedProvider) {
      // Prefer the free provider
      const freeProvider = configuredProviders.find(p => 
        p.pricing?.tier === 'free' || p.id === 'free-test-provider'
      );
      const defaultProvider = freeProvider || configuredProviders[0];
      setSelectedProvider(defaultProvider);
    }
  }, [configuredProviders, selectedProvider]);

  const handleProviderSelect = (providerId: string) => {
    const provider = MARKETING_AI_PROVIDERS.find(p => p.id === providerId);
    if (provider) {
      setSelectedProvider(provider);
      setProviderError("");
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Enhanced refinement form submitted with data:", formData);
    setIsSubmitting(true);

    try {
      await onSubmit(formData);
    } catch (error) {
      console.error("Error submitting refinement form:", error);
      setIsSubmitting(false);
    }
  };

  const handleGenerateImage = async () => {
    if (!formData.prompt) {
      setProviderError("Please enter an image description");
      return;
    }
    
    if (!formData.aiProvider || !selectedProvider) {
      setProviderError("Please select an AI provider");
      return;
    }
    
    setIsGenerating(true);
    setProviderError("");
    
    try {
      await onGenerateImage(formData.prompt, formData.aiProvider);
    } catch (error) {
      console.error("Error generating image:", error);
      setProviderError("Failed to generate image. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  if (!t || Object.keys(t).length === 0) {
    return (
      <div className="flex justify-center items-center h-40">
        <Loader size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* AI Provider Selection */}
      <Card className="border-l-4 border-l-blue-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600">
                <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2"/>
                <path d="M14.5 4.5c-1.8.7-3 2.5-3 4.5 0 0-2 0-2 2 0 2 2 2 2 2"/>
                <path d="M14.5 4.5A4 4 0 1 1 18 9"/>
              </svg>
            </div>
            {t.creation.refinement.form.select_provider}
          </CardTitle>
          <CardDescription>
            Choose an AI provider to generate marketing images. Each provider offers different capabilities and pricing.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {configuredProviders.length === 0 ? (
            <Alert>
              <AlertDescription>
                {t.creation.refinement.form.no_providers}. Please configure at least one AI provider to continue.
              </AlertDescription>
            </Alert>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {configuredProviders.map((provider) => (
                <Card 
                  key={provider.id}
                  className={`cursor-pointer transition-all duration-200 ${
                    selectedProvider?.id === provider.id 
                      ? 'ring-2 ring-blue-500 border-blue-500' 
                      : 'hover:shadow-md'
                  }`}
                  onClick={() => handleProviderSelect(provider.id)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base">{provider.name}</CardTitle>
                      <Badge 
                        variant={provider.pricing.tier === 'free' ? 'default' : 'secondary'}
                        className="capitalize"
                      >
                        {provider.pricing.tier}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="space-y-2">
                      {provider.marketingCapabilities?.imageGeneration && (
                        <Badge variant="outline" className="text-xs">Image Generation</Badge>
                      )}
                      {provider.marketingCapabilities?.logoDesign && (
                        <Badge variant="outline" className="text-xs">Logo Design</Badge>
                      )}
                      
                      {provider.pricing.freeQuota && (
                        <p className="text-xs text-muted-foreground">
                          {provider.pricing.freeQuota.description}
                        </p>
                      )}
                    </div>
                    
                    <Button 
                      variant={selectedProvider?.id === provider.id ? "default" : "outline"}
                      size="sm"
                      className="w-full mt-3"
                    >
                      {selectedProvider?.id === provider.id ? 'Selected' : 'Select'}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Image Generation Form */}
      <Card className="shadow-lg border-t-4 border-t-accent">
        <CardHeader className="bg-gradient-to-r from-accent/5 to-primary/5">
          <div className="flex items-center space-x-2 mb-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-accent">
              <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
              <path d="M5 3v4"/>
              <path d="M19 17v4"/>
              <path d="M3 5h4"/>
              <path d="M17 19h4"/>
            </svg>
            <CardTitle className="text-xl font-semibold">{t.creation.refinement.title}</CardTitle>
          </div>
          <CardDescription>{t.creation.refinement.description}</CardDescription>
        </CardHeader>
        
        <form onSubmit={handleSubmit} className="fade-in">
          <CardContent className="space-y-6 pt-6">
            {/* Selected Provider Info */}
            {selectedProvider && (
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-blue-900">Selected: {selectedProvider.name}</h4>
                    <p className="text-sm text-blue-700">
                      {selectedProvider.marketingCapabilities?.imageGeneration ? 'Ready for image generation' : 'Limited capabilities'}
                    </p>
                  </div>
                  <Badge variant="default" className="bg-blue-500">
                    {selectedProvider.pricing.tier}
                  </Badge>
                </div>
              </div>
            )}

            {/* Prompt Input */}
            <div className="space-y-2">
              <Label htmlFor="prompt" className="text-sm font-medium">
                {t.creation.refinement.form.prompt}
              </Label>
              <Textarea
                id="prompt"
                name="prompt"
                placeholder={t.creation.refinement.form.prompt_placeholder}
                value={formData.prompt}
                onChange={handleChange}
                rows={4}
                required
                className="focus:border-accent transition-all resize-none"
              />
              <p className="text-xs text-muted-foreground">
                Be specific about style, colors, composition, and branding elements you want in your marketing image.
              </p>
            </div>

            {/* Error Display */}
            {providerError && (
              <Alert variant="destructive">
                <AlertDescription>{providerError}</AlertDescription>
              </Alert>
            )}
            
            {/* Generate Button */}
            <div className="pt-4">
              <Button
                type="button"
                onClick={handleGenerateImage}
                disabled={isGenerating || !formData.prompt || !selectedProvider}
                className="w-full btn-scale bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg hover:shadow-xl transition-all duration-200"
                size="lg"
              >
                {isGenerating ? (
                  <>
                    <Loader size="sm" color="white" className="mr-3" />
                    <span className="font-medium">{t.creation.refinement.form.generating}</span>
                  </>
                ) : (
                  <>
                    <svg 
                      xmlns="http://www.w3.org/2000/svg" 
                      width="20" 
                      height="20" 
                      viewBox="0 0 24 24" 
                      fill="none" 
                      stroke="currentColor" 
                      strokeWidth="2.5" 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      className="mr-3"
                    >
                      <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
                      <path d="M5 3v4"/>
                      <path d="M19 17v4"/>
                      <path d="M3 5h4"/>
                      <path d="M17 19h4"/>
                    </svg>
                    <span className="font-medium">{t.creation.refinement.form.generate_image}</span>
                  </>
                )}
              </Button>
            </div>

            {/* Generated Images Display */}
            {generatedImages.length > 0 && (
              <div className="space-y-3">
                <Label className="text-sm font-medium">{t.creation.refinement.form.generated_images}</Label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {generatedImages.map((image, index) => (
                    <div 
                      key={index} 
                      className="relative border rounded-md overflow-hidden hover:shadow-lg transition-shadow duration-200"
                    >
                      <Image
                        src={image.url}
                        alt={`Generated image ${index + 1}`}
                        width={300}
                        height={300}
                        className="w-full h-auto object-cover"
                      />
                      <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white p-2 text-xs">
                        <p className="font-medium">{image.ai_provider}</p>
                        <p>{image.prompt.length > 50 ? `${image.prompt.substring(0, 50)}...` : image.prompt}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
          
          <CardFooter className="flex justify-between items-center border-t pt-6">
            <div className="text-sm text-muted-foreground">
              {generatedImages.length === 0 
                ? "Generate at least one image to proceed" 
                : `${generatedImages.length} image(s) generated`
              }
            </div>
            <Button
              type="submit"
              disabled={isSubmitting || generatedImages.length === 0}
              className="btn-scale bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white shadow-lg hover:shadow-xl transition-all duration-200"
              size="lg"
            >
              {isSubmitting ? (
                <>
                  <Loader size="sm" color="white" className="mr-3" />
                  <span className="font-medium">{t.creation.refinement.form.saving}</span>
                </>
              ) : (
                <>
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    width="18" 
                    height="18" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2" 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    className="mr-3"
                  >
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                  <span className="font-medium">{t.creation.refinement.form.save}</span>
                </>
              )}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
};
