"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { getTranslations } from "@/i18n";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { getMaterial, addFeedback, updateStage } from "@/services/materials";
import { Material, MaterialStage, MaterialStatus } from "@/types";
import { formatDate } from "@/lib/utils";

export default function MaterialDetailPage({
  params
}: {
  params: { locale: string; id: string }
}) {
  const locale = params.locale || "en";
  const materialId = params.id;
  const [t, setT] = useState<Record<string, any>>({});
  const [translationsLoaded, setTranslationsLoaded] = useState(false);
  
  const [material, setMaterial] = useState<Material | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [feedbackText, setFeedbackText] = useState("");
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);  const [isUpdatingStage, setIsUpdatingStage] = useState(false);

  useEffect(() => {
    const loadTranslations = async () => {
      try {
        const translations = await getTranslations(locale === "pt" ? "pt" : "en");
        setT(translations);
        setTranslationsLoaded(true);
      } catch (error) {
        console.error("Failed to load translations:", error);
        setT({
          errors: { server_error: "Server error. Please try again later." },
          common: { loading: "Loading..." }
        });
        setTranslationsLoaded(true);
      }
    };
    loadTranslations();
  }, [locale]);
  useEffect(() => {
    const fetchMaterial = async () => {
      try {
        const data = await getMaterial(materialId);
        setMaterial(data);
      } catch (err) {
        console.error("Error fetching material:", err);
        // Safely access error message with fallback
        setError(t.errors && t.errors.server_error 
          ? t.errors.server_error 
          : "Server error. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };

    // Only fetch if translations are loaded and materialId exists
    if (Object.keys(t).length > 0 && materialId) {
      fetchMaterial();
    }
  }, [materialId, t]);

  const handleSubmitFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!feedbackText.trim() || !material) return;

    setIsSubmittingFeedback(true);
    try {
      const updatedMaterial = await addFeedback(material.id, feedbackText);
      setMaterial(updatedMaterial);
      setFeedbackText("");
    } catch (error) {
      console.error("Error submitting feedback:", error);
    } finally {
      setIsSubmittingFeedback(false);
    }
  };

  const handleUpdateStage = async () => {
    if (!material) return;

    let nextStage: MaterialStage;
    if (material.stage === MaterialStage.IDEA) {
      nextStage = MaterialStage.REFINEMENT;
    } else if (material.stage === MaterialStage.REFINEMENT) {
      nextStage = MaterialStage.FINALIZATION;
    } else {
      // Already in final stage, mark as completed
      nextStage = material.stage;
    }

    setIsUpdatingStage(true);
    try {
      const updatedMaterial = await updateStage(
        material.id,
        nextStage,
        nextStage === material.stage ? MaterialStatus.COMPLETED : MaterialStatus.IN_PROGRESS
      );
      setMaterial(updatedMaterial);
    } catch (error) {
      console.error("Error updating stage:", error);
    } finally {
      setIsUpdatingStage(false);
    }
  };

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
        return t.materials.statuses.draft;
      case MaterialStatus.IN_PROGRESS:
        return t.materials.statuses.in_progress;
      case MaterialStatus.READY_FOR_REVIEW:
        return t.materials.statuses.ready_for_review;
      case MaterialStatus.COMPLETED:
        return t.materials.statuses.completed;
      case MaterialStatus.ARCHIVED:
        return t.materials.statuses.archived;
      default:
        return status;
    }
  };
  // Show loading if translations aren't loaded yet or data is being fetched
  if (!translationsLoaded || (isLoading && Object.keys(t).length === 0)) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="spinner" />
        <span className="ml-2">Loading...</span>
      </div>
    );
  }

  // Make sure translations are loaded before rendering
  if (!t.nav || !t.materials || !t.common) {
    console.error("Translation keys are missing", t);
    return (
      <div className="flex justify-center items-center h-64 text-red-500">
        <p>Error loading page content. Please refresh the page.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="spinner" />
        <span className="ml-2">{t.common.loading}</span>
      </div>
    );
  }
  if (error || !material) {
    return (
      <div className="text-center py-12 text-red-500">
        {error || "Material not found"}
      </div>
    );
  }
  
  // Only show connection error if api_error is explicitly true
  if (material && material.api_error === true) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 mb-4">
          <h2 className="text-xl font-bold">Connection Error</h2>
          <p>{material.description || "Could not connect to the API server. Please check your connection and try again."}</p>
        </div>
        <Button onClick={() => window.location.reload()}>
          {t.common && t.common.retry ? t.common.retry : "Retry"}
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            {material.title}
          </h1>
          <div className="flex space-x-2 text-sm text-muted-foreground">
            <span>{getStageLabel(material.stage)}</span>
            <span>•</span>
            <span>{getStatusLabel(material.status)}</span>
            <span>•</span>
            <span>{formatDate(material.created_at)}</span>
          </div>
        </div>
        
        <div className="flex space-x-2">
          <Button
            variant="outline"
            asChild
          >
            <Link href={`/${locale}/materials/${material.id}/edit`}>
              {typeof t.common?.edit === 'string' ? t.common?.edit : "Edit"}
            </Link>
          </Button>
          {material.stage !== MaterialStage.FINALIZATION || material.status !== MaterialStatus.COMPLETED ? (
            <Button
              onClick={handleUpdateStage}
              isLoading={isUpdatingStage}
            >
              {t.material.next_stage}
            </Button>
          ) : null}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t.material.details}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {material.description && (
              <div>
                <h3 className="font-medium">{t.materials.description}</h3>
                <p className="text-sm mt-1">{material.description}</p>
              </div>
            )}
            
            {material.target_audience && (
              <div>
                <h3 className="font-medium">{t.material.target_audience}</h3>
                <p className="text-sm mt-1">{material.target_audience}</p>
              </div>
            )}
            
            {material.campaign_objective && (
              <div>
                <h3 className="font-medium">{t.material.campaign_objective}</h3>
                <p className="text-sm mt-1">{material.campaign_objective}</p>
              </div>
            )}
            
            {material.keywords.length > 0 && (
              <div>
                <h3 className="font-medium">{t.material.keywords}</h3>
                <div className="flex flex-wrap gap-1 mt-1">
                  {material.keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t.material.feedback}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {material.feedback.length > 0 ? (
              <div className="space-y-3">
                {material.feedback.map((feedback, index) => (
                  <div key={index} className="border-b pb-3 last:border-b-0 last:pb-0">
                    <p className="text-sm">{feedback.comment}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatDate(feedback.created_at)}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No feedback yet</p>
            )}

            <form onSubmit={handleSubmitFeedback}>
              <div className="space-y-2">
                <Label htmlFor="feedback">{t.material.add_feedback}</Label>
                <Textarea
                  id="feedback"
                  value={feedbackText}
                  onChange={(e) => setFeedbackText(e.target.value)}
                  rows={3}
                  required
                />
              </div>
              <Button
                type="submit"
                className="mt-2"
                isLoading={isSubmittingFeedback}
                disabled={!feedbackText.trim()}
              >
                {t.material.submit_feedback}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      {material.generated_images.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold">{t.material.generated_images}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {material.generated_images.map((image, index) => (
              <div 
                key={index} 
                className={`border rounded-lg overflow-hidden cursor-pointer ${
                  material.selected_image === image.url ? 'ring-2 ring-primary' : ''
                }`}
              >
                <Image
                  src={image.url}
                  alt={`Generated image ${index + 1}`}
                  width={400}
                  height={200}
                  className="w-full h-48 object-cover"
                />
                <div className="p-3">
                  <p className="text-sm text-gray-500 truncate">{image.prompt}</p>
                  <p className="text-xs text-gray-400 mt-1">{image.ai_provider}</p>
                  {material.selected_image === image.url && (
                    <div className="mt-2">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {t.material.selected_image}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
