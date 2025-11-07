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
import { PromptTemplateSelector } from "@/components/ui/prompt-template-selector";
import { PROMPT_TEMPLATES, type PromptTemplate } from "@/data/prompt-templates";
import { getDatePresets, generateSeasonalContext, formatSeasonalContext, type SeasonalContext } from "@/lib/seasonal-context";

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
    campaign_brief: initialData.campaign_brief || initialData.description || "", // New field, fallback to description
    target_audience: initialData.target_audience || "",
    campaign_objective: initialData.campaign_objective || "",
    creative_approach: initialData.creative_approach || "hybrid", // Default to hybrid
    keywords: initialData.keywords || [],
    campaign_date: initialData.campaign_date || new Date(),
  });
  const [keywordsInput, setKeywordsInput] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);
  const [selectedTemplate, setSelectedTemplate] = React.useState<PromptTemplate | null>(null);
  const [showDatePresets, setShowDatePresets] = React.useState(false);
  const [seasonalContext, setSeasonalContext] = React.useState<SeasonalContext | null>(null);
  const datePresets = getDatePresets();

  // Reinitialize form when initialData changes (e.g., when navigating back)
  React.useEffect(() => {
    if (initialData && Object.keys(initialData).length > 0) {
      setFormData({
        title: initialData.title || "",
        description: initialData.description || "", // Legacy field
        campaign_brief: initialData.campaign_brief || initialData.description || "", // New field with fallback
        target_audience: initialData.target_audience || "",
        campaign_objective: initialData.campaign_objective || "",
        creative_approach: initialData.creative_approach || "hybrid", // Default to hybrid
        keywords: initialData.keywords || [],
        campaign_date: initialData.campaign_date || new Date(),
      });
      console.log("Form reinitialized with saved data:", initialData);
    }
  }, [initialData]);

  // Update seasonal context when campaign date changes
  React.useEffect(() => {
    try {
      const date = formData.campaign_date ? new Date(formData.campaign_date) : new Date();
      const context = generateSeasonalContext(date);
      setSeasonalContext(context);
    } catch (error) {
      console.error("Error generating seasonal context:", error);
      setSeasonalContext(null);
    }
  }, [formData.campaign_date]);

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

  const handleCampaignDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const dateValue = e.target.value ? new Date(e.target.value) : new Date();
    setFormData((prev) => ({
      ...prev,
      campaign_date: dateValue
    }));
  };

  const handleDatePresetClick = (date: Date) => {
    setFormData((prev) => ({
      ...prev,
      campaign_date: date
    }));
    setShowDatePresets(false);
  };

  const handleTemplateSelect = (template: PromptTemplate, generatedPrompt: string) => {
    setSelectedTemplate(template);
    
    // Update the campaign_brief field with the generated prompt
    setFormData((prev) => ({
      ...prev,
      campaign_brief: generatedPrompt,
      description: generatedPrompt // Also update legacy field for backward compatibility
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

          {/* Visual Storytelling Approach - Strategic decision before templates */}
          <div className="space-y-3 p-4 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 rounded-xl border border-purple-200 dark:border-purple-800">
            <div className="flex items-center space-x-2 mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-purple-600 dark:text-purple-400">
                <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
                <path d="M12 9v4"></path>
                <path d="M12 17h.01"></path>
              </svg>
              <h3 className="text-sm font-semibold text-purple-900 dark:text-purple-100">
                🎬 Visual Storytelling Approach
              </h3>
            </div>
            <p className="text-xs text-purple-700 dark:text-purple-300 mb-3">
              How should your visuals communicate your message?
            </p>
            
            <div className="space-y-2">
              {/* Story-Led Option */}
              <div
                onClick={() => setFormData(prev => ({ ...prev, creative_approach: "story_led" }))}
                className={`flex items-start space-x-3 p-3 rounded-lg border transition-all cursor-pointer ${
                  formData.creative_approach === "story_led"
                    ? "bg-purple-50 border-purple-300 dark:bg-purple-950/20 dark:border-purple-600"
                    : "border-gray-200 hover:border-purple-200 dark:border-gray-700 dark:hover:border-purple-600"
                }`}
              >
                <input
                  type="radio"
                  name="creative_approach"
                  value="story_led"
                  checked={formData.creative_approach === "story_led"}
                  onChange={(e) => setFormData(prev => ({ ...prev, creative_approach: e.target.value as any }))}
                  className="mt-1 h-4 w-4 text-purple-600 focus:ring-purple-500"
                />
                <div className="flex-1 space-y-1">
                  <label className="flex items-center gap-2 cursor-pointer font-medium text-sm">
                    <span className="text-base">📖</span>
                    {t.creation?.idea?.form?.storytelling_story_led || "Story-Led"}
                  </label>
                  <p className="text-xs text-muted-foreground">
                    {t.creation?.idea?.form?.storytelling_story_led_desc || "Show people in situations, tell stories through scenes"}
                  </p>
                </div>
              </div>
              
              {/* Concept-Led Option */}
              <div
                onClick={() => setFormData(prev => ({ ...prev, creative_approach: "concept_led" }))}
                className={`flex items-start space-x-3 p-3 rounded-lg border transition-all cursor-pointer ${
                  formData.creative_approach === "concept_led"
                    ? "bg-purple-50 border-purple-300 dark:bg-purple-950/20 dark:border-purple-600"
                    : "border-gray-200 hover:border-purple-200 dark:border-gray-700 dark:hover:border-purple-600"
                }`}
              >
                <input
                  type="radio"
                  name="creative_approach"
                  value="concept_led"
                  checked={formData.creative_approach === "concept_led"}
                  onChange={(e) => setFormData(prev => ({ ...prev, creative_approach: e.target.value as any }))}
                  className="mt-1 h-4 w-4 text-purple-600 focus:ring-purple-500"
                />
                <div className="flex-1 space-y-1">
                  <label className="flex items-center gap-2 cursor-pointer font-medium text-sm">
                    <span className="text-base">💡</span>
                    {t.creation?.idea?.form?.storytelling_concept_led || "Concept-Led"}
                  </label>
                  <p className="text-xs text-muted-foreground">
                    {t.creation?.idea?.form?.storytelling_concept_led_desc || "Show ideas through imagery, symbols, and clear visuals"}
                  </p>
                </div>
              </div>
              
              {/* Hybrid Option (Default) */}
              <div
                onClick={() => setFormData(prev => ({ ...prev, creative_approach: "hybrid" }))}
                className={`flex items-start space-x-3 p-3 rounded-lg border transition-all cursor-pointer ${
                  (formData.creative_approach === "hybrid" || !formData.creative_approach)
                    ? "bg-purple-50 border-purple-300 dark:bg-purple-950/20 dark:border-purple-600"
                    : "border-gray-200 hover:border-purple-200 dark:border-gray-700 dark:hover:border-purple-600"
                }`}
              >
                <input
                  type="radio"
                  name="creative_approach"
                  value="hybrid"
                  checked={formData.creative_approach === "hybrid" || !formData.creative_approach}
                  onChange={(e) => setFormData(prev => ({ ...prev, creative_approach: e.target.value as any }))}
                  className="mt-1 h-4 w-4 text-purple-600 focus:ring-purple-500"
                />
                <div className="flex-1 space-y-1">
                  <label className="flex items-center gap-2 cursor-pointer font-medium text-sm">
                    <span className="text-base">⚖️</span>
                    {t.creation?.idea?.form?.storytelling_hybrid || "Hybrid"} 
                    <span className="ml-2 px-2 py-0.5 text-xs bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-full">
                      Recommended
                    </span>
                  </label>
                  <p className="text-xs text-muted-foreground">
                    {t.creation?.idea?.form?.storytelling_hybrid_desc || "Mix both approaches as needed based on context"}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Prompt Template Selector - Positioned after Storytelling Approach */}
          <div className="space-y-3 p-4 bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 rounded-xl border border-blue-200 dark:border-blue-800">
            <div className="flex items-center space-x-2 mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600 dark:text-blue-400">
                <path d="M12 20h9"></path>
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
              </svg>
              <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100">
                💡 Professional Templates
              </h3>
            </div>
            <p className="text-xs text-blue-700 dark:text-blue-300 mb-3">
              Templates will incorporate your audience and objective from above for better results
              <span className="block mt-1 font-mono text-xs bg-yellow-100 px-2 py-1 rounded">
                DEBUG: creative_approach = "{formData.creative_approach || 'undefined'}"
              </span>
            </p>
            <PromptTemplateSelector
              context={{
                title: formData.title || "[Product/Service Name]",
                targetAudience: formData.target_audience,
                campaignObjective: formData.campaign_objective,
                keywords: formData.keywords
              }}
              onSelect={handleTemplateSelect}
              selectedTemplateId={selectedTemplate?.id}
              translations={t}
              creativeApproach={formData.creative_approach}
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

          {/* Campaign Date Field */}
          <div className="space-y-3 pt-4 border-t">
            <Label htmlFor="campaign_date" className="text-sm font-medium flex items-center space-x-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-accent">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              <span>{t.creation?.idea?.form?.campaign_date || "Campaign Date"}</span>
            </Label>
            <p className="text-xs text-muted-foreground -mt-1">
              {t.creation?.idea?.form?.campaign_date_hint || "When will this campaign run? This helps generate seasonally appropriate content."}
            </p>
            
            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowDatePresets(!showDatePresets)}
                className="w-auto btn-scale"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2">
                  <path d="M21 10H3"></path>
                  <path d="M21 6H3"></path>
                  <path d="M21 14H3"></path>
                  <path d="M21 18H3"></path>
                </svg>
                {t.creation?.idea?.form?.quick_dates || "Quick Dates"}
              </Button>
              
              <Input
                type="date"
                id="campaign_date"
                name="campaign_date"
                value={formData.campaign_date ? new Date(formData.campaign_date).toISOString().split('T')[0] : ''}
                onChange={handleCampaignDateChange}
                className="flex-1 focus:border-primary transition-all"
              />
              
              <Button
                type="button"
                variant="ghost"
                onClick={() => setFormData(prev => ({ ...prev, campaign_date: new Date() }))}
                className="btn-scale"
                title={t.creation?.idea?.form?.use_today || "Use Today"}
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
              </Button>
            </div>
            
            {/* Date Presets Grid */}
            {showDatePresets && (
              <div className="grid grid-cols-2 gap-2 p-3 border rounded-lg bg-card shadow-sm animate-in fade-in-50 duration-200">
                {Object.entries(datePresets).map(([key, preset]) => (
                  <Button
                    key={key}
                    type="button"
                    variant="ghost"
                    onClick={() => handleDatePresetClick(preset.date)}
                    className="justify-start hover:bg-accent/50 transition-all"
                  >
                    <span className="text-sm">{preset.label}</span>
                    <span className="ml-auto text-xs text-muted-foreground">
                      {preset.date.toLocaleDateString(locale, { month: 'short', day: 'numeric' })}
                    </span>
                  </Button>
                ))}
              </div>
            )}
            
            {/* Seasonal Context Preview */}
            {seasonalContext && (
              <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30 rounded-lg border border-blue-200 dark:border-blue-800 space-y-2 animate-in fade-in-50 duration-300">
                <div className="flex items-center space-x-2 text-sm font-semibold text-blue-900 dark:text-blue-100">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 2v1"></path>
                    <path d="m18 6-1 1"></path>
                    <path d="M22 12h-1"></path>
                    <path d="m18 18-1-1"></path>
                    <path d="M12 21v1"></path>
                    <path d="m6 18 1-1"></path>
                    <path d="M2 12h1"></path>
                    <path d="m6 6 1 1"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                  <span>{t.creation?.idea?.form?.seasonal_context || "Seasonal Context"}</span>
                </div>
                <p className="text-xs text-blue-800 dark:text-blue-200">
                  {t.creation?.idea?.form?.seasonal_preview || "Based on your selected date, we'll generate content for"}:
                </p>
                <div className="grid grid-cols-2 gap-3 mt-2">
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-blue-900 dark:text-blue-100">
                      {t.creation?.idea?.seasonal_info?.season || "Season"}
                    </p>
                    <p className="text-sm text-blue-700 dark:text-blue-300">{seasonalContext.season} ({seasonalContext.monthName})</p>
                  </div>
                  {seasonalContext.holidays.length > 0 && (
                    <div className="space-y-1">
                      <p className="text-xs font-medium text-blue-900 dark:text-blue-100">Holidays</p>
                      <p className="text-sm text-blue-700 dark:text-blue-300">{seasonalContext.holidays.join(", ")}</p>
                    </div>
                  )}
                  <div className="space-y-1 col-span-2">
                    <p className="text-xs font-medium text-blue-900 dark:text-blue-100">
                      {t.creation?.idea?.seasonal_info?.themes || "Suggested Themes"}
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {seasonalContext.themes.slice(0, 6).map((theme, idx) => (
                        <span key={idx} className="inline-block px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200 rounded-full">
                          {theme}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="space-y-1 col-span-2">
                    <p className="text-xs font-medium text-blue-900 dark:text-blue-100">
                      {t.creation?.idea?.seasonal_info?.colors || "Seasonal Colors"}
                    </p>
                    <div className="flex gap-2">
                      {seasonalContext.colors.map((color, idx) => (
                        <div
                          key={idx}
                          className="w-8 h-8 rounded-md border-2 border-white dark:border-gray-700 shadow-sm"
                          style={{ backgroundColor: color }}
                          title={color}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Campaign Brief - Moved to bottom for real-time visibility of enrichments */}
          <div className="space-y-2 pt-6 border-t-2 border-dashed border-gray-300 dark:border-gray-700">
            <div className="flex items-center justify-between mb-3">
              <Label htmlFor="campaign_brief" className="text-sm font-medium flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-green-600 dark:text-green-400">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                <span>{t.creation.idea.form.campaign_brief}</span>
                {selectedTemplate && (
                  <span className="ml-2 px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full">
                    Using: {selectedTemplate.name}
                  </span>
                )}
              </Label>
              <span className="px-3 py-1 text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded-full border border-green-200 dark:border-green-800">
                ✨ Auto-Enriched
              </span>
            </div>
            <Textarea
              id="campaign_brief"
              name="campaign_brief"
              placeholder={t.creation.idea.form.campaign_brief_placeholder}
              value={formData.campaign_brief}
              onChange={handleChange}
              rows={6}
              className="focus:border-green-500 transition-all resize-none bg-green-50/30 dark:bg-green-950/10"
            />
            <p className="text-xs text-green-600 dark:text-green-400 mt-1 flex items-start space-x-1">
              <span>💡</span>
              <span>{t.creation.idea.form.campaign_brief_hint}</span>
            </p>
          </div>
        </CardContent>        <CardFooter className="flex justify-between items-center border-t pt-6">
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
