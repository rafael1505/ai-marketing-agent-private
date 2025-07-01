import React, { useState, useMemo } from "react";
import Link from "next/link";
import { getTranslations } from "@/i18n";
import { Material, MaterialStage, MaterialStatus } from "@/types";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate, truncateText } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface MaterialCardProps {
  material: Material;
  locale?: string;
}

export const MaterialCard: React.FC<MaterialCardProps> = ({
  material,
  locale = "en"
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const t = useMemo(() => {
    try {
      // Use synchronous access to avoid state management issues
      return getTranslations(locale === "pt" ? "pt" : "en");
    } catch (e) {
      console.error("Translation error in MaterialCard:", e);
      // Return a fallback minimal translation object
      return {
        materials: { 
          view: "View", 
          edit: "Edit",
          stages: {
            idea: "Idea",
            refinement: "Refinement",
            finalization: "Finalization"
          },
          status: {
            draft: "Draft",
            in_progress: "In Progress",
            ready_for_review: "Ready for Review",
            completed: "Completed",
            archived: "Archived"
          }
        }
      };
    }
  }, [locale]);
  
  // Mark component as loaded after small delay for smooth animation
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoaded(true);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  const getStageLabel = (stage: MaterialStage): string => {
    switch (stage) {
      case MaterialStage.IDEA:
        return t.materials.stages.idea;
      case MaterialStage.REFINEMENT:
        return t.materials.stages.refinement;
      case MaterialStage.FINALIZATION:
        return t.materials.stages.finalization;
      default:
        return stage;
    }
  };

  const getStatusLabel = (status: MaterialStatus): string => {
    switch (status) {
      case MaterialStatus.DRAFT:
        return t.materials.status.draft;
      case MaterialStatus.IN_PROGRESS:
        return t.materials.status.in_progress;
      case MaterialStatus.READY_FOR_REVIEW:
        return t.materials.status.ready_for_review;
      case MaterialStatus.COMPLETED:
        return t.materials.status.completed;
      case MaterialStatus.ARCHIVED:
        return t.materials.status.archived;
      default:
        return status;
    }
  };

  const getStageBadgeClass = (stage: MaterialStage): string => {
    switch (stage) {
      case MaterialStage.IDEA:
        return "material-stage-idea";
      case MaterialStage.REFINEMENT:
        return "material-stage-refinement";
      case MaterialStage.FINALIZATION:
        return "material-stage-finalization";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusColor = (status: MaterialStatus): string => {
    switch (status) {
      case MaterialStatus.DRAFT:
        return "material-status-draft";
      case MaterialStatus.IN_PROGRESS:
        return "bg-blue-100 text-blue-800";
      case MaterialStatus.READY_FOR_REVIEW:
        return "bg-amber-100 text-amber-800";
      case MaterialStatus.COMPLETED:
        return "bg-green-100 text-green-800";
      case MaterialStatus.ARCHIVED:
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getBorderColor = (stage: MaterialStage): string => {
    switch (stage) {
      case MaterialStage.IDEA:
        return "border-t-primary";
      case MaterialStage.REFINEMENT:
        return "border-t-accent";
      case MaterialStage.FINALIZATION:
        return "border-t-success";
      default:
        return "border-t-muted";
    }
  };
  
  const getBackgroundGradient = (stage: MaterialStage): string => {
    switch (stage) {
      case MaterialStage.IDEA:
        return "from-primary/5 to-secondary/5";
      case MaterialStage.REFINEMENT:
        return "from-accent/5 to-primary/5";
      case MaterialStage.FINALIZATION:
        return "from-success/5 to-primary/5";
      default:
        return "from-gray-50 to-gray-50";
    }
  };
  return (
    <div className={`h-full transition-opacity duration-300 ${isLoaded ? 'opacity-100' : 'opacity-0'}`}>
      <Card className={`shadow-md hover-card h-full border-t-4 ${getBorderColor(material.stage)}`}>
        <CardHeader className={`bg-gradient-to-r ${getBackgroundGradient(material.stage)}`}>
          <div className="flex justify-between items-start">
            <CardTitle className="text-lg font-semibold">{material.title}</CardTitle>
            <div className="flex space-x-2">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStageBadgeClass(material.stage)}`}>
                {getStageLabel(material.stage)}
              </span>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(material.status)}`}>
                {getStatusLabel(material.status)}
              </span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground mb-4 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1.5">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
            {formatDate(material.created_at)}
          </div>
          <p className="text-foreground">
            {material.description ? truncateText(material.description, 150) : ""}
          </p>
          {material.keywords.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-1.5">
              {material.keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-secondary text-secondary-foreground transition-colors hover:bg-secondary/80"
                >
                  #{keyword}
                </span>
              ))}
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-between space-x-2 border-t pt-4">
          <span className="text-xs text-muted-foreground">ID: {material.id.substring(0, 8)}</span>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm" asChild className="btn-scale">
              <Link href={`/${locale}/materials/${material.id}`}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
                  <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                {t.materials.view}
              </Link>
            </Button>
            <Button variant="default" size="sm" asChild className="btn-scale">
              <Link href={`/${locale}/materials/${material.id}/edit`}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
                  <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/>
                </svg>
                {t.materials.edit}
              </Link>
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
};
