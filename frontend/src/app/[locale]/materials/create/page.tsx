"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getTranslations } from "@/i18n";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { IdeaGenerationForm } from "@/components/forms/idea-generation-form";
import { RefinementForm } from "@/components/forms/refinement-form";
import { FinalizationForm } from "@/components/forms/finalization-form";
import { MaterialStage, MaterialStatus, IdeaGenerationFormData, RefinementFormData, FinalizationFormData, GeneratedImage, Material } from "@/types";
import { createMaterial, addGeneratedImage, selectImage, addFeedback, updateStage } from "@/services/materials";
import { DEFAULT_AI_PROVIDERS, MATERIAL_CREATION_STEPS } from "@/constants";

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
    if (!material) return;
    
    try {
      // In a real implementation, you would integrate with the chosen AI provider here
      // For now, we'll use a placeholder image URL
      const generationParams = {
        width: 512,
        height: 512,
        steps: 30,
        seed: Math.floor(Math.random() * 100000),
      };
      
      const placeholderImageUrl = `https://picsum.photos/seed/${generationParams.seed}/512/512`;
      
      const updatedMaterial = await addGeneratedImage(
        material.id,
        placeholderImageUrl,
        prompt,
        aiProvider,
        generationParams
      );
      
      setMaterial(updatedMaterial);
      setGeneratedImages(updatedMaterial.generated_images);
    } catch (error) {
      console.error("Error generating image:", error);
    }
  };

  const handleRefinementSubmit = async (data: RefinementFormData) => {
    if (!material) return;
    
    try {
      const updatedMaterial = await updateStage(
        material.id, 
        MaterialStage.FINALIZATION,
        MaterialStatus.IN_PROGRESS
      );
      
      setMaterial(updatedMaterial);
      setCurrentStep(2);
    } catch (error) {
      console.error("Error updating stage:", error);
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
          <RefinementForm
            onSubmit={handleRefinementSubmit}
            onGenerateImage={handleGenerateImage}
            aiProviders={DEFAULT_AI_PROVIDERS}
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
