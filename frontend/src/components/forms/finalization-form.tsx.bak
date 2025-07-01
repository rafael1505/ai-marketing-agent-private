"use client";

import React from "react";
import Image from "next/image";
import { getTranslations } from "@/i18n";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { FinalizationFormData, GeneratedImage } from "@/types";
import { Loader } from "@/components/ui/loader";

interface FinalizationFormProps {
  onSubmit: (data: FinalizationFormData) => void;
  generatedImages: GeneratedImage[];
  initialData?: Partial<FinalizationFormData>;
  locale?: string;
}

export const FinalizationForm: React.FC<FinalizationFormProps> = ({
  onSubmit,
  generatedImages,
  initialData = {},
  locale = "en"
}) => {
  // Using Record<string, unknown> to allow for nested translation objects
  const [t, setT] = React.useState<Record<string, unknown>>({});
  const [formData, setFormData] = React.useState<FinalizationFormData>({
    selectedImage: initialData.selectedImage || "",
    finalFeedback: initialData.finalFeedback || "",
  });
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  React.useEffect(() => {
    const loadTranslations = async () => {
      const translations = await getTranslations(locale === "pt" ? "pt" : "en");
      setT(translations);
    };
    loadTranslations();
  }, [locale]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSelectImage = (url: string) => {
    setFormData((prev) => ({ ...prev, selectedImage: url }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      onSubmit(formData);
    } catch (error) {
      console.error("Error submitting finalization form:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!t || Object.keys(t).length === 0) {
    return (
      <div className="flex justify-center items-center h-40">
        <Loader size="lg" />
      </div>
    );
  }

  // Get the correct translation object or provide fallbacks
  const translations = t as any; // Type assertion for easier access
  const finalizeTitle = translations?.creation?.finalization?.title || "Finalize Campaign";
  const finalizeDesc = translations?.creation?.finalization?.description || "Choose final image and provide feedback";
  const selectImageLabel = translations?.creation?.finalization?.form?.select_image || "Select an Image";
  const finalFeedbackLabel = translations?.creation?.finalization?.form?.final_feedback || "Final Feedback";
  const finalFeedbackPlaceholder = translations?.creation?.finalization?.form?.final_feedback_placeholder || "Add any final adjustments or notes...";
  const submitLabel = translations?.creation?.finalization?.form?.submit || "Finalize Campaign";
  const submittingLabel = translations?.creation?.finalization?.form?.submitting || "Finalizing...";

  return (
    <Card className="shadow-lg border-t-4 border-t-success">
      <CardHeader className="bg-gradient-to-r from-success/5 to-primary/5">
        <div className="flex items-center space-x-2 mb-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-success">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          <CardTitle className="text-xl font-semibold">{finalizeTitle}</CardTitle>
        </div>
        <CardDescription>{finalizeDesc}</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit} className="fade-in">
        <CardContent className="space-y-6 pt-6">
          <div className="space-y-3">
            <Label className="text-sm font-medium">{selectImageLabel}</Label>
            
            {generatedImages.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {generatedImages.map((image, index) => (
                  <div 
                    key={index} 
                    className={`
                      relative border rounded-md overflow-hidden transition-all duration-300 cursor-pointer
                      ${formData.selectedImage === image.url ? 'ring-2 ring-success shadow-lg scale-[1.02]' : 'hover:shadow-md'}
                    `}
                    onClick={() => handleSelectImage(image.url)}
                  >
                    <Image
                      src={image.url}
                      alt={`Generated image ${index + 1}`}
                      width={300}
                      height={300}
                      className="w-full h-auto object-cover"
                    />
                    {formData.selectedImage === image.url && (
                      <div className="absolute top-2 right-2 bg-success text-white rounded-full p-0.5">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                      </div>
                    )}
                    <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white p-2 text-xs">
                      {image.prompt.length > 40 ? `${image.prompt.substring(0, 40)}...` : image.prompt}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex justify-center items-center h-40 bg-muted rounded-md border border-dashed">
                <p className="text-muted-foreground">No images available</p>
              </div>
            )}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="finalFeedback" className="text-sm font-medium">{finalFeedbackLabel}</Label>
            <div className="relative">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="absolute left-3 top-3 text-muted-foreground">
                <path d="M3 3v18h18"/>
                <path d="m7 17 4-4"/>
                <path d="M11 17h6v-6"/>
                <path d="m7 8 5 5 5-5"/>
              </svg>
              <Textarea
                id="finalFeedback"
                name="finalFeedback"
                placeholder={finalFeedbackPlaceholder}
                value={formData.finalFeedback}
                onChange={handleChange}
                rows={4}
                className="focus:border-success transition-all resize-none pl-10"
              />
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex justify-end space-x-4 pt-2">
          <Button
            type="submit"
            disabled={isSubmitting || !formData.selectedImage}
            className="btn-scale bg-success hover:bg-success/90"
          >
            {isSubmitting ? (
              <>
                <Loader size="sm" color="white" className="mr-2" />
                {submittingLabel}
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2">
                  <path d="m8.5 14.5 2 2 5-5"/>
                  <path d="M22 12c0-5.5-4.5-10-10-10S2 6.5 2 12s4.5 10 10 10 10-4.5 10-10z"/>
                </svg>
                {submitLabel}
              </>
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
};
