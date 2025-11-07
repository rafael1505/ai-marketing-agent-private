/**
 * People Preference Selector Component
 * 
 * Smart UI component for selecting how people should appear in AI-generated images.
 * Features:
 * - 4 modes: Auto, Include, Exclude, Minimal
 * - Real-time conflict detection
 * - Contextual warnings and suggestions
 * - Industry-specific recommendations
 */

"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  PeoplePreference, 
  ConflictAnalysis, 
  Material 
} from "@/types";
import { 
  analyzePeopleConflicts, 
  getPeopleModeDescription, 
  getSeverityBadgeVariant,
  getIndustryRecommendation 
} from "@/lib/conflict-analyzer";
import { SeasonalContext } from "@/lib/seasonal-context";

interface PeoplePreferenceSelectorProps {
  value: PeoplePreference;
  onChange: (value: PeoplePreference) => void;
  industryId: string | null;
  material: Material | null;
  seasonalContext: SeasonalContext | null;
  translations: any;
}

export const PeoplePreferenceSelector: React.FC<PeoplePreferenceSelectorProps> = ({
  value,
  onChange,
  industryId,
  material,
  seasonalContext,
  translations
}) => {
  const [conflictAnalysis, setConflictAnalysis] = React.useState<ConflictAnalysis>({
    hasConflict: false,
    overallSeverity: "none",
    conflictingSources: [],
    recommendation: "auto"
  });
  
  const [showDetails, setShowDetails] = React.useState(false);
  
  // Analyze conflicts whenever dependencies change
  React.useEffect(() => {
    const analysis = analyzePeopleConflicts(
      value,
      industryId,
      material,
      seasonalContext
    );
    setConflictAnalysis(analysis);
  }, [value, industryId, material, seasonalContext]);
  
  // Get translations with fallbacks
  const t = translations?.creation?.refinement?.people_preference || {
    title: "People Preference",
    description: "Control whether people appear in your images",
    mode_auto: "Auto (Recommended)",
    mode_auto_desc: "Let the system decide based on your campaign context",
    mode_include: "Always Include People",
    mode_include_desc: "Generate lifestyle and human-centric images",
    mode_exclude: "Never Include People",
    mode_exclude_desc: "Product-only, object-focused, or abstract imagery",
    mode_minimal: "Product-Focused (Minimal People)",
    mode_minimal_desc: "Prioritize products, but allow people if contextually relevant",
    conflict_warning: "Potential Conflict Detected",
    recommendation_prefix: "Recommended for your industry:",
    view_details: "View Details",
    hide_details: "Hide Details",
    apply_recommendation: "Use Recommended Setting"
  };
  
  const modes: PeoplePreference[] = ["auto", "include", "exclude", "minimal"];
  
  // Get industry recommendation
  const industryRecommendation = getIndustryRecommendation(industryId);
  const showRecommendation = value !== industryRecommendation && industryRecommendation !== "auto";
  
  return (
    <Card className="border-l-4 border-l-purple-500">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
            <span className="text-lg">👥</span>
          </div>
          {t.title}
          {conflictAnalysis.hasConflict && (
            <Badge variant={getSeverityBadgeVariant(conflictAnalysis.overallSeverity)}>
              {conflictAnalysis.overallSeverity.toUpperCase()} CONFLICT
            </Badge>
          )}
        </CardTitle>
        <CardDescription>
          {t.description}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="space-y-3">
          {modes.map((mode) => {
            const modeInfo = getPeopleModeDescription(mode);
            const isRecommended = mode === industryRecommendation;
            const isSelected = value === mode;
            
            return (
              <div
                key={mode}
                onClick={() => onChange(mode)}
                className={`flex items-start space-x-3 p-3 rounded-lg border transition-all cursor-pointer ${
                  isSelected
                    ? "bg-purple-50 border-purple-300 dark:bg-purple-950/20 dark:border-purple-800"
                    : "border-gray-200 hover:border-purple-200 dark:border-gray-700 dark:hover:border-purple-800"
                }`}
              >
                <input
                  type="radio"
                  id={`people-${mode}`}
                  name="people-preference"
                  value={mode}
                  checked={isSelected}
                  onChange={() => onChange(mode)}
                  className="mt-1 h-4 w-4 text-purple-600 focus:ring-purple-500"
                />
                <div className="flex-1 space-y-1">
                  <Label
                    htmlFor={`people-${mode}`}
                    className="flex items-center gap-2 cursor-pointer font-medium"
                  >
                    <span className="text-lg">{modeInfo.icon}</span>
                    {t[`mode_${mode}`] || modeInfo.title}
                    {isRecommended && (
                      <Badge variant="secondary" className="ml-2">
                        ⭐ Recommended
                      </Badge>
                    )}
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    {t[`mode_${mode}_desc`] || modeInfo.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Industry Recommendation */}
        {showRecommendation && (
          <Alert>
            <AlertDescription className="flex items-center justify-between">
              <span>
                💡 {t.recommendation_prefix} <strong>{getPeopleModeDescription(industryRecommendation).title}</strong>
              </span>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => onChange(industryRecommendation)}
              >
                {t.apply_recommendation}
              </Button>
            </AlertDescription>
          </Alert>
        )}
        
        {/* Conflict Warnings */}
        {conflictAnalysis.hasConflict && (
          <Alert variant={conflictAnalysis.overallSeverity === "high" ? "destructive" : "default"}>
            <AlertTitle className="flex items-center justify-between">
              <span>⚠️ {t.conflict_warning}</span>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
              >
                {showDetails ? t.hide_details : t.view_details}
              </Button>
            </AlertTitle>
            
            {showDetails && (
              <AlertDescription className="mt-3 space-y-3">
                {conflictAnalysis.conflictingSources.map((conflict, index) => (
                  <div key={index} className="p-3 bg-white dark:bg-gray-900 rounded-lg border">
                    <div className="flex items-start gap-2">
                      <Badge variant={getSeverityBadgeVariant(conflict.severity)}>
                        {conflict.source.replace("_", " ").toUpperCase()}
                      </Badge>
                      <div className="flex-1 space-y-1">
                        <p className="text-sm font-medium">{conflict.reason}</p>
                        <p className="text-xs text-muted-foreground italic">
                          💡 {conflict.suggestion}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
                
                {conflictAnalysis.recommendation !== value && (
                  <Button
                    type="button"
                    onClick={() => onChange(conflictAnalysis.recommendation)}
                    className="w-full"
                    variant="outline"
                  >
                    Switch to "{getPeopleModeDescription(conflictAnalysis.recommendation).title}"
                  </Button>
                )}
              </AlertDescription>
            )}
          </Alert>
        )}
        
        {/* Mode-specific hints */}
        {value === "exclude" && !conflictAnalysis.hasConflict && (
          <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <p className="text-sm text-blue-900 dark:text-blue-100">
              💼 <strong>Product-Only Mode Active:</strong> AI will focus exclusively on products, objects, abstract elements, or scenery. Perfect for informative flyers, technical documentation, or product catalogs.
            </p>
          </div>
        )}
        
        {value === "minimal" && (
          <div className="p-3 bg-green-50 dark:bg-green-950/20 rounded-lg border border-green-200 dark:border-green-800">
            <p className="text-sm text-green-900 dark:text-green-100">
              🎯 <strong>Product-Focused Mode Active:</strong> AI will prioritize showing your product/service while allowing subtle human context (hands holding items, people in background). Great for product showcases with lifestyle hints.
            </p>
          </div>
        )}
        
        {value === "include" && (
          <div className="p-3 bg-purple-50 dark:bg-purple-950/20 rounded-lg border border-purple-200 dark:border-purple-800">
            <p className="text-sm text-purple-900 dark:text-purple-100">
              👥 <strong>People-Centric Mode Active:</strong> AI will generate lifestyle imagery with diverse, authentic people in natural settings. Ideal for campaigns highlighting human experiences, emotions, or community impact.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
