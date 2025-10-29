"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getTranslations } from "@/i18n";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { IdeaGenerationForm } from "@/components/forms/idea-generation-form";
import { EnhancedRefinementForm } from "@/components/forms/enhanced-refinement-form";
import { FinalizationForm } from "@/components/forms/finalization-form";
import { AIErrorDisplay } from "@/components/ui/ai-error-display";
import { MaterialStage, MaterialStatus, IdeaGenerationFormData, RefinementFormData, FinalizationFormData, GeneratedImage, Material } from "@/types";
import { createMaterial, addGeneratedImage, selectImage, addFeedback, updateStage } from "@/services/materials";
import { generateMultipleImages, getAvailableProviders, getRecommendedProvider, getProviderConfigurations, getActiveProviders, type ProviderConfig } from "@/services/ai-providers";
import { MATERIAL_CREATION_STEPS } from "@/constants";

export default function CreateMaterialPage({
  params
}: {
  params: { locale: string }
}) {  const locale = params.locale || "en";  const [t, setT] = useState<Record<string, any>>({});
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  
  const [currentStep, setCurrentStep] = useState(0);
  const [material, setMaterial] = useState<Material | null>(null);
  const [generatedImages, setGeneratedImages] = useState<GeneratedImage[]>([]);
  const [activeProviders, setActiveProviders] = useState<ProviderConfig[]>([]);
  const [aiError, setAiError] = useState<any>(null);
  useEffect(() => {
    const loadTranslations = async () => {
      setIsLoading(true);
      try {
        const translations = await getTranslations(locale === "pt" ? "pt" : "en");
        setT(translations);
        
        // Set a development token if none exists
        if (typeof window !== 'undefined' && !localStorage.getItem('token')) {
          // Use a fresh mock token for development - valid for 24 hours
          const devToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsInJvbGUiOiJhZG1pbiIsImlzX2FkbWluIjp0cnVlLCJpYXQiOjE3NTE0OTY4NjUsImV4cCI6MTc1NDA4ODg2NX0.1QglhuJU3ipmB1qt74lIRvhU-xk3-UkiwFBuzVvcYWc';
          localStorage.setItem('token', devToken);
          console.log('Development token set for testing');
        }

        // Load AI provider configurations
        await loadActiveProviders();
      } catch (error) {
        console.error("Error loading translations:", error);
      } finally {
        setIsLoading(false);
      }
    };
    loadTranslations();
    
    // Listen for provider config updates
    const handleConfigUpdate = (event: CustomEvent) => {
      console.log('AI Provider config updated in materials page, reloading...');
      loadActiveProviders();
    };
    
    // Listen for the custom event we dispatch when configs are updated
    window.addEventListener('aiProviderConfigUpdated', handleConfigUpdate as EventListener);
    
    // Also listen for localStorage changes from other tabs
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === 'ai-provider-configurations') {
        console.log('localStorage changed in materials page, reloading...');
        loadActiveProviders();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('aiProviderConfigUpdated', handleConfigUpdate as EventListener);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [locale]);

  const loadActiveProviders = async () => {
    try {
      console.log('Loading active AI providers for material creation...');
      const activeProvidersData = await getActiveProviders();
      
      console.log('Loaded active providers:', activeProvidersData);
      setActiveProviders(activeProvidersData);
      
      if (activeProvidersData.length === 0) {
        console.warn('No active AI providers found. Users need to configure providers in the AI Providers tab.');
      }
    } catch (error) {
      console.error('Error loading active providers:', error);
      setActiveProviders([]);
    }
  };
  const handleIdeaSubmit = async (data: IdeaGenerationFormData) => {
    try {
      const createdMaterial = await createMaterial({
        title: data.title,
        description: data.description,
        target_audience: data.target_audience,
        campaign_objective: data.campaign_objective,
        keywords: data.keywords,
      });
      
      // Check if we're in demo/mock mode
      if (createdMaterial.api_error) {
        console.log("Material created in demo/mock mode");
      }
      
      setMaterial(createdMaterial);
      setCurrentStep(1);
    } catch (error) {
      console.error("Error creating material:", error);
      // Show error to user
      alert(`Something went wrong: ${error.message || "Unknown error"}\n\nPlease try again.`);
    }
  };

  const handleGenerateImage = async (prompt: string, aiProvider: string) => {
    if (!material) {
      console.error("Cannot generate image: no material found");
      alert("Material not found. Please refresh the page.");
      return;
    }
    
    console.log("Generating multiple images with new AI provider service:", { materialId: material.id, prompt, aiProvider });
    
    // Clear any previous errors
    setAiError(null);
    
    try {
      // Check if the selected provider is active and configured
      const selectedProvider = activeProviders.find(p => p.id === aiProvider);
      
      if (!selectedProvider && activeProviders.length === 0) {
        alert("No AI providers are configured and active. Please configure an AI provider in the AI Providers tab first.");
        return;
      }
      
      // Use the specified provider or fall back to the first active one
      let providerToUse = aiProvider;
      if (!selectedProvider && activeProviders.length > 0) {
        providerToUse = activeProviders[0].id;
        console.log(`Provider ${aiProvider} not active, using: ${providerToUse}`);
      }
      
      // Generate 3 images (reduced from 5 to improve performance)
      console.log(`Generating 3 images with provider: ${providerToUse}`);
      
      const result = await generateMultipleImages(prompt, providerToUse, 3, '1024x1024');
      
      if (!result.success) {
        // Display enriched error if available
        if (result.error_details) {
          setAiError(result.error_details);
          return; // Exit early to show error display component
        }
        throw new Error(result.error || 'Failed to generate images');
      }
      
      console.log(`Successfully generated ${result.images.length} images:`, result);
      
      if (result.images.length === 0) {
        throw new Error("No images were generated. Please try again.");
      }
      
      // Add all generated images to the material
      let updatedMaterial = material;
      
      for (let i = 0; i < result.images.length; i++) {
        const imageUrl = result.images[i];
        const generationParams = {
          width: 1024,
          height: 1024,
          provider: result.provider,
          model: result.model,
          style: 'photorealistic',
          variation: i + 1,
          cost: result.cost || 0
        };
        
        console.log(`Adding generated image ${i + 1} to material...`);
        try {
          updatedMaterial = await addGeneratedImage(
            updatedMaterial.id,
            imageUrl,
            prompt,
            result.provider,
            generationParams
          );
        } catch (addError) {
          console.error(`Failed to add image ${i + 1} to material:`, addError);
          // Continue with other images
        }
      }
      
      console.log("Updated material with all new images:", updatedMaterial);
      setMaterial(updatedMaterial);
      setGeneratedImages(updatedMaterial.generated_images || []);
      
      const costMessage = result.cost && result.cost > 0 ? ` (Cost: $${result.cost.toFixed(4)})` : '';
      console.log(`Successfully generated ${result.images.length} images using ${result.provider}!${costMessage}`);
      
    } catch (error: any) {
      console.error("Error generating images:", error);
      
      // Check if error has enriched details (from network errors, timeout, etc.)
      if (error.error_details) {
        setAiError(error.error_details);
      } else if (error.isTimeout) {
        // Handle timeout errors specifically
        setAiError({
          error_type: 'timeout',
          message: error.userMessage || 'Request timeout',
          user_message: 'errors.ai.timeout',
          provider: aiProvider || 'unknown',
          correlation_id: error.error_details?.correlation_id || `client-${Date.now()}`,
          timestamp: new Date().toISOString(),
          http_status: 408,
          suggested_actions: [
            'actions.try_again',
            'actions.try_different_provider',
            'actions.reduce_image_complexity'
          ],
          details: error.error_details?.details || {}
        });
      } else {
        // Set generic error for unexpected exceptions
        setAiError({
          error_type: 'unknown',
          message: error.message || "Unknown error",
          user_message: "errors.ai.unknown",
          provider: aiProvider || 'unknown',
          correlation_id: `client-${Date.now()}`,
          timestamp: new Date().toISOString(),
          suggested_actions: ["actions.try_again", "actions.check_console"]
        });
      }
    }
  };

  const handleRefinementSubmit = async (data: RefinementFormData) => {
    if (!material) {
      console.error("Cannot submit refinement: no material found");
      return;
    }
    
    console.log("Submitting refinement with data:", data);
    
    try {
      const updatedMaterial = await updateStage(
        material.id, 
        MaterialStage.FINALIZATION,
        MaterialStatus.IN_PROGRESS
      );
      
      console.log("Material stage updated:", updatedMaterial);
      setMaterial(updatedMaterial);
      setCurrentStep(2);
    } catch (error: any) {
      console.error("Error updating stage:", error);
      
      // Enhanced error handling
      const errorMessage = error?.response?.data?.detail || 
                          error?.message || 
                          "Unknown error occurred while updating stage";
      const statusCode = error?.response?.status;
      
      // Set AI error state for better UX
      setAiError({
        error_type: statusCode === 404 ? 'not_found' : 'unknown',
        message: errorMessage,
        user_message: statusCode === 404 
          ? 'errors.stage_update_not_found' 
          : 'errors.stage_update_failed',
        correlation_id: `stage-update-${Date.now()}`,
        timestamp: new Date().toISOString(),
        http_status: statusCode,
        suggested_actions: ['actions.try_again', 'actions.refresh_page'],
        details: {
          materialId: material.id,
          targetStage: MaterialStage.FINALIZATION,
          error: errorMessage
        }
      });
      
      throw error; // Re-throw to allow form to handle error state
    }
  };

  const handleFinalizationSubmit = async (data: FinalizationFormData) => {
    if (!material) return;
    
    try {
      // Select the final image
      let updatedMaterial = await selectImage(material.id, data.selectedImage);
      
      // Add final feedback if provided
      if (data.finalFeedback) {
        updatedMaterial = await addFeedback(material.id, data.finalFeedback);
      }
      
      // Update to completed status
      updatedMaterial = await updateStage(
        material.id,
        MaterialStage.FINALIZATION,
        MaterialStatus.COMPLETED
      );
      
      // Redirect to the material detail page
      router.push(`/${locale}/materials/${material.id}`);
    } catch (error) {
      console.error("Error finalizing material:", error);
    }
  };
  // Loading state while translations are being fetched
  if (isLoading || !t.creation) {
    return (
      <div className="space-y-8">
        <div className="animate-pulse">
          <div className="h-10 w-3/4 bg-gray-200 rounded mb-2"></div>
          <div className="h-5 w-1/2 bg-gray-200 rounded"></div>
        </div>
        <div className="flex justify-between items-center">
          <div className="h-12 w-full bg-gray-200 rounded"></div>
        </div>
        <div className="mt-8">
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">
          {t.creation.title}
        </h1>
        <p className="text-muted-foreground">
          {MATERIAL_CREATION_STEPS[currentStep].description}
        </p>
      </div>

      <div className="flex justify-between items-center">
        <ol className="flex w-full">
          {MATERIAL_CREATION_STEPS.map((step, index) => (
            <li 
              key={step.id}
              className={`flex w-full items-center ${
                index !== MATERIAL_CREATION_STEPS.length - 1 
                  ? "after:content-[''] after:w-full after:h-1 after:border-b after:border-gray-200 after:border-4 after:inline-block" 
                  : ""
              }`}
            >
              <span className={`flex items-center justify-center w-10 h-10 rounded-full lg:h-12 lg:w-12 shrink-0 ${
                currentStep === index 
                  ? "bg-primary text-white" 
                  : currentStep > index 
                    ? "bg-green-500 text-white" 
                    : "bg-gray-200 text-gray-500"
              }`}>
                {currentStep > index ? (
                  <svg className="w-3.5 h-3.5 lg:w-4 lg:h-4" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
                    <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 5.917 5.724 10.5 15 1.5"/>
                  </svg>
                ) : (
                  index + 1
                )}
              </span>
              <span className="ml-2 text-sm font-medium sm:hidden lg:block">
                {step.title}
              </span>
            </li>
          ))}
        </ol>
      </div>

      <div className="mt-8">
        {/* AI Error Display - Shows when image generation fails */}
        {aiError && (
          <div className="mb-6">
            <AIErrorDisplay 
              error={aiError.message || "An error occurred"}
              errorDetails={aiError}
              onRetry={() => {
                setAiError(null);
                // User can retry by clicking generate again
              }}
              locale={locale}
            />
          </div>
        )}
        
        {currentStep === 0 && (
          <IdeaGenerationForm
            onSubmit={handleIdeaSubmit}
            locale={locale}
          />
        )}
        
        {currentStep === 1 && (
          <EnhancedRefinementForm
            onSubmit={handleRefinementSubmit}
            onGenerateImage={handleGenerateImage}
            aiProviders={activeProviders}
            generatedImages={generatedImages}
            locale={locale}
          />
        )}
        
        {currentStep === 2 && (
          <FinalizationForm
            onSubmit={handleFinalizationSubmit}
            generatedImages={generatedImages}
            locale={locale}
          />
        )}
      </div>
    </div>
  );
}
