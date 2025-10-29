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
import { RefinementFormData, GeneratedImage } from "@/types";
import { Loader } from "@/components/ui/loader";

interface RefinementFormProps {
  onSubmit: (data: RefinementFormData) => void;
  onGenerateImage: (prompt: string, provider: string) => Promise<void>;
  aiProviders: any[]; // Updated to use the new AI provider format
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
  const [selectedProvider, setSelectedProvider] = React.useState<any | null>(null);
  const [providerError, setProviderError] = React.useState<string>("");
  const [selectedImageIndex, setSelectedImageIndex] = React.useState<number | null>(null);
  const [progressMessage, setProgressMessage] = React.useState<string>("");
  const [elapsedSeconds, setElapsedSeconds] = React.useState<number>(0);

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
    // Use the providers passed from parent (which are already filtered for active/configured)
    return aiProviders.length > 0 ? aiProviders : [];
  }, [aiProviders]);

  // Auto-select the first provider if no provider is selected
  React.useEffect(() => {
    if (configuredProviders.length > 0 && !selectedProvider) {
      // Select the first available provider
      const defaultProvider = configuredProviders[0];
      setSelectedProvider(defaultProvider);
    }
  }, [configuredProviders, selectedProvider]);

  // Keyboard navigation for image modal
  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (selectedImageIndex === null) return;

      switch (event.key) {
        case 'Escape':
          setSelectedImageIndex(null);
          break;
        case 'ArrowLeft':
          event.preventDefault();
          setSelectedImageIndex(
            selectedImageIndex > 0 ? selectedImageIndex - 1 : generatedImages.length - 1
          );
          break;
        case 'ArrowRight':
          event.preventDefault();
          setSelectedImageIndex(
            selectedImageIndex < generatedImages.length - 1 ? selectedImageIndex + 1 : 0
          );
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [selectedImageIndex, generatedImages.length]);

  const handleProviderSelect = (providerId: string) => {
    const provider = configuredProviders.find(p => p.id === providerId);
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
    setElapsedSeconds(0);
    setProgressMessage("");
    
    // Start progress tracking - update every 10 seconds
    const startTime = Date.now();
    const progressInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      setElapsedSeconds(elapsed);
      
      // Provider-specific time estimates
      const providerEstimates: Record<string, number> = {
        'openai': 75,      // DALL-E 3: ~75s for 3 images
        'stability': 45,   // Stability AI: ~45s for 3 images
        'replicate': 60,   // Replicate: ~60s for 3 images
        'huggingface': 90, // HuggingFace: ~90s for 3 images
      };
      const estimatedTime = providerEstimates[formData.aiProvider.toLowerCase()] || 60;
      
      if (elapsed >= 10 && elapsed < estimatedTime) {
        setProgressMessage(
          `Still generating... ${elapsed}s elapsed. ${selectedProvider.name} can take up to ${estimatedTime}s for 3 images.`
        );
      }
    }, 10000); // Update every 10 seconds
    
    try {
      console.log("Starting image generation with:", { prompt: formData.prompt, provider: formData.aiProvider });
      await onGenerateImage(formData.prompt, formData.aiProvider);
      console.log("Image generation completed successfully");
      setProgressMessage(""); // Clear progress message on success
    } catch (error) {
      console.error("Error generating image:", error);
      const errorMessage = error instanceof Error ? error.message : "Failed to generate image. Please try again.";
      setProviderError(errorMessage);
      
      // Parent component (create/edit page) handles error display with AIErrorDisplay
      // No need for browser alert() here
    } finally {
      clearInterval(progressInterval);
      setIsGenerating(false);
      setProgressMessage("");
      setElapsedSeconds(0);
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
                        variant={provider.pricing?.tier === 'free' ? 'default' : 'secondary'}
                        className="capitalize"
                      >
                        {provider.pricing?.tier || 'free'}
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
                      
                      {/* Safe null check for pricing and freeQuota */}
                      {provider.pricing && provider.pricing.freeQuota && (
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
                    {selectedProvider.pricing?.tier || 'free'}
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
            <div className="pt-4 space-y-3">
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
              
              {/* Progress Indicator */}
              {isGenerating && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 animate-pulse">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-5 h-5 text-blue-600 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-blue-900">
                        {t.creation?.refinement?.form?.processing || "Processing your request..."}
                        {elapsedSeconds > 0 && <span className="ml-2 text-blue-600">({elapsedSeconds}s)</span>}
                      </p>
                      <p className="text-xs text-blue-700 mt-1">
                        {progressMessage || (t.creation?.refinement?.form?.processing_message || `Generating 3 AI images with ${selectedProvider?.name || "AI provider"}. This may take 20-90 seconds depending on the provider.`)}
                      </p>
                      <div className="mt-2 flex items-center gap-2 text-xs text-blue-600">
                        <span>⏳</span>
                        <span>Please wait while we create your images...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Generated Images Display */}
            {generatedImages.length > 0 && (
              <div className="space-y-3">
                <Label className="text-sm font-medium">{t.creation.refinement.form.generated_images || "Generated Images"}</Label>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                  {generatedImages.map((image, index) => (
                    <div 
                      key={index} 
                      className="relative aspect-square border rounded-lg overflow-hidden cursor-pointer hover:shadow-lg hover:scale-105 transition-all duration-200 group"
                      onClick={() => setSelectedImageIndex(index)}
                    >
                      <Image
                        src={image.url}
                        alt={`Generated image ${index + 1}`}
                        width={150}
                        height={150}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-200 flex items-center justify-center">
                        <svg 
                          className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                          xmlns="http://www.w3.org/2000/svg" 
                          fill="none" 
                          viewBox="0 0 24 24" 
                          stroke="currentColor"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                        </svg>
                      </div>
                      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-2">
                        <p className="text-white text-xs font-medium truncate">{image.ai_provider}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="text-center text-sm text-muted-foreground">
                  Click on any image to view larger
                </div>
              </div>
            )}

            {/* Image Modal */}
            {selectedImageIndex !== null && (
              <div 
                className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
                onClick={() => setSelectedImageIndex(null)}
              >
                <div 
                  className="relative max-w-4xl max-h-full bg-white rounded-lg overflow-hidden shadow-2xl"
                  onClick={(e) => e.stopPropagation()}
                >
                  {/* Modal Header */}
                  <div className="flex items-center justify-between p-4 border-b">
                    <div className="flex items-center gap-3">
                      <Badge variant="secondary" className="text-sm">
                        {generatedImages[selectedImageIndex].ai_provider}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        Image {selectedImageIndex + 1} of {generatedImages.length}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {/* Navigation Buttons */}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedImageIndex(
                          selectedImageIndex > 0 ? selectedImageIndex - 1 : generatedImages.length - 1
                        )}
                        disabled={generatedImages.length <= 1}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
                        </svg>
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedImageIndex(
                          selectedImageIndex < generatedImages.length - 1 ? selectedImageIndex + 1 : 0
                        )}
                        disabled={generatedImages.length <= 1}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                        </svg>
                      </Button>
                      {/* Close Button */}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedImageIndex(null)}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </Button>
                    </div>
                  </div>

                  {/* Modal Image */}
                  <div className="relative">
                    <Image
                      src={generatedImages[selectedImageIndex].url}
                      alt={`Generated image ${selectedImageIndex + 1}`}
                      width={800}
                      height={600}
                      className="w-full h-auto max-h-[70vh] object-contain"
                    />
                  </div>

                  {/* Modal Footer */}
                  <div className="p-4 border-t bg-gray-50">
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700">Prompt:</p>
                      <p className="text-sm text-gray-600 bg-white p-3 rounded border">
                        {generatedImages[selectedImageIndex].prompt}
                      </p>
                    </div>
                  </div>
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
