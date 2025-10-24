"use client";

import React from "react";
import Image from "next/image";
import { getTranslations } from "@/i18n";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
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

export const RefinementForm: React.FC<RefinementFormProps> = ({
  onSubmit,
  onGenerateImage,
  aiProviders,
  generatedImages,
  initialData = {},
  locale = "en"
}) => {
  const [t, setT] = React.useState<Record<string, any>>({});
  const [formData, setFormData] = React.useState<RefinementFormData>({
    prompt: initialData.prompt || "Create a professional marketing image for a modern tech product",
    aiProvider: initialData.aiProvider || (aiProviders.length > 0 ? aiProviders[0].id : ""),
    generationParams: initialData.generationParams || {},
  });

  React.useEffect(() => {
    const loadTranslations = async () => {
      try {
        const translations = await getTranslations(locale === "pt" ? "pt" : "en");
        setT(translations);
      } catch (error) {
        console.error("Error loading translations:", error);
        // Fallback translations
        setT({
          creation: {
            refinement: {
              title: "Content Refinement",
              description: "Generate and refine visual content",
              form: {
                prompt: "Generation Prompt",
                prompt_placeholder: "Describe the image you want to generate",
                ai_provider: "AI Provider",
                generate_image: "Generate Image",
                generating: "Generating...",
                generated_images: "Generated Images",
                save: "Continue to Finalization",
                saving: "Saving..."
              }
            }
          }
        });
      }
    };
    loadTranslations();
  }, [locale]);
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Refinement form submitted with data:", formData);
    setIsSubmitting(true);

    try {
      await onSubmit(formData);
      console.log("Refinement form submission completed");
    } catch (error) {
      console.error("Error submitting refinement form:", error);
      setIsSubmitting(false); // Reset on error
    }
  };

  const handleGenerateImage = async () => {
    if (!formData.prompt || !formData.aiProvider) {
      console.warn("Cannot generate image: missing prompt or AI provider");
      return;
    }
    
    console.log("Generating image with:", { prompt: formData.prompt, provider: formData.aiProvider });
    setIsGenerating(true);
    
    try {
      await onGenerateImage(formData.prompt, formData.aiProvider);
      console.log("Image generation completed successfully");
    } catch (error) {
      console.error("Error generating image:", error);
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
          <div className="space-y-2">
            <Label htmlFor="prompt" className="text-sm font-medium">{t.creation.refinement.form.prompt}</Label>
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
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="aiProvider" className="text-sm font-medium">{t.creation.refinement.form.ai_provider}</Label>
            <div className="relative">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2"/>
                <path d="M14.5 4.5c-1.8.7-3 2.5-3 4.5 0 0-2 0-2 2 0 2 2 2 2 2"/>
                <path d="M14.5 4.5A4 4 0 1 1 18 9"/>
                <path d="M3 12h2"/>
                <path d="M19 12h2"/>
                <path d="M12 3v2"/>
                <path d="M12 19v2"/>
                <path d="m9 7-1-1"/>
                <path d="m16 16-1-1"/>
                <path d="m9 17-1 1"/>
                <path d="m16 8-1 1"/>
              </svg>
              <select
                id="aiProvider"
                name="aiProvider"
                value={formData.aiProvider}
                onChange={handleChange as React.ChangeEventHandler<HTMLSelectElement>}
                required
                className="w-full pl-10 focus:border-accent transition-all h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {aiProviders.map((provider) => (
                  <option key={provider.id} value={provider.id}>
                    {provider.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="pt-4">
            <Button
              type="button"
              onClick={handleGenerateImage}
              disabled={isGenerating || !formData.prompt || !formData.aiProvider}
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
                  <span className="font-medium">{t.creation?.refinement?.form?.generate_image || "Generate Image"}</span>
                </>
              )}
            </Button>
            
            {/* Debug/Test Button for Development */}
            {process.env.NODE_ENV === 'development' && (
              <Button
                type="button"
                onClick={() => {
                  console.log("Debug: Current form data:", formData);
                  console.log("Debug: Generated images:", generatedImages);
                  console.log("Debug: AI Providers:", aiProviders);
                  alert(`Debug Info:\nPrompt: ${formData.prompt}\nProvider: ${formData.aiProvider}\nImages: ${generatedImages.length}`);
                }}
                variant="outline"
                className="w-full mt-2 text-sm"
              >
                🐛 Debug Form State
              </Button>
            )}
          </div>

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
                      {image.prompt.length > 50 ? `${image.prompt.substring(0, 50)}...` : image.prompt}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-between items-center border-t pt-6">
          <div className="text-sm text-muted-foreground">
            Generate images to proceed to the next step
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
  );
};
