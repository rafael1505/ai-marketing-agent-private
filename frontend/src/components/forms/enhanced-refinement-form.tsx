"use client";

import React from "react";
import Image from "next/image";
import { getTranslations } from "@/i18n";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { RefinementFormData, GeneratedImage, Material } from "@/types";
import { Loader } from "@/components/ui/loader";
import { ContextEnrichmentDisplay } from "@/components/ui/context-enrichment-display";
import { PeoplePreferenceSelector } from "@/components/ui/people-preference-selector";
import { PhaseStrategyContext } from "@/components/ui/phase-strategy-context";
import { PromptTemplateSelector } from "@/components/ui/prompt-template-selector";
import { PROMPT_TEMPLATES, type PromptTemplate } from "@/data/prompt-templates";
import { INDUSTRY_TEMPLATES, enrichPromptWithIndustry } from "@/data/industry-templates";
import { getDatePresets } from "@/lib/seasonal-context";
import { generateSeasonalContext, enrichPromptWithSeasonalContext, SeasonalContext } from "@/lib/seasonal-context";
import { enrichPromptWithMaterialContext } from "@/lib/material-context";
import { generateVisualPromptFromCampaign } from "@/lib/visual-prompt-generator";

interface RefinementFormProps {
  onSubmit: (data: RefinementFormData) => void;
  onGenerateImage: (prompt: string, provider: string, batchSize?: number, peoplePreference?: string) => Promise<void>; // Phase 2: Added batch size, Phase 9: Added peoplePreference (4-mode system)
  aiProviders: any[]; // Updated to use the new AI provider format
  generatedImages: GeneratedImage[];
  initialData?: Partial<RefinementFormData>;
  material?: Material | null; // Material data including campaign_date for seasonal context
  locale?: string;
}

export const EnhancedRefinementForm: React.FC<RefinementFormProps> = ({
  onSubmit,
  onGenerateImage,
  aiProviders,
  generatedImages,
  initialData = {},
  material = null,
  locale = "en"
}) => {
  const [t, setT] = React.useState<Record<string, any>>({});
  const [formData, setFormData] = React.useState<RefinementFormData>({
    prompt: initialData.prompt || "", // Will be auto-generated from campaign data
    aiProvider: initialData.aiProvider || "",
    generationParams: initialData.generationParams || {},
    peoplePreference: initialData.peoplePreference || "auto", // Smart 4-mode system (default: auto)
  });
  
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [selectedProvider, setSelectedProvider] = React.useState<any | null>(null);
  const [providerError, setProviderError] = React.useState<string>("");
  const [selectedImageIndex, setSelectedImageIndex] = React.useState<number | null>(null);
  const [progressMessage, setProgressMessage] = React.useState<string>("");
  const [elapsedSeconds, setElapsedSeconds] = React.useState<number>(0);
  
  // Context enrichment state
  const [selectedIndustry, setSelectedIndustry] = React.useState<string | null>(null);
  const [seasonalContext, setSeasonalContext] = React.useState<SeasonalContext | null>(null);
  const [showEnrichmentOptions, setShowEnrichmentOptions] = React.useState(true);
  
  // Batch generation state (Phase 2)
  const [batchSize, setBatchSize] = React.useState<number>(3); // Default: 3 images
  const [batchProgress, setBatchProgress] = React.useState<Array<{status: string, imageUrl?: string}>>([]);

  // Phase 1 fields moved to Phase 2 (UX Restructuring)
  const [creativeApproach, setCreativeApproach] = React.useState<"story_led" | "concept_led" | "hybrid">(
    material?.creative_approach || "hybrid"
  );
  const [campaignDate, setCampaignDate] = React.useState<Date>(
    material?.campaign_date ? new Date(material.campaign_date) : new Date()
  );
  const [selectedTemplate, setSelectedTemplate] = React.useState<any | null>(null);
  const [showDatePresets, setShowDatePresets] = React.useState(false);

  // Initialize seasonal context after component mounts (client-side only)
  // Use material's campaign_date if available, otherwise use current date
  React.useEffect(() => {
    try {
      const targetDate = material?.campaign_date ? new Date(material.campaign_date) : new Date();
      const context = generateSeasonalContext(targetDate);
      setSeasonalContext(context);
      console.log("Initialized seasonal context for date:", targetDate, context);
    } catch (error) {
      console.error("Error getting seasonal context:", error);
      setSeasonalContext(null);
    }
  }, [material?.campaign_date]);

  // Auto-select people preference based on creative approach from Phase 1
  React.useEffect(() => {
    if (material?.creative_approach && !initialData.peoplePreference) {
      let defaultPreference: string = "auto";
      
      if (material.creative_approach === "story_led") {
        defaultPreference = "include"; // Story-Led → Show people
        console.log("Auto-selected 'include' people preference based on Story-Led approach");
      } else if (material.creative_approach === "concept_led") {
        defaultPreference = "exclude"; // Concept-Led → Focus on concepts without people
        console.log("Auto-selected 'exclude' people preference based on Concept-Led approach");
      } else {
        // hybrid or undefined → use auto (let context decide)
        defaultPreference = "auto";
        console.log("Using 'auto' people preference for Hybrid approach");
      }
      
      setFormData(prev => ({ 
        ...prev, 
        peoplePreference: defaultPreference as any 
      }));
    }
  }, [material?.creative_approach, initialData.peoplePreference]);

  React.useEffect(() => {
    const loadTranslations = async () => {
      try {
        const translations = await getTranslations(locale === "pt" ? "pt" : "en");
        setT(translations);
      } catch (error) {
        console.error("Error loading translations:", error);
        setT({
          creation: {
            refinement: {
              title: "Content Refinement & Image Generation",
              description: "Generate professional marketing images using AI",
              form: {
                prompt: "Image Description",
                prompt_placeholder: "Describe the marketing image you want to create",
                ai_provider: "AI Provider",
                select_provider: "Select an AI Provider",
                generate_image: "Generate Image",
                generating: "Generating...",
                generated_images: "Generated Images",
                save: "Continue to Finalization",
                saving: "Saving...",
                no_providers: "No AI providers configured",
                configure_providers: "Configure AI Providers"
              }
            }
          }
        });
      }
    };
    loadTranslations();
  }, [locale]);

  // Auto-generate visual direction prompt from campaign strategy data
  React.useEffect(() => {
    // Only generate if:
    // 1. We have material data (campaign strategy from Phase 1)
    // 2. The prompt is empty (not edited by user yet)
    // 3. This is not initial data from a saved/resumed session
    if (material && !initialData.prompt && !formData.prompt) {
      try {
        const generatedPrompt = generateVisualPromptFromCampaign(material, t);
        setFormData(prev => ({ 
          ...prev, 
          prompt: generatedPrompt 
        }));
        console.log("Auto-generated visual direction prompt from campaign data");
      } catch (error) {
        console.error("Error generating visual prompt:", error);
      }
    }
  }, [material, t, initialData.prompt]); // Re-generate only if material or translations change

  // Update form data when provider changes
  React.useEffect(() => {
    if (selectedProvider) {
      setFormData(prev => ({ ...prev, aiProvider: selectedProvider.id }));
      setProviderError("");
    }
  }, [selectedProvider]);

  const configuredProviders = React.useMemo(() => {
    // Use the providers passed from parent (which are already filtered for active/configured)
    return aiProviders.length > 0 ? aiProviders : [];
  }, [aiProviders]);

  // Auto-select the first provider if no provider is selected
  React.useEffect(() => {
    if (configuredProviders.length > 0 && !selectedProvider) {
      // Select the first available provider
      const defaultProvider = configuredProviders[0];
      setSelectedProvider(defaultProvider);
    }
  }, [configuredProviders, selectedProvider]);

  // Keyboard navigation for image modal
  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (selectedImageIndex === null) return;

      switch (event.key) {
        case 'Escape':
          event.preventDefault();
          event.stopPropagation(); // Prevent event from bubbling to parent elements
          setSelectedImageIndex(null);
          break;
        case 'ArrowLeft':
          event.preventDefault();
          event.stopPropagation(); // Prevent event from bubbling to form/stepper
          setSelectedImageIndex(
            selectedImageIndex > 0 ? selectedImageIndex - 1 : generatedImages.length - 1
          );
          break;
        case 'ArrowRight':
          event.preventDefault();
          event.stopPropagation(); // Prevent event from bubbling to form/stepper
          setSelectedImageIndex(
            selectedImageIndex < generatedImages.length - 1 ? selectedImageIndex + 1 : 0
          );
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [selectedImageIndex, generatedImages.length]);

  const handleProviderSelect = (providerId: string) => {
    const provider = configuredProviders.find(p => p.id === providerId);
    if (provider) {
      setSelectedProvider(provider);
      setProviderError("");
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Enhanced refinement form submitted with data:", formData);
    setIsSubmitting(true);

    try {
      // Merge Phase 2 formData with Phase 1 fields (moved to Phase 2)
      const enrichedFormData = {
        ...formData,
        creative_approach: creativeApproach,
        campaign_date: campaignDate,
      };
      
      console.log("Submitting enriched form data:", enrichedFormData);
      await onSubmit(enrichedFormData);
    } catch (error) {
      console.error("Error submitting refinement form:", error);
      setIsSubmitting(false);
    }
  };

  const handleGenerateImage = async () => {
    if (!formData.prompt) {
      setProviderError(t.creation?.refinement?.form?.error_no_description || "Please enter an image description");
      return;
    }
    
    if (!formData.aiProvider || !selectedProvider) {
      setProviderError(t.creation?.refinement?.form?.error_no_provider || "Please select an AI provider");
      return;
    }
    
    setIsGenerating(true);
    setProviderError("");
    setElapsedSeconds(0);
    setProgressMessage("");
    
    // Start progress tracking - update every 10 seconds
    const startTime = Date.now();
    const progressInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      setElapsedSeconds(elapsed);
      
      // Provider-specific time estimates (Phase 2: adjusted for batch size)
      const providerEstimates: Record<string, number> = {
        'openai': 25,      // DALL-E 3: ~25s per image
        'stability': 15,   // Stability AI: ~15s per image
        'replicate': 20,   // Replicate: ~20s per image
        'huggingface': 30, // HuggingFace: ~30s per image
      };
      const timePerImage = providerEstimates[formData.aiProvider.toLowerCase()] || 20;
      const estimatedTime = timePerImage * batchSize;
      
      if (elapsed >= 10 && elapsed < estimatedTime) {
        setProgressMessage(
          `Still generating... ${elapsed}s elapsed. ${selectedProvider.name} can take up to ${estimatedTime}s for ${batchSize} images.`
        );
      }
    }, 10000); // Update every 10 seconds
    
    try {
      // Enrich the prompt with all available context (order matters!)
      let enrichedPrompt = formData.prompt;
      
      // 1. First, add material context (title, description, target_audience, campaign_objective, keywords)
      //    This provides the foundation - what the campaign is about
      enrichedPrompt = enrichPromptWithMaterialContext(enrichedPrompt, material);
      console.log("✓ Applied material context (title, description, audience, objective, keywords)");
      
      // 2. Apply industry context if selected
      //    This adds industry-specific guidelines and best practices
      if (selectedIndustry) {
        enrichedPrompt = enrichPromptWithIndustry(enrichedPrompt, selectedIndustry, t);
        console.log("✓ Applied industry context:", selectedIndustry);
      }
      
      // 3. Apply seasonal context based on material's campaign date
      //    This adds seasonally appropriate themes, colors, and keywords
      const campaignDate = material?.campaign_date ? new Date(material.campaign_date) : new Date();
      enrichedPrompt = enrichPromptWithSeasonalContext(enrichedPrompt, campaignDate);
      console.log("✓ Applied seasonal context for date:", campaignDate.toLocaleDateString());
      
      console.log("Starting image generation with fully enriched prompt:", { 
        original: formData.prompt,
        enriched: enrichedPrompt,
        materialTitle: material?.title,
        hasDescription: !!material?.description,
        hasAudience: !!material?.target_audience,
        hasObjective: !!material?.campaign_objective,
        keywordsCount: material?.keywords?.length || 0,
        industry: selectedIndustry || "none",
        campaignDate: campaignDate.toLocaleDateString(),
        provider: formData.aiProvider,
        batchSize: batchSize 
      });
      
      // Phase 2: Pass batch size to parent component
      // Phase 9: Pass peoplePreference (4-mode system) to control people in images
      await onGenerateImage(enrichedPrompt, formData.aiProvider, batchSize, formData.peoplePreference);
      console.log(`Batch generation completed successfully: ${batchSize} images (peoplePreference: ${formData.peoplePreference})`);
      setProgressMessage(""); // Clear progress message on success
    } catch (error) {
      console.error("Error generating image:", error);
      const errorMessage = error instanceof Error ? error.message : (t.creation?.refinement?.form?.error_generate_failed || "Failed to generate image. Please try again.");
      setProviderError(errorMessage);
      
      // Parent component (create/edit page) handles error display with AIErrorDisplay
      // No need for browser alert() here
    } finally {
      clearInterval(progressInterval);
      setIsGenerating(false);
      setProgressMessage("");
      setElapsedSeconds(0);
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
    <div className="space-y-6">
      {/* AI Provider Selection */}
      <Card className="border-l-4 border-l-blue-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600">
                <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2"/>
                <path d="M14.5 4.5c-1.8.7-3 2.5-3 4.5 0 0-2 0-2 2 0 2 2 2 2 2"/>
                <path d="M14.5 4.5A4 4 0 1 1 18 9"/>
              </svg>
            </div>
            {t.creation.refinement.form.select_provider}
          </CardTitle>
          <CardDescription>
            {t.creation?.refinement?.form?.provider_description || "Choose an AI provider to generate marketing images. Each provider offers different capabilities and pricing."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {configuredProviders.length === 0 ? (
            <Alert>
              <AlertDescription>
                {t.creation.refinement.form.no_providers}. Please configure at least one AI provider to continue.
              </AlertDescription>
            </Alert>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {configuredProviders.map((provider) => (
                <Card 
                  key={provider.id}
                  className={`cursor-pointer transition-all duration-200 ${
                    selectedProvider?.id === provider.id 
                      ? 'ring-2 ring-blue-500 border-blue-500' 
                      : 'hover:shadow-md'
                  }`}
                  onClick={() => handleProviderSelect(provider.id)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base">{provider.name}</CardTitle>
                      <Badge 
                        variant={provider.pricing?.tier === 'free' ? 'default' : 'secondary'}
                        className="capitalize"
                      >
                        {provider.pricing?.tier || 'free'}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="space-y-2">
                      {provider.marketingCapabilities?.imageGeneration && (
                        <Badge variant="outline" className="text-xs">Image Generation</Badge>
                      )}
                      {provider.marketingCapabilities?.logoDesign && (
                        <Badge variant="outline" className="text-xs">Logo Design</Badge>
                      )}
                      
                      {/* Safe null check for pricing and freeQuota */}
                      {provider.pricing && provider.pricing.freeQuota && (
                        <p className="text-xs text-muted-foreground">
                          {provider.pricing.freeQuota.description}
                        </p>
                      )}
                    </div>
                    
                    <Button 
                      type="button"
                      variant={selectedProvider?.id === provider.id ? "default" : "outline"}
                      size="sm"
                      className="w-full mt-3"
                    >
                      {selectedProvider?.id === provider.id ? 'Selected' : 'Select'}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Image Generation Form */}
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
            {/* Phase 1 Strategy Context - Read-only summary */}
            <PhaseStrategyContext material={material} translations={t} />

            {/* ========== EXECUTION FIELDS (Moved from Phase 1) ========== */}

            {/* Creative Approach */}
            <div className="space-y-3 p-4 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 rounded-xl border border-purple-200 dark:border-purple-800">
              <div className="flex items-center space-x-2 mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-purple-600 dark:text-purple-400">
                  <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
                  <path d="M12 9v4"></path>
                  <path d="M12 17h.01"></path>
                </svg>
                <h3 className="text-sm font-semibold text-purple-900 dark:text-purple-100">
                  🎬 {t.creation?.refinement?.form?.creative_approach || "Visual Storytelling Approach"}
                </h3>
              </div>
              <p className="text-xs text-purple-700 dark:text-purple-300 mb-3">
                {t.creation?.refinement?.form?.creative_approach_hint || "How should your visuals communicate your message?"}
              </p>
              
              <div className="space-y-2">
                {/* Story-Led Option */}
                <div
                  onClick={() => setCreativeApproach("story_led")}
                  className={`flex items-start space-x-3 p-3 rounded-lg border transition-all cursor-pointer ${
                    creativeApproach === "story_led"
                      ? "bg-purple-50 border-purple-300 dark:bg-purple-950/20 dark:border-purple-600"
                      : "border-gray-200 hover:border-purple-200 dark:border-gray-700 dark:hover:border-purple-600"
                  }`}
                >
                  <input
                    type="radio"
                    name="creative_approach"
                    value="story_led"
                    checked={creativeApproach === "story_led"}
                    onChange={(e) => setCreativeApproach(e.target.value as any)}
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
                  onClick={() => setCreativeApproach("concept_led")}
                  className={`flex items-start space-x-3 p-3 rounded-lg border transition-all cursor-pointer ${
                    creativeApproach === "concept_led"
                      ? "bg-purple-50 border-purple-300 dark:bg-purple-950/20 dark:border-purple-600"
                      : "border-gray-200 hover:border-purple-200 dark:border-gray-700 dark:hover:border-purple-600"
                  }`}
                >
                  <input
                    type="radio"
                    name="creative_approach"
                    value="concept_led"
                    checked={creativeApproach === "concept_led"}
                    onChange={(e) => setCreativeApproach(e.target.value as any)}
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
                  onClick={() => setCreativeApproach("hybrid")}
                  className={`flex items-start space-x-3 p-3 rounded-lg border transition-all cursor-pointer ${
                    creativeApproach === "hybrid"
                      ? "bg-purple-50 border-purple-300 dark:bg-purple-950/20 dark:border-purple-600"
                      : "border-gray-200 hover:border-purple-200 dark:border-gray-700 dark:hover:border-purple-600"
                  }`}
                >
                  <input
                    type="radio"
                    name="creative_approach"
                    value="hybrid"
                    checked={creativeApproach === "hybrid"}
                    onChange={(e) => setCreativeApproach(e.target.value as any)}
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

            {/* Template Selector */}
            <div className="space-y-3 p-4 bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 rounded-xl border border-blue-200 dark:border-blue-800">
              <div className="flex items-center space-x-2 mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600 dark:text-blue-400">
                  <path d="M12 20h9"></path>
                  <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
                </svg>
                <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100">
                  💡 {t.creation?.refinement?.form?.professional_templates || "Professional Templates"}
                </h3>
              </div>
              <p className="text-xs text-blue-700 dark:text-blue-300 mb-3">
                {t.creation?.refinement?.form?.templates_hint || "Templates will incorporate your audience and objective for better results"}
              </p>
              <PromptTemplateSelector
                context={{
                  title: material?.title || "[Product/Service Name]",
                  targetAudience: material?.target_audience,
                  campaignObjective: material?.campaign_objective,
                  keywords: material?.keywords || []
                }}
                onSelect={(template: PromptTemplate, generatedPrompt: string) => {
                  setSelectedTemplate(template);
                  // Update the Visual Direction Prompt (formData.prompt) with the generated prompt
                  setFormData(prev => ({ ...prev, prompt: generatedPrompt }));
                }}
                selectedTemplateId={selectedTemplate?.id}
                translations={t}
                creativeApproach={creativeApproach}
              />
            </div>

            {/* Campaign Date */}
            <div className="space-y-3 p-4 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/20 dark:to-orange-950/20 rounded-xl border border-amber-200 dark:border-amber-800">
              <Label htmlFor="campaign_date" className="text-sm font-medium flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-amber-600 dark:text-amber-400">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="16" y1="2" x2="16" y2="6"></line>
                  <line x1="8" y1="2" x2="8" y2="6"></line>
                  <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
                <span>{t.creation?.idea?.form?.campaign_date || "Campaign Date"}</span>
              </Label>
              <p className="text-xs text-amber-700 dark:text-amber-300 -mt-1 mb-2">
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
                  value={campaignDate ? new Date(campaignDate).toISOString().split('T')[0] : ''}
                  onChange={(e) => {
                    const dateValue = e.target.value ? new Date(e.target.value) : new Date();
                    setCampaignDate(dateValue);
                    // Update seasonal context
                    try {
                      const context = generateSeasonalContext(dateValue);
                      setSeasonalContext(context);
                    } catch (error) {
                      console.error("Error updating seasonal context:", error);
                    }
                  }}
                  className="flex-1 focus:border-primary transition-all"
                />
                
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => {
                    const today = new Date();
                    setCampaignDate(today);
                    try {
                      const context = generateSeasonalContext(today);
                      setSeasonalContext(context);
                    } catch (error) {
                      console.error("Error updating seasonal context:", error);
                    }
                  }}
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
                  {Object.entries(getDatePresets()).map(([key, preset]: [string, any]) => (
                    <Button
                      key={key}
                      type="button"
                      variant="ghost"
                      onClick={() => {
                        setCampaignDate(preset.date);
                        setShowDatePresets(false);
                        try {
                          const context = generateSeasonalContext(preset.date);
                          setSeasonalContext(context);
                        } catch (error) {
                          console.error("Error updating seasonal context:", error);
                        }
                      }}
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
                <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30 rounded-lg border border-blue-200 dark:border-blue-800 space-y-2 animate-in fade-in-50 duration-300 mt-3">
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

            {/* ========== END OF EXECUTION FIELDS ========== */}

            {/* Selected Provider Info */}
            {selectedProvider && (
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-blue-900">
                      {(t.creation?.refinement?.form?.provider_selected || "Selected: {provider}").replace("{provider}", selectedProvider.name)}
                    </h4>
                    <p className="text-sm text-blue-700">
                      {selectedProvider.marketingCapabilities?.imageGeneration 
                        ? (t.creation?.refinement?.form?.provider_ready || 'Ready for image generation')
                        : (t.creation?.refinement?.form?.provider_limited || 'Limited capabilities')}
                    </p>
                  </div>
                  <Badge variant="default" className="bg-blue-500">
                    {selectedProvider.pricing?.tier || 'free'}
                  </Badge>
                </div>
              </div>
            )}

            {/* Batch Settings (Phase 2) */}
            <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600 dark:text-blue-400">
                    <rect width="7" height="7" x="3" y="3" rx="1"/>
                    <rect width="7" height="7" x="14" y="3" rx="1"/>
                    <rect width="7" height="7" x="14" y="14" rx="1"/>
                    <rect width="7" height="7" x="3" y="14" rx="1"/>
                  </svg>
                  <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100">
                    {t.creation?.refinement?.form?.batch_settings || "Batch Settings"}
                  </h3>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="batchSize" className="text-sm font-medium text-blue-900 dark:text-blue-100">
                  {t.creation?.refinement?.form?.image_count || "Number of Images"}
                </Label>
                <p className="text-xs text-blue-700 dark:text-blue-300 mb-2">
                  {t.creation?.refinement?.form?.image_count_description || "Generate multiple variations simultaneously"}
                </p>
                <div className="flex gap-2">
                  {[3, 5, 10].map((size) => (
                    <button
                      key={size}
                      type="button"
                      onClick={() => setBatchSize(size)}
                      className={`flex-1 px-4 py-2 rounded-lg border-2 transition-all font-medium ${
                        batchSize === size
                          ? 'border-blue-500 bg-blue-500 text-white shadow-md'
                          : 'border-blue-200 dark:border-blue-700 bg-white dark:bg-blue-900/20 text-blue-900 dark:text-blue-100 hover:border-blue-400 dark:hover:border-blue-500'
                      }`}
                    >
                      {size} {size === 1 ? 'image' : 'images'}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Context Enrichment Options */}
            {showEnrichmentOptions && (
              <div className="space-y-4 p-4 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 rounded-xl border border-purple-200 dark:border-purple-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-purple-600 dark:text-purple-400">
                      <circle cx="12" cy="12" r="10"></circle>
                      <path d="M12 16v-4"></path>
                      <path d="M12 8h.01"></path>
                    </svg>
                    <h3 className="text-sm font-semibold text-purple-900 dark:text-purple-100">
                      ✨ {t.enrichment?.ui?.enrich_your_prompt || "Enrich Your Prompt"}
                    </h3>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShowEnrichmentOptions(false)}
                    className="text-purple-600 hover:text-purple-800 dark:text-purple-400 dark:hover:text-purple-200 transition-colors"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </button>
                </div>

                {/* Industry Selection */}
                <div className="space-y-2">
                  <Label className="text-xs font-medium text-purple-800 dark:text-purple-200">
                    🏢 {t.enrichment?.ui?.select_industry || "Select Industry"}
                  </Label>
                  <select
                    value={selectedIndustry || ''}
                    onChange={(e) => setSelectedIndustry(e.target.value || null)}
                    className="w-full px-3 py-2 text-sm border border-purple-200 dark:border-purple-800 rounded-lg bg-white dark:bg-gray-900 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  >
                    <option value="">{t.enrichment?.ui?.all_industries || "All Industries"}</option>
                    {Object.keys(INDUSTRY_TEMPLATES).map((industry) => (
                      <option key={industry} value={industry}>
                        {industry.charAt(0).toUpperCase() + industry.slice(1)}
                      </option>
                    ))}
                  </select>
                  {selectedIndustry && (
                    <p className="text-xs text-purple-700 dark:text-purple-300">
                      {`${t.enrichment?.ui?.apply || "Apply"} ${selectedIndustry} ${t.enrichment?.ui?.industry_guidelines || "industry guidelines"}`}
                    </p>
                  )}
                </div>

                {/* Material Context Summary - Shows what from Idea Phase will be used */}
                {material && (
                  <div className="mt-3 p-3 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 rounded-lg border border-green-200 dark:border-green-800">
                    <h4 className="text-xs font-semibold text-green-900 dark:text-green-100 mb-2">
                      📝 {t.enrichment?.ui?.material_context || "Campaign Context from Idea Phase"}
                    </h4>
                    <div className="space-y-1 text-xs text-green-800 dark:text-green-200">
                      {material.title && (
                        <p><span className="font-medium">Title:</span> {material.title}</p>
                      )}
                      {material.target_audience && (
                        <p><span className="font-medium">Audience:</span> {material.target_audience}</p>
                      )}
                      {material.campaign_objective && (
                        <p><span className="font-medium">Objective:</span> {material.campaign_objective}</p>
                      )}
                      {material.keywords && material.keywords.length > 0 && (
                        <p><span className="font-medium">Keywords:</span> {material.keywords.join(", ")}</p>
                      )}
                      <p className="text-xs text-green-600 dark:text-green-400 italic mt-2">
                        ✓ This campaign context will be automatically included in all image generations
                      </p>
                    </div>
                  </div>
                )}

                {/* Seasonal Context Display */}
                {seasonalContext && (
                  <div className="mt-3 p-3 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
                    <h4 className="text-xs font-semibold text-blue-900 dark:text-blue-100 mb-2">
                      🗓️ {t.forms?.seasonal_context || "Seasonal Context"}
                    </h4>
                    <div className="space-y-1 text-xs text-blue-800 dark:text-blue-200">
                      <p>
                        <span className="font-medium">{t.forms?.season || "Season"}:</span>{" "}
                        {seasonalContext.season} ({seasonalContext.monthName})
                      </p>
                      {seasonalContext.holidays.length > 0 && (
                        <p>
                          <span className="font-medium">🎉 Holidays:</span>{" "}
                          {seasonalContext.holidays.join(", ")}
                        </p>
                      )}
                      <p className="text-xs text-blue-600 dark:text-blue-400 italic mt-2">
                        ℹ️ Seasonal context will be automatically applied during image generation
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {!showEnrichmentOptions && (
              <button
                type="button"
                onClick={() => setShowEnrichmentOptions(true)}
                className="text-sm text-purple-600 hover:text-purple-800 dark:text-purple-400 dark:hover:text-purple-200 underline transition-colors"
              >
                Show enrichment options
              </button>
            )}

            {/* Smart People Preference Selector - 4-Mode System with Conflict Detection */}
            <PeoplePreferenceSelector
              value={formData.peoplePreference || "auto"}
              onChange={(newValue) => setFormData(prev => ({ ...prev, peoplePreference: newValue }))}
              industryId={selectedIndustry}
              material={material}
              seasonalContext={seasonalContext}
              translations={t}
            />

            {/* Visual Direction Prompt - Moved to bottom for real-time enrichment feedback */}
            <div className="space-y-2 p-4 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/20 dark:to-orange-950/20 rounded-xl border-2 border-amber-200 dark:border-amber-800">
              <div className="flex items-center justify-between mb-2">
                <Label htmlFor="prompt" className="text-sm font-semibold text-amber-900 dark:text-amber-100 flex items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-amber-600 dark:text-amber-400">
                    <path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"></path>
                    <path d="m15 5 4 4"></path>
                  </svg>
                  {t.creation?.refinement?.form?.prompt || "Visual Direction Prompt"}
                </Label>
                <Badge variant="secondary" className="bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
                  Final Prompt
                </Badge>
              </div>
              <p className="text-xs text-amber-700 dark:text-amber-300 mb-3">
                📝 This prompt was auto-generated and enriched with all your selections above. Review and refine before generating.
              </p>
              <Textarea
                id="prompt"
                name="prompt"
                placeholder={t.creation?.refinement?.form?.prompt_placeholder || "Describe the visual style, mood, colors, and composition you want"}
                value={formData.prompt}
                onChange={handleChange}
                rows={8}
                required
                className="focus:border-amber-500 transition-all resize-none bg-white dark:bg-gray-900"
              />
              <div className="space-y-1 mt-2">
                <p className="text-xs text-amber-600 dark:text-amber-400 flex items-start space-x-1">
                  <span>✨</span>
                  <span>{t.creation?.refinement?.form?.prompt_hint || "This prompt includes your campaign context, industry guidelines, seasonal themes, and people preferences."}</span>
                </p>
                <p className="text-xs text-muted-foreground flex items-start space-x-1">
                  <span>💡</span>
                  <span>{t.creation?.refinement?.form?.prompt_tip || "Be specific about visual style, mood, colors, composition, and key elements"}</span>
                </p>
              </div>
            </div>

            {/* Error Display */}
            {providerError && (
              <Alert variant="destructive">
                <AlertDescription>{providerError}</AlertDescription>
              </Alert>
            )}
            
            {/* Generate Button */}
            <div className="pt-4 space-y-3">
              <Button
                type="button"
                onClick={handleGenerateImage}
                disabled={isGenerating || !formData.prompt || !selectedProvider}
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
                    <span className="font-medium">
                      {batchSize > 1 
                        ? `Generate ${batchSize} Images` 
                        : (t.creation.refinement.form.generate_image || "Generate Image")}
                    </span>
                  </>
                )}
              </Button>
              
              {/* Progress Indicator */}
              {isGenerating && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 animate-pulse">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <svg className="w-5 h-5 text-blue-600 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-blue-900">
                        {t.creation?.refinement?.form?.processing || "Processing your request..."}
                        {elapsedSeconds > 0 && <span className="ml-2 text-blue-600">({elapsedSeconds}s)</span>}
                      </p>
                      <p className="text-xs text-blue-700 mt-1">
                        {progressMessage || ((t.creation?.refinement?.form?.generating_message || "Generating {count} AI images with {provider}. This may take {time} seconds depending on the provider.")
                          .replace("{count}", String(batchSize))
                          .replace("{provider}", selectedProvider?.name || "AI provider")
                          .replace("{time}", String(batchSize * 20) + "-" + String(batchSize * 30)))}
                      </p>
                      <div className="mt-2 flex items-center gap-2 text-xs text-blue-600">
                        <span>⏳</span>
                        <span>{t.creation?.refinement?.form?.please_wait || "Please wait while we create your images..."}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Generated Images Display */}
            {generatedImages.length > 0 && (
              <div className="space-y-3">
                <Label className="text-sm font-medium">{t.creation.refinement.form.generated_images || "Generated Images"}</Label>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                  {generatedImages.map((image, index) => (
                    <div 
                      key={index} 
                      className="relative aspect-square border rounded-lg overflow-hidden cursor-pointer hover:shadow-lg hover:scale-105 transition-all duration-200 group"
                      onClick={() => setSelectedImageIndex(index)}
                    >
                      <Image
                        src={image.url}
                        alt={`Generated image ${index + 1}`}
                        width={150}
                        height={150}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-200 flex items-center justify-center">
                        <svg 
                          className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                          xmlns="http://www.w3.org/2000/svg" 
                          fill="none" 
                          viewBox="0 0 24 24" 
                          stroke="currentColor"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                        </svg>
                      </div>
                      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-2">
                        <p className="text-white text-xs font-medium truncate">{image.ai_provider}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="text-center text-sm text-muted-foreground">
                  Click on any image to view larger
                </div>
              </div>
            )}

            {/* Image Modal */}
            {selectedImageIndex !== null && (
              <div 
                className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
                onClick={() => setSelectedImageIndex(null)}
              >
                <div 
                  className="relative max-w-4xl max-h-full bg-white rounded-lg overflow-hidden shadow-2xl"
                  onClick={(e) => e.stopPropagation()}
                >
                  {/* Modal Header */}
                  <div className="flex items-center justify-between p-4 border-b">
                    <div className="flex items-center gap-3">
                      <Badge variant="secondary" className="text-sm">
                        {generatedImages[selectedImageIndex].ai_provider}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        Image {selectedImageIndex + 1} of {generatedImages.length}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {/* Navigation Buttons */}
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedImageIndex(
                          selectedImageIndex > 0 ? selectedImageIndex - 1 : generatedImages.length - 1
                        )}
                        disabled={generatedImages.length <= 1}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
                        </svg>
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedImageIndex(
                          selectedImageIndex < generatedImages.length - 1 ? selectedImageIndex + 1 : 0
                        )}
                        disabled={generatedImages.length <= 1}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                        </svg>
                      </Button>
                      {/* Close Button */}
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedImageIndex(null)}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </Button>
                    </div>
                  </div>

                  {/* Modal Image */}
                  <div className="relative">
                    <Image
                      src={generatedImages[selectedImageIndex].url}
                      alt={`Generated image ${selectedImageIndex + 1}`}
                      width={800}
                      height={600}
                      className="w-full h-auto max-h-[70vh] object-contain"
                    />
                  </div>

                  {/* Modal Footer */}
                  <div className="p-4 border-t bg-gray-50">
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700">Prompt:</p>
                      <p className="text-sm text-gray-600 bg-white p-3 rounded border">
                        {generatedImages[selectedImageIndex].prompt}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
          
          <CardFooter className="flex justify-between items-center border-t pt-6">
            <div className="text-sm text-muted-foreground">
              {generatedImages.length === 0 
                ? (t.creation?.refinement?.form?.generate_to_proceed || "Generate at least one image to proceed")
                : `${generatedImages.length} image(s) generated`
              }
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
    </div>
  );
};
