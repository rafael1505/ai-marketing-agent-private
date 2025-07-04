"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getTranslations } from "@/i18n";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { IdeaGenerationForm } from "@/components/forms/idea-generation-form";
import { EnhancedRefinementForm } from "@/components/forms/enhanced-refinement-form";
import { FinalizationForm } from "@/components/forms/finalization-form";
import { MaterialStage, MaterialStatus, IdeaGenerationFormData, RefinementFormData, FinalizationFormData, GeneratedImage, Material } from "@/types";
import { createMaterial, addGeneratedImage, selectImage, addFeedback, updateStage } from "@/services/materials";
import { MATERIAL_CREATION_STEPS } from "@/constants";
import { MARKETING_AI_PROVIDERS } from "@/constants/marketing-ai-providers";

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
      } catch (error) {
        console.error("Error loading translations:", error);
      } finally {
        setIsLoading(false);
      }
    };
    loadTranslations();
  }, [locale]);
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
      return;
    }
    
    console.log("Generating multiple images with:", { materialId: material.id, prompt, aiProvider });
    
    try {
      // Generate 5 images as per SRS requirements
      const numberOfImages = 5;
      const generatedImages: any[] = [];
      
      for (let i = 0; i < numberOfImages; i++) {
        console.log(`Generating image ${i + 1} of ${numberOfImages}...`);
        
        // Add slight variation to each request to get different images
        const variationPrompt = i === 0 ? prompt : `${prompt} (style ${i + 1})`;
        
        try {
          const response = await fetch(`/api/v1/ai/generate-image?prompt=${encodeURIComponent(variationPrompt)}&ai_provider=${encodeURIComponent(aiProvider)}&size=1024x1024&style=photorealistic`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (!response.ok) {
            throw new Error(`Generation failed: ${response.status} ${response.statusText}`);
          }
          
          const result = await response.json();
          if (!result.success) {
            throw new Error(result.error || "Image generation failed");
          }
          
          generatedImages.push({
            ...result,
            prompt: variationPrompt,
            index: i + 1
          });
          
          console.log(`Successfully generated image ${i + 1}`);
        } catch (imageError) {
          console.error(`Failed to generate image ${i + 1}:`, imageError);
          // Continue with other images even if one fails
        }
      }
      
      console.log(`Generated ${generatedImages.length} images successfully`);
      
      if (generatedImages.length === 0) {
        throw new Error("Failed to generate any images");
      }
      
      // Add all generated images to the material
      let updatedMaterial = material;
      
      for (const result of generatedImages) {
        const generationParams = {
          width: 1024,
          height: 1024,
          provider: aiProvider,
          style: 'photorealistic',
          variation: result.index
        };
        
        console.log(`Adding generated image ${result.index} to material...`);
        updatedMaterial = await addGeneratedImage(
          updatedMaterial.id,
          result.image_url,
          result.prompt,
          aiProvider,
          generationParams
        );
      }
      
      console.log("Updated material with all new images:", updatedMaterial);
      setMaterial(updatedMaterial);
      setGeneratedImages(updatedMaterial.generated_images || []);
    } catch (error) {
      console.error("Error generating images:", error);
      alert(`Failed to generate images: ${error.message || "Unknown error"}`);
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
    } catch (error) {
      console.error("Error updating stage:", error);
      alert(`Failed to proceed to finalization: ${error.message || "Unknown error"}`);
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
            aiProviders={MARKETING_AI_PROVIDERS}
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
