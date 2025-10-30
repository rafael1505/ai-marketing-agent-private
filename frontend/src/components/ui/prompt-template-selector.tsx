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
}

export function PromptTemplateSelector({ 
  onSelect, 
  context,
  selectedTemplateId 
}: PromptTemplateSelectorProps) {
  const [expanded, setExpanded] = React.useState(false);

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

  return (
    <div className="space-y-4">
      <Card className="rounded-2xl bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-2xl">✨</span>
              <CardTitle className="text-lg font-medium text-purple-900">
                Quick Start Templates
              </CardTitle>
            </div>
            {!expanded && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setExpanded(true)}
                className="text-purple-700 hover:text-purple-900 hover:bg-purple-100"
              >
                Browse All →
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <CardDescription className="text-purple-700 mb-4">
            Start with a professionally designed prompt template tailored to your campaign type
          </CardDescription>

          {!expanded ? (
            // Show popular templates
            <div className="grid grid-cols-2 gap-3">
              {PROMPT_TEMPLATES.slice(0, 4).map((template) => {
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
                              {template.name}
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
          ) : (
            // Show all templates by category
            <div className="space-y-6">
              {categories.map((category) => {
                const templates = PROMPT_TEMPLATES.filter(t => t.category === category.id);
                
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
                                  {template.name}
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
                ← Show Less
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
                  Template Applied
                </p>
                <p className="text-xs text-green-700 mt-1">
                  Your prompt has been generated based on the selected template. 
                  Feel free to customize it further below.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
