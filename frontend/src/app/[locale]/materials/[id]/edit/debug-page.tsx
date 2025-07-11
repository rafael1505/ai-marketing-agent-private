"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { MaterialStage, MaterialStatus, Material } from "@/types";
import { MATERIAL_CREATION_STEPS } from "@/constants";

export default function DebugEditPage({
  params
}: {
  params: { locale: string; id: string }
}) {
  const { locale, id } = params;
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [material, setMaterial] = useState<Material | null>(null);

  useEffect(() => {
    console.log("Debug Edit Page - Starting to load material", { locale, id });
    setIsLoading(true);
    
    // Create a mock material immediately
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
    
    console.log("Debug Edit Page - Setting mock material", mockMaterial);
    setMaterial(mockMaterial);
    setIsLoading(false);
  }, [id, locale]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        <p className="ml-4">Loading material...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h1 className="text-2xl font-bold mb-4">Error</h1>
        <p className="text-gray-600 mb-4">{error}</p>
        <Button onClick={() => router.push(`/${locale}/materials`)}>
          Back to Materials
        </Button>
      </div>
    );
  }

  if (!material) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h1 className="text-2xl font-bold mb-4">Material Not Found</h1>
        <Button onClick={() => router.push(`/${locale}/materials`)}>
          Back to Materials
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-8">
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
          Successfully loaded material for editing
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
                index === 0 
                  ? "bg-primary text-white" 
                  : "bg-gray-200 text-gray-500"
              }`}>
                {index + 1}
              </span>
              <span className="ml-2 text-sm font-medium sm:hidden lg:block">
                {step.title}
              </span>
            </li>
          ))}
        </ol>
      </div>

      <div className="mt-8 p-6 bg-gray-50 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">Material Details</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <strong>Title:</strong> {material.title}
          </div>
          <div>
            <strong>ID:</strong> {material.id}
          </div>
          <div>
            <strong>Stage:</strong> {material.stage}
          </div>
          <div>
            <strong>Status:</strong> {material.status}
          </div>
          <div className="col-span-2">
            <strong>Description:</strong> {material.description}
          </div>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Multi-Step Workflow</h2>
        <p className="text-gray-600">
          This debug page confirms that the edit page can load properly with the full multi-step workflow structure. 
          The actual form components will be loaded here once the basic page structure is working correctly.
        </p>
      </div>
    </div>
  );
}
