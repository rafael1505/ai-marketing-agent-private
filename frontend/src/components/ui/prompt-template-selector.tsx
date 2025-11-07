"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PROMPT_TEMPLATES, PromptTemplate, PromptContext } from "@/data/prompt-templates";
import { Check } from "lucide-react";

interface PromptTemplateSelectorProps {
  onSelect: (template: PromptTemplate, generatedPrompt: string) => void;
  context: PromptContext;
  selectedTemplateId?: string;
  translations?: any;
  creativeApproach?: 'story_led' | 'concept_led' | 'hybrid'; // Filter templates by approach
}

export function PromptTemplateSelector({ 
  onSelect, 
  context,
  selectedTemplateId,
  translations,
  creativeApproach = 'hybrid'
}: PromptTemplateSelectorProps) {
  const [expanded, setExpanded] = React.useState(false);
  
  // Filter templates based on creative approach
  const filteredTemplates = React.useMemo(() => {
    // Check if templates have creativeApproach property
    const hasCreativeApproachProperty = PROMPT_TEMPLATES.length > 0 && 'creativeApproach' in PROMPT_TEMPLATES[0];
    
    // If templates don't have the property yet (build cache issue), show all templates
    if (!hasCreativeApproachProperty) {
      return PROMPT_TEMPLATES;
    }
    
    if (creativeApproach === 'hybrid') {
      return PROMPT_TEMPLATES;
    }
    
    const filtered = PROMPT_TEMPLATES.filter(template => {
      const templateApproach = template.creativeApproach;
      const matches = templateApproach === creativeApproach || templateApproach === 'both';
      return matches;
    });
    
    return filtered;
  }, [creativeApproach]);

  const categories = [
    { id: 'product', name: 'Product', icon: '📦' },
    { id: 'content', name: 'Content', icon: '📝' },
    { id: 'engagement', name: 'Engagement', icon: '💬' },
    { id: 'conversion', name: 'Conversion', icon: '💰' },
  ];

  const handleTemplateSelect = (template: PromptTemplate) => {
    const generatedPrompt = template.promptBuilder(context);
    onSelect(template, generatedPrompt);
  };

  // Helper to get translated template name
  const getTemplateName = (template: PromptTemplate) => {
    if (translations?.enrichment?.templates) {
      const templateKey = template.id;
      return translations.enrichment.templates[templateKey]?.name || template.name;
    }
    return template.name;
  };

  // Helper to get translated template description
  const getTemplateDescription = (template: PromptTemplate) => {
    if (translations?.enrichment?.templates) {
      const templateKey = template.id;
      return translations.enrichment.templates[templateKey]?.description || '';
    }
    return '';
  };

  return (
    <div className="space-y-4">
      <Card className="rounded-2xl bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-2xl">✨</span>
              <CardTitle className="text-lg font-medium text-purple-900">
                {translations?.enrichment?.ui?.quick_start_templates || "Quick Start Templates"}
              </CardTitle>
            </div>
            {!expanded && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setExpanded(true)}
                className="text-purple-700 hover:text-purple-900 hover:bg-purple-100"
              >
                {translations?.enrichment?.ui?.browse_all || "Browse All"} →
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <CardDescription className="text-purple-700 mb-4">
            {translations?.enrichment?.ui?.template_selector_description || "Start with a professionally designed prompt template tailored to your campaign type"}
            {creativeApproach !== 'hybrid' && (
              <span className="block mt-2 text-sm font-medium text-purple-900">
                {creativeApproach === 'story_led' 
                  ? '📖 Showing templates optimized for Story-Led approach'
                  : '💡 Showing templates optimized for Concept-Led approach'
                }
              </span>
            )}
          </CardDescription>

          {!expanded ? (
            // Show popular templates (filtered by creative approach)
            <>
              {filteredTemplates.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p className="text-sm">No templates match the selected creative approach.</p>
                  <p className="text-xs mt-2">Try selecting a different approach or use Hybrid mode.</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-3">
                  {filteredTemplates.slice(0, 4).map((template) => {
                const Icon = template.icon;
                const isSelected = selectedTemplateId === template.id;
                
                return (
                  <Card
                    key={template.id}
                    className={`cursor-pointer transition-all hover:shadow-md ${
                      isSelected 
                        ? 'border-2 border-purple-500 bg-purple-50' 
                        : 'border border-gray-200 hover:border-purple-300'
                    }`}
                    onClick={() => handleTemplateSelect(template)}
                  >
                    <CardHeader className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          <Icon />
                          <div>
                            <CardTitle className="text-sm font-medium">
                              {getTemplateName(template)}
                            </CardTitle>
                            <Badge 
                              variant="secondary" 
                              className="mt-1 text-xs bg-gray-100 text-gray-600"
                            >
                              {template.category}
                            </Badge>
                          </div>
                        </div>
                        {isSelected && (
                          <Check className="w-5 h-5 text-purple-600" />
                        )}
                      </div>
                    </CardHeader>
                  </Card>
                );
              })}
                </div>
              )}
            </>
          ) : (
            // Show all templates by category (filtered by creative approach)
            <div className="space-y-6">
              {categories.map((category) => {
                const templates = filteredTemplates.filter(t => t.category === category.id);
                
                return (
                  <div key={category.id}>
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-xl">{category.icon}</span>
                      <h3 className="text-sm font-semibold text-gray-700">
                        {category.name}
                      </h3>
                      <span className="text-xs text-gray-500">
                        ({templates.length})
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {templates.map((template) => {
                        const Icon = template.icon;
                        const isSelected = selectedTemplateId === template.id;
                        
                        return (
                          <Card
                            key={template.id}
                            className={`cursor-pointer transition-all hover:shadow-md ${
                              isSelected 
                                ? 'border-2 border-purple-500 bg-purple-50' 
                                : 'border border-gray-200 hover:border-purple-300'
                            }`}
                            onClick={() => handleTemplateSelect(template)}
                          >
                            <CardHeader className="p-3">
                              <div className="flex flex-col gap-2">
                                <div className="flex items-center justify-between">
                                  <Icon />
                                  {isSelected && (
                                    <Check className="w-4 h-4 text-purple-600" />
                                  )}
                                </div>
                                <CardTitle className="text-xs font-medium leading-tight">
                                  {getTemplateName(template)}
                                </CardTitle>
                              </div>
                            </CardHeader>
                          </Card>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setExpanded(false)}
                className="w-full text-purple-700 hover:text-purple-900 hover:bg-purple-100"
              >
                ← {translations?.enrichment?.ui?.show_less || "Show Less"}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {selectedTemplateId && (
        <Card className="rounded-2xl border-green-200 bg-green-50">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <Check className="w-5 h-5 text-green-600 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-green-900">
                  {translations?.enrichment?.ui?.template_applied || "Template Applied"}
                </p>
                <p className="text-xs text-green-700 mt-1">
                  {translations?.enrichment?.ui?.template_applied_description || "Your prompt has been generated based on the selected template. Feel free to customize it further below."}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
