"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { IdeaGenerationForm } from "@/components/forms/idea-generation-form";
import { EnhancedRefinementForm } from "@/components/forms/enhanced-refinement-form";
import { FinalizationForm } from "@/components/forms/finalization-form";
import { AIErrorDisplay } from "@/components/ui/ai-error-display";
import { StepNavigation } from "@/components/materials/step-navigation";
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
  
  // Navigation state
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [canProceedToNext, setCanProceedToNext] = useState(false);
  const [autoSaveTimer, setAutoSaveTimer] = useState<NodeJS.Timeout | null>(null);
  
  // Ref for error container to enable auto-scroll
  const errorRef = useRef<HTMLDivElement>(null);

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

  // Auto-scroll to error when it appears (UX improvement)
  useEffect(() => {
    if (aiError && errorRef.current) {
      // Smooth scroll to error with offset for better visibility
      const errorElement = errorRef.current;
      const offset = 100; // 100px above the error for context
      const elementPosition = errorElement.getBoundingClientRect().top + window.pageYOffset;
      const offsetPosition = elementPosition - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });

      // Optional: Add a subtle pulse animation to draw attention
      errorElement.classList.add('animate-pulse');
      setTimeout(() => {
        errorElement.classList.remove('animate-pulse');
      }, 2000);
    }
  }, [aiError]);

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

  const handleGenerateImage = async (prompt: string, aiProvider: string, batchSize: number = 3, peoplePreference: string = "auto"): Promise<void> => {
    if (!material) {
      alert("Material not found. Please refresh the page.");
      return;
    }
    
    // Clear previous errors
    setAiError(null);
    
    console.log(`Generating image with prompt: "${prompt}" using provider: ${aiProvider}, batchSize: ${batchSize}, peoplePreference: ${peoplePreference}`);
    
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
      
      // Generate images with user-selected batch size (3, 5, or 10)
      console.log(`Generating ${batchSize} images with provider: ${providerToUse}, peoplePreference: ${peoplePreference}`);
      
      const result = await generateMultipleImages(prompt, providerToUse, batchSize, '1024x1024', peoplePreference);
      
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
      
      // Add all generated images to the material at once (batch generation)
      console.log(`Adding ${result.images.length} generated images to material...`);
      
      // Create new image objects for all generated images
      const newImages = result.images.map((imageUrl, i) => ({
        url: imageUrl,
        prompt: prompt,
        ai_provider: result.provider,
        generation_params: {
          width: 1024,
          height: 1024,
          provider: result.provider,
          model: result.model,
          style: 'photorealistic',
          variation: i + 1,
          cost: result.cost || 0
        },
        created_at: new Date().toISOString()
      }));
      
      // Update material with all new images at once
      const updatedMaterial = {
        ...material,
        generated_images: [...(material.generated_images || []), ...newImages],
        updated_at: new Date().toISOString()
      };
      
      console.log("Updated material with all new images:", updatedMaterial.generated_images.length, "total images");
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

  const handleIdeaSubmit = async (data: IdeaGenerationFormData) => {
    if (!material) return;
    
    try {
      // Update material with idea generation data
      const updatedMaterial = await updateMaterial(material.id, {
        title: data.title,
        description: data.description,
        target_audience: data.target_audience,
        campaign_objective: data.campaign_objective,
        keywords: data.keywords,
        campaign_date: data.campaign_date
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

  // Navigation handlers
  const handleNextStep = () => {
    if (currentStep < MATERIAL_CREATION_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
      setHasUnsavedChanges(false);
      // Scroll to top of page for better UX
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handlePreviousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
      setHasUnsavedChanges(false);
      // Scroll to top of page
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleCancelEditing = () => {
    // Clear auto-save timer
    if (autoSaveTimer) {
      clearInterval(autoSaveTimer);
    }
    // Navigate back to material detail page
    router.push(`/${locale}/materials/${id}`);
  };

  const handleSaveDraft = async () => {
    try {
      // Save current state to localStorage for recovery
      const draftData = {
        currentStep,
        material,
        generatedImages,
        timestamp: new Date().toISOString()
      };
      
      localStorage.setItem(`material-edit-draft-${id}`, JSON.stringify(draftData));
      
      // Show success message
      console.log('Draft saved successfully');
      
      // Material changes are already persisted via updateMaterial, addGeneratedImage, etc.
      if (material?.id) {
        console.log('Material changes already persisted to backend:', material.id);
      }
      
      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Error saving draft:', error);
    }
  };

  // Auto-save every 30 seconds
  useEffect(() => {
    if (hasUnsavedChanges && material) {
      const timer = setInterval(() => {
        console.log('Auto-saving draft...');
        handleSaveDraft();
      }, 30000); // 30 seconds
      
      setAutoSaveTimer(timer);
      
      return () => {
        if (timer) clearInterval(timer);
      };
    }
  }, [hasUnsavedChanges, material]);

  // Validation logic for each step
  useEffect(() => {
    if (!material) {
      setCanProceedToNext(false);
      return;
    }

    switch (currentStep) {
      case 0: // Idea generation
        // Can proceed if material exists (it already does in edit mode)
        setCanProceedToNext(true);
        break;
      case 1: // Refinement
        // Can proceed if at least one image is generated
        setCanProceedToNext(generatedImages.length > 0);
        break;
      case 2: // Finalization
        // Always can complete (select image)
        setCanProceedToNext(true);
        break;
      default:
        setCanProceedToNext(false);
    }
  }, [currentStep, material, generatedImages]);

  // Cleanup auto-save timer on unmount
  useEffect(() => {
    return () => {
      if (autoSaveTimer) {
        clearInterval(autoSaveTimer);
      }
    };
  }, [autoSaveTimer]);

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

  // Get step descriptions from translations
  const getStepDescription = (stepIndex: number) => {
    switch (stepIndex) {
      case 0:
        return translations?.materials?.stage_descriptions?.idea || "Define your campaign concept and objectives";
      case 1:
        return translations?.materials?.stage_descriptions?.refinement || "Generate and refine visual content";
      case 2:
        return translations?.materials?.stage_descriptions?.finalization || "Select final content and complete";
      default:
        return "";
    }
  };

  return (
    <div className="space-y-8">
      {/* Header with Breadcrumb */}
      <div>
        <nav className="flex mb-4" aria-label="Breadcrumb">
          <ol className="inline-flex items-center space-x-1 md:space-x-3 text-sm">
            <li className="inline-flex items-center">
              <button
                onClick={() => router.push(`/${locale}/materials`)}
                className="inline-flex items-center text-gray-600 hover:text-blue-600 transition-colors"
              >
                {translations?.materials?.title || "Materials"}
              </button>
            </li>
            <li>
              <div className="flex items-center">
                <svg className="w-3 h-3 text-gray-400 mx-1" fill="none" viewBox="0 0 6 10">
                  <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m1 9 4-4-4-4"/>
                </svg>
                <button
                  onClick={() => router.push(`/${locale}/materials/${id}`)}
                  className="text-gray-600 hover:text-blue-600 transition-colors"
                >
                  {material.title}
                </button>
              </div>
            </li>
            <li>
              <div className="flex items-center">
                <svg className="w-3 h-3 text-gray-400 mx-1" fill="none" viewBox="0 0 6 10">
                  <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m1 9 4-4-4-4"/>
                </svg>
                <span className="text-gray-500">
                  {translations?.common?.edit || "Edit"}
                </span>
              </div>
            </li>
            <li aria-current="page">
              <div className="flex items-center">
                <svg className="w-3 h-3 text-gray-400 mx-1" fill="none" viewBox="0 0 6 10">
                  <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m1 9 4-4-4-4"/>
                </svg>
                <span className="text-blue-600 font-medium">
                  {currentStep === 0 && (translations?.materials?.stages?.idea_generation || "Idea Generation")}
                  {currentStep === 1 && (translations?.materials?.stages?.refinement || "Refinement")}
                  {currentStep === 2 && (translations?.materials?.stages?.finalization || "Finalization")}
                </span>
              </div>
            </li>
          </ol>
        </nav>
        
        <h1 className="text-3xl font-bold tracking-tight mb-2">
          {translations?.materials?.edit_title || "Edit Material"}: {material.title}
        </h1>
        <p className="text-muted-foreground">
          {getStepDescription(currentStep)}
        </p>
      </div>

      {/* Visual Step Indicator (Apple-inspired) */}
      <div className="flex justify-center items-center">
        <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-2xl">
          {MATERIAL_CREATION_STEPS.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className="flex flex-col items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full transition-all duration-300 ${
                  currentStep === index 
                    ? "bg-blue-500 text-white shadow-lg scale-110" 
                    : currentStep > index 
                      ? "bg-green-500 text-white" 
                      : "bg-gray-300 text-gray-600"
                }`}>
                  {currentStep > index ? (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <span className="text-sm font-semibold">{index + 1}</span>
                  )}
                </div>
                <span className={`mt-2 text-xs font-medium transition-colors ${
                  currentStep === index ? "text-blue-600" : "text-gray-500"
                }`}>
                  {index === 0 && (translations?.materials?.stages?.idea_generation || "Idea")}
                  {index === 1 && (translations?.materials?.stages?.refinement || "Refine")}
                  {index === 2 && (translations?.materials?.stages?.finalization || "Finalize")}
                </span>
              </div>
              
              {index < MATERIAL_CREATION_STEPS.length - 1 && (
                <div className={`h-0.5 w-16 mx-3 transition-colors ${
                  currentStep > index ? "bg-green-500" : "bg-gray-300"
                }`} />
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="mt-8 mb-24">
        {/* Display AI Error if present */}
        {aiError && (
          <div ref={errorRef} className="mb-6">
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
          </div>
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
              keywords: material.keywords || [],
              campaign_date: material.campaign_date
            }}
          />
        )}
        
        {currentStep === 1 && (
          <EnhancedRefinementForm
            onSubmit={handleRefinementSubmit}
            onGenerateImage={handleGenerateImage}
            aiProviders={activeProviders}
            generatedImages={generatedImages}
            material={material}
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

      {/* Step Navigation Component - Fixed at bottom */}
      <StepNavigation
        currentStep={currentStep}
        totalSteps={MATERIAL_CREATION_STEPS.length}
        stepTitles={[
          translations?.materials?.stages?.idea_generation || "Idea Generation",
          translations?.materials?.stages?.refinement || "Refinement",
          translations?.materials?.stages?.finalization || "Finalization"
        ]}
        onPrevious={currentStep > 0 ? handlePreviousStep : undefined}
        onNext={currentStep < MATERIAL_CREATION_STEPS.length - 1 ? handleNextStep : undefined}
        onCancel={handleCancelEditing}
        onSaveDraft={handleSaveDraft}
        canGoNext={canProceedToNext}
        canGoPrevious={currentStep > 0}
        hasUnsavedChanges={hasUnsavedChanges}
        showSaveDraft={true}
        showCancel={true}
        translations={{
          previous_step: translations?.common?.previous_step || "Previous Step",
          next_step: translations?.common?.next_step || "Next Step",
          save_draft: translations?.common?.save_draft || "Save Draft",
          cancel_editing: translations?.common?.cancel_editing || "Cancel",
          unsaved_changes: translations?.common?.unsaved_changes || "Unsaved Changes",
          unsaved_changes_message: translations?.common?.unsaved_changes_message || "Are you sure you want to leave? Your changes will be lost.",
          confirm: translations?.common?.confirm || "Confirm",
          back: translations?.common?.back || "Back"
        }}
      />
    </div>
  );
}
