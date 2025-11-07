"use client";

import React from "react";
import { getTranslations } from "@/i18n";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader } from "@/components/ui/loader";
import { IdeaGenerationFormData } from "@/types";

interface IdeaGenerationFormProps {
  onSubmit: (data: IdeaGenerationFormData) => void;
  initialData?: Partial<IdeaGenerationFormData>;
  locale?: string;
}

export const IdeaGenerationForm: React.FC<IdeaGenerationFormProps> = ({
  onSubmit,
  initialData = {},
  locale = "en"
}) => {
  const t = getTranslations(locale === "pt" ? "pt" : "en");
  const [formData, setFormData] = React.useState<IdeaGenerationFormData>({
    title: initialData.title || "",
    description: initialData.description || "", // Legacy field for compatibility
    target_audience: initialData.target_audience || "",
    campaign_objective: initialData.campaign_objective || "",
    keywords: initialData.keywords || [],
  });
  const [keywordsInput, setKeywordsInput] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);

  // Reinitialize form when initialData changes (e.g., when navigating back)
  React.useEffect(() => {
    if (initialData && Object.keys(initialData).length > 0) {
      setFormData({
        title: initialData.title || "",
        description: initialData.description || "", // Legacy field
        target_audience: initialData.target_audience || "",
        campaign_objective: initialData.campaign_objective || "",
        keywords: initialData.keywords || [],
      });
    }
  }, [initialData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // If there are keywords in the input, add them
    if (keywordsInput) {
      const newKeywords = keywordsInput
        .split(",")
        .map((k) => k.trim())
        .filter((k) => k);
      
      formData.keywords = [...formData.keywords, ...newKeywords];
    }

    try {
      onSubmit(formData);
    } catch (error) {
      console.error("Error submitting idea form:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const addKeyword = () => {
    if (!keywordsInput.trim()) return;
    
    const newKeywords = keywordsInput
      .split(",")
      .map((k) => k.trim())
      .filter((k) => k);
    
    setFormData((prev) => ({
      ...prev,
      keywords: [...prev.keywords, ...newKeywords]
    }));
    
    setKeywordsInput("");
  };

  const removeKeyword = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      keywords: prev.keywords.filter((_, i) => i !== index)
    }));
  };

  return (    <Card className="shadow-lg border-t-4 border-t-primary">
      <CardHeader className="bg-gradient-to-r from-primary/5 to-accent/5">
        <div className="flex items-center space-x-2 mb-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          <CardTitle className="text-xl font-semibold">{t.creation.idea.title}</CardTitle>
        </div>
        <CardDescription>{t.creation.idea.description}</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit} className="fade-in">
        <CardContent className="space-y-6 pt-6">
          <div className="space-y-2">
            <Label htmlFor="title" className="text-sm font-medium">{t.creation.idea.form.title}</Label>
            <Input
              id="title"
              name="title"
              placeholder={t.creation.idea.form.title_placeholder}
              value={formData.title}
              onChange={handleChange}
              required
              className="focus:border-primary transition-all"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="target_audience" className="text-sm font-medium flex items-center space-x-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
              <span>{t.creation.idea.form.target_audience}</span>
            </Label>
            <Input
              id="target_audience"
              name="target_audience"
              placeholder={t.creation.idea.form.target_audience_placeholder}
              value={formData.target_audience}
              onChange={handleChange}
              className="focus:border-primary transition-all"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="campaign_objective" className="text-sm font-medium flex items-center space-x-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-accent">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              <span>{t.creation.idea.form.campaign_objective}</span>
            </Label>
            <Input
              id="campaign_objective"
              name="campaign_objective"
              placeholder={t.creation.idea.form.campaign_objective_placeholder}
              value={formData.campaign_objective}
              onChange={handleChange}
              className="focus:border-primary transition-all"
            />
          </div>

          <div className="space-y-3">
            <Label htmlFor="keywords" className="text-sm font-medium flex items-center space-x-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                <line x1="7" y1="7" x2="7.01" y2="7"></line>
              </svg>
              <span>{t.creation.idea.form.keywords}</span>
            </Label>
            <div className="flex space-x-2">
              <Input
                id="keywords"
                placeholder={t.creation.idea.form.keywords_placeholder}
                value={keywordsInput}
                onChange={(e) => setKeywordsInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addKeyword();
                  }
                }}
                className="focus:border-primary transition-all"
              />
              <Button 
                type="button" 
                onClick={addKeyword} 
                variant="outline"
                className="btn-scale"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                Add
              </Button>
            </div>
            
            {formData.keywords.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3 p-3 bg-secondary/50 rounded-md border border-border">
                {formData.keywords.map((keyword, index) => (
                  <div
                    key={index}
                    className="flex items-center bg-secondary rounded-full px-3 py-1 text-sm transition-all hover:shadow-sm"
                  >
                    <span className="text-secondary-foreground">{keyword}</span>
                    <button
                      type="button"
                      className="ml-2 text-secondary-foreground/70 hover:text-secondary-foreground transition-colors rounded-full h-5 w-5 inline-flex items-center justify-center"
                      onClick={() => removeKeyword(index)}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
        <CardFooter className="flex justify-between items-center border-t pt-6">
          <div className="text-sm text-muted-foreground">
            All fields are required for optimal results
          </div>
          <Button 
            type="submit" 
            isLoading={isLoading}
            className="btn-scale bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white shadow-lg hover:shadow-xl transition-all duration-200"
            size="lg"
          >
            {isLoading ? (
              <>
                <Loader size="sm" color="white" className="mr-3" />
                <span className="font-medium">Creating...</span>
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
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
                <span className="font-medium">{t.creation.idea.form.submit}</span>
              </>
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
};
