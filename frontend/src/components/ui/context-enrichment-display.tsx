"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getTemporalContext } from "@/utils/temporal-context";
import { getIndustryTemplate } from "@/data/industry-templates";

interface ContextEnrichmentDisplayProps {
  industry?: string;
  onApplyIndustry?: () => void;
  onApplyTemporal?: () => void;
  industryApplied?: boolean;
  temporalApplied?: boolean;
}

export function ContextEnrichmentDisplay({
  industry,
  onApplyIndustry,
  onApplyTemporal,
  industryApplied = false,
  temporalApplied = false
}: ContextEnrichmentDisplayProps) {
  const temporalContext = getTemporalContext();
  const industryTemplate = industry ? getIndustryTemplate(industry) : null;

  return (
    <div className="space-y-4">
      {/* Temporal Context Card */}
      <Card className="rounded-2xl bg-gradient-to-r from-orange-50 to-yellow-50 border-orange-200">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xl">📅</span>
              <CardTitle className="text-sm font-medium text-orange-900">
                Seasonal Context
              </CardTitle>
            </div>
            {onApplyTemporal && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onApplyTemporal}
                disabled={temporalApplied}
                className={`text-xs ${
                  temporalApplied
                    ? 'text-green-600 cursor-default'
                    : 'text-orange-700 hover:text-orange-900 hover:bg-orange-100'
                }`}
              >
                {temporalApplied ? '✓ Applied' : 'Apply →'}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-orange-800">
                {temporalContext.season.name} ({temporalContext.currentMonth})
              </span>
              <Badge variant="secondary" className="bg-orange-100 text-orange-700 text-xs">
                {temporalContext.seasonalMood}
              </Badge>
            </div>
            
            <div className="text-xs text-orange-700">
              <p className="font-medium mb-1">Suggested themes:</p>
              <div className="flex flex-wrap gap-1">
                {temporalContext.suggestedThemes.map((theme) => (
                  <Badge 
                    key={theme} 
                    variant="outline" 
                    className="bg-white border-orange-200 text-orange-700"
                  >
                    {theme}
                  </Badge>
                ))}
              </div>
            </div>

            {temporalContext.upcomingHolidays.length > 0 && (
              <div className="text-xs text-orange-700">
                <p className="font-medium mb-1">Upcoming events:</p>
                <ul className="list-disc list-inside space-y-0.5">
                  {temporalContext.upcomingHolidays.map((holiday, idx) => (
                    <li key={idx}>{holiday}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Industry Context Card */}
      {industryTemplate && (
        <Card className="rounded-2xl bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xl">🏢</span>
                <CardTitle className="text-sm font-medium text-indigo-900">
                  Industry Guidelines
                </CardTitle>
              </div>
              {onApplyIndustry && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onApplyIndustry}
                  disabled={industryApplied}
                  className={`text-xs ${
                    industryApplied
                      ? 'text-green-600 cursor-default'
                      : 'text-indigo-700 hover:text-indigo-900 hover:bg-indigo-100'
                  }`}
                >
                  {industryApplied ? '✓ Applied' : 'Apply →'}
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <Badge variant="secondary" className="bg-indigo-100 text-indigo-700 text-xs mb-2">
                {industryTemplate.name}
              </Badge>
              <p className="text-xs text-indigo-700 leading-relaxed">
                {industryTemplate.styleGuide}
              </p>
            </div>

            <div className="text-xs text-indigo-700">
              <p className="font-medium mb-1">Visual keywords:</p>
              <div className="flex flex-wrap gap-1">
                {industryTemplate.visualKeywords.slice(0, 6).map((keyword) => (
                  <Badge 
                    key={keyword} 
                    variant="outline" 
                    className="bg-white border-indigo-200 text-indigo-700"
                  >
                    {keyword}
                  </Badge>
                ))}
              </div>
            </div>

            {industryTemplate.avoidElements.length > 0 && (
              <div className="text-xs text-indigo-700">
                <p className="font-medium mb-1">⚠️ Avoid:</p>
                <p className="italic">
                  {industryTemplate.avoidElements.slice(0, 3).join(', ')}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
