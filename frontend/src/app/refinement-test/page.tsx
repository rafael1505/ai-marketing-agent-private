"use client";

import React, { useState } from "react";
import { RefinementForm } from "@/components/forms/refinement-form";
import { DEFAULT_AI_PROVIDERS } from "@/constants";
import { GeneratedImage } from "@/types";

export default function RefinementTestPage() {
  const [generatedImages, setGeneratedImages] = useState<GeneratedImage[]>([]);

  const handleSubmit = async (data: any) => {
    console.log("Test refinement submit:", data);
    alert("Refinement form submitted! Check console for data.");
  };

  const handleGenerateImage = async (prompt: string, provider: string) => {
    console.log("Test image generation:", { prompt, provider });
    
    // Simulate image generation
    const newImage: GeneratedImage = {
      url: `https://picsum.photos/seed/${Date.now()}/512/512`,
      prompt,
      ai_provider: provider,
      generation_params: { width: 512, height: 512, seed: Date.now() },
      created_at: new Date().toISOString()
    };
    
    setGeneratedImages(prev => [...prev, newImage]);
    alert("Image generated! Check the form for the new image.");
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Refinement Form Test</h1>
      
      <RefinementForm
        onSubmit={handleSubmit}
        onGenerateImage={handleGenerateImage}
        aiProviders={DEFAULT_AI_PROVIDERS}
        generatedImages={generatedImages}
        locale="en"
      />
    </div>
  );
}
