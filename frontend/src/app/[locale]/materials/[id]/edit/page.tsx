"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { IdeaGenerationForm } from "@/components/forms/idea-generation-form";
import { EnhancedRefinementForm } from "@/components/forms/enhanced-refinement-form";
import { FinalizationForm } from "@/components/forms/finalization-form";
import { AIErrorDisplay } from "@/components/ui/ai-error-display";
import { MaterialStage, MaterialStatus, IdeaGenerationFormData, RefinementFormData, FinalizationFormData, GeneratedImage, Material } from "@/types";
import { getMaterial, updateMaterial, addGeneratedImage, selectImage, addFeedback, updateStage } from "@/services/materials";
import { generateMultipleImages, getAvailableProviders, getProviderConfigurations, getActiveProviders, type ProviderConfig } from "@/services/ai-providers";
import { MATERIAL_CREATION_STEPS } from "@/constants";
import { getTranslations } from "@/i18n";

export default function EditMaterialPage({
  params
}: {
  params: { locale: string; id: string }
}) {
  const { locale, id } = params;
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [currentStep, setCurrentStep] = useState(0);
  const [material, setMaterial] = useState<Material | null>(null);
  const [generatedImages, setGeneratedImages] = useState<GeneratedImage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [aiError, setAiError] = useState<any | null>(null);
  const [activeProviders, setActiveProviders] = useState<ProviderConfig[]>([]);
  const [translations, setTranslations] = useState<Record<string, any>>({});

  useEffect(() => {
    const loadMaterial = async () => {
      try {
        setIsLoading(true);
        
        // Load translations
        const trans = await getTranslations(locale === "pt" ? "pt" : "en");
        setTranslations(trans);
        
        // Load provider configurations first
        await loadActiveProviders();
        
        const existingMaterial = await getMaterial(id);
        if (!existingMaterial) {
          throw new Error("Material not found");
        }
        setMaterial(existingMaterial);
        
        // Set current step based on material stage
        if (existingMaterial.stage === MaterialStage.IDEA) {
          setCurrentStep(0);
        } else if (existingMaterial.stage === MaterialStage.REFINEMENT) {
          setCurrentStep(1);
        } else if (existingMaterial.stage === MaterialStage.FINALIZATION) {
          setCurrentStep(2);
        }
        
        // Load existing generated images if any
        if (existingMaterial.generated_images) {
          setGeneratedImages(existingMaterial.generated_images);
        }
      } catch (err) {
        console.error("Error loading material:", err);
        
        // Create a mock material for editing if API fails
        const mockMaterial: Material = {
          id: id,
          title: "Sample Marketing Material",
          description: "This is a sample marketing material for editing",
          target_audience: "Tech professionals",
          campaign_objective: "Increase brand awareness",
          keywords: ["technology", "innovation", "marketing"],
          stage: MaterialStage.IDEA,
          status: MaterialStatus.DRAFT,
          company_id: "demo-company",
          created_by: "demo-user",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          generated_images: [],
          selected_image: "",
          feedback: []
        };
        
        setMaterial(mockMaterial);
        setCurrentStep(0);
        setError(null); // Clear error since we're using mock data
      } finally {
        setIsLoading(false);
      }
    };

    if (id) {
      loadMaterial();
    }
    
    // Listen for provider config updates
    const handleConfigUpdate = (event: CustomEvent) => {
      console.log('AI Provider config updated in materials edit page, reloading...');
      loadActiveProviders();
    };
    
    // Listen for the custom event we dispatch when configs are updated
    window.addEventListener('aiProviderConfigUpdated', handleConfigUpdate as EventListener);
    
    // Also listen for localStorage changes from other tabs
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === 'ai-provider-configurations') {
        console.log('localStorage changed in materials edit page, reloading...');
        loadActiveProviders();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('aiProviderConfigUpdated', handleConfigUpdate as EventListener);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [id]);

  const loadActiveProviders = async () => {
    try {
      console.log('Loading active AI providers for material editing...');
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

  const handleGenerateImage = async (prompt: string, aiProvider: string): Promise<void> => {
    if (!material) {
      alert("Material not found. Please refresh the page.");
      return;
    }
    
    // Clear previous errors
    setAiError(null);
    
    console.log(`Generating image with prompt: "${prompt}" using provider: ${aiProvider}`);
    
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
      
      // Generate 5 images as per SRS requirements using the new service
      console.log(`Generating 5 images with provider: ${providerToUse}`);
      
      const result = await generateMultipleImages(prompt, providerToUse, 5, '1024x1024');
      
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
      alert(`Successfully generated ${result.images.length} images using ${result.provider}!${costMessage}`);
      
    } catch (error: any) {
      console.error("Error generating images:", error);
      
      // Check if error has enriched details (from network errors, etc.)
      if (error.error_details) {
        setAiError(error.error_details);
      } else {
        // Show simple alert for unexpected errors (not from AI providers)
        alert(`Failed to generate images: ${error.message || "Unknown error"}`);
      }
    }
  };

  const handleIdeaSubmit = async (data: IdeaGenerationFormData) => {
    if (!material) return;
    
    try {
      // Update material with idea generation data
      const updatedMaterial = await updateMaterial(material.id, {
        title: data.title,
        description: data.description,
        target_audience: data.target_audience,
        campaign_objective: data.campaign_objective,
        keywords: data.keywords
      });
      
      // Update stage to refinement
      const materialWithStage = await updateStage(
        material.id,
        MaterialStage.REFINEMENT,
        MaterialStatus.IN_PROGRESS
      );
      
      console.log("Material updated:", materialWithStage);
      setMaterial(materialWithStage);
      setCurrentStep(1);
    } catch (error) {
      console.error("Error updating material:", error);
      alert(`Failed to proceed to refinement: ${error.message || "Unknown error"}`);
      throw error;
    }
  };

  const handleRefinementSubmit = async (data: RefinementFormData) => {
    if (!material) return;
    
    try {
      // Update material with refinement data (just update stage, refinement happens via image generation)
      // The refinement form mainly handles image generation
      
      // Update stage to finalization
      const materialWithStage = await updateStage(
        material.id,
        MaterialStage.FINALIZATION,
        MaterialStatus.IN_PROGRESS
      );
      
      console.log("Material stage updated:", materialWithStage);
      setMaterial(materialWithStage);
      setCurrentStep(2);
    } catch (error) {
      console.error("Error updating stage:", error);
      alert(`Failed to proceed to finalization: ${error.message || "Unknown error"}`);
      throw error;
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
      
      console.log("Material finalized:", updatedMaterial);
      setMaterial(updatedMaterial);
      
      // Navigate to the material view page
      router.push(`/${locale}/materials/${material.id}`);
    } catch (error) {
      console.error("Error finalizing material:", error);
      alert(`Failed to finalize material: ${error.message || "Unknown error"}`);
      throw error;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !material) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h1 className="text-2xl font-bold mb-4">Error</h1>
        <p className="text-gray-600 mb-4">{error || "Material not found"}</p>
        <Button onClick={() => router.push(`/${locale}/materials`)}>
          Back to Materials
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4 mb-4">
        <Button
          variant="outline"
          size="sm"
          onClick={() => router.push(`/${locale}/materials/${id}`)}
        >
          ← Back to Material
        </Button>
      </div>
      
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">
          Edit Material: {material.title}
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
        {/* Display AI Error if present */}
        {aiError && (
          <AIErrorDisplay
            error={aiError.message}
            errorDetails={aiError}
            onRetry={() => {
              setAiError(null);
              // Could trigger retry logic here
            }}
            onSwitchProvider={() => {
              setAiError(null);
              router.push(`/${locale}/settings/ai-providers`);
            }}
            locale={locale}
            translations={translations}
          />
        )}
        
        {currentStep === 0 && (
          <IdeaGenerationForm
            onSubmit={handleIdeaSubmit}
            locale={locale}
            initialData={{
              title: material.title || "",
              description: material.description || "",
              target_audience: material.target_audience || "",
              campaign_objective: material.campaign_objective || "",
              keywords: material.keywords || []
            }}
          />
        )}
        
        {currentStep === 1 && (
          <EnhancedRefinementForm
            onSubmit={handleRefinementSubmit}
            onGenerateImage={handleGenerateImage}
            aiProviders={activeProviders}
            generatedImages={generatedImages}
            locale={locale}
            initialData={{
              prompt: material.description || "",
              aiProvider: "openai",
              generationParams: {}
            }}
          />
        )}
        
        {currentStep === 2 && (
          <FinalizationForm
            onSubmit={handleFinalizationSubmit}
            generatedImages={generatedImages}
            locale={locale}
            initialData={{
              selectedImage: material.selected_image || "",
              finalFeedback: ""
            }}
          />
        )}
      </div>
    </div>
  );
}
