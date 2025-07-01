"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getTranslations } from "@/i18n";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { TagInput } from "@/components/ui/tag-input";
import { getMaterial, updateMaterial } from "@/services/materials";
import { Material, MaterialStage, MaterialStatus } from "@/types";

export default function MaterialEditPage({
  params
}: {
  params: { locale: string; id: string }
}) {
  const router = useRouter();
  const locale = params.locale || "en";
  const materialId = params.id;
  
  const [t, setT] = useState<Record<string, any>>({});
  const [translationsLoaded, setTranslationsLoaded] = useState(false);
  
  const [material, setMaterial] = useState<Material | null>(null);
  const [formData, setFormData] = useState<{
    title: string;
    description: string;
    target_audience: string;
    campaign_objective: string;
    keywords: string[];
    stage: MaterialStage | undefined;
    status: MaterialStatus | undefined;
  }>({
    title: "",
    description: "",
    target_audience: "",
    campaign_objective: "",
    keywords: [],
    stage: undefined,
    status: undefined
  });
  
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Load translations
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
          common: { loading: "Loading..." },
          materials: { edit_title: "Edit Material" }
        });
        setTranslationsLoaded(true);
      }
    };
    loadTranslations();
  }, [locale]);

  // Load material data
  useEffect(() => {
    if (!translationsLoaded) return;
    
    const fetchMaterial = async () => {
      try {
        setIsLoading(true);
        const data = await getMaterial(materialId);
        setMaterial(data);
        setFormData({
          title: data.title || "",
          description: data.description || "",
          target_audience: data.target_audience || "",
          campaign_objective: data.campaign_objective || "",
          keywords: data.keywords || [],
          stage: data.stage,
          status: data.status
        });
      } catch (error) {
        console.error("Error fetching material:", error);
        setError(t.errors?.server_error || "Failed to load material. Please try again.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchMaterial();
  }, [translationsLoaded, materialId, t]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleKeywordsChange = (keywords: string[]) => {
    setFormData(prev => ({ ...prev, keywords }));
  };

  const handleSelectChange = (field: string, value: string) => {
    if (field === 'stage') {
      setFormData(prev => ({ ...prev, [field]: value as MaterialStage }));
    } else if (field === 'status') {
      setFormData(prev => ({ ...prev, [field]: value as MaterialStatus }));
    } else {
      setFormData(prev => ({ ...prev, [field]: value }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveSuccess(false);
    setError("");

    try {
      await updateMaterial(materialId, formData);
      setSaveSuccess(true);
      // Optionally redirect back to the material view page after successful save
      setTimeout(() => {
        router.push(`/${locale}/materials/${materialId}`);
      }, 1500);
    } catch (error) {
      console.error("Error updating material:", error);
      setError(t.errors?.save_failed || "Failed to save changes. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  if (!translationsLoaded || isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="spinner" />
        <span className="ml-2">{typeof t.common?.loading === 'string' ? t.common?.loading : "Loading..."}</span>
      </div>
    );
  }

  if (error && !material) {
    return (
      <div className="p-4">
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button asChild>
          <Link href={`/${locale}/materials`}>{typeof t.common?.back === 'string' ? t.common?.back : "Back to Materials"}</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">
          {typeof t.materials?.edit_title === 'string' ? t.materials?.edit_title : "Edit Material"}
        </h1>
        <Button variant="outline" asChild>
          <Link href={`/${locale}/materials/${materialId}`}>
            {typeof t.common?.cancel === 'string' ? t.common?.cancel : "Cancel"}
          </Link>
        </Button>
      </div>

      {saveSuccess && (
        <Alert className="bg-green-50 border-green-200 text-green-800">
          <AlertDescription>
            {typeof t.materials?.save_success === 'string' ? t.materials?.save_success : "Changes saved successfully!"}
          </AlertDescription>
        </Alert>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <h2 className="text-lg font-medium">{typeof t.materials?.details === 'string' ? t.materials?.details : "Material Details"}</h2>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">{typeof t.materials?.title === 'string' ? t.materials?.title : "Title"}</Label>
              <Input
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">{typeof t.materials?.description === 'string' ? t.materials?.description : "Description"}</Label>
              <Textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={4}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="target_audience">{typeof t.materials?.target_audience === 'string' ? t.materials?.target_audience : "Target Audience"}</Label>
              <Input
                id="target_audience"
                name="target_audience"
                value={formData.target_audience}
                onChange={handleChange}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="campaign_objective">{typeof t.materials?.campaign_objective === 'string' ? t.materials?.campaign_objective : "Campaign Objective"}</Label>
              <Input
                id="campaign_objective"
                name="campaign_objective"
                value={formData.campaign_objective}
                onChange={handleChange}
              />
            </div>

            <div className="space-y-2">
              <Label>{typeof t.materials?.keywords === 'string' ? t.materials?.keywords : "Keywords"}</Label>
              <TagInput
                placeholder={typeof t.materials?.add_keywords === 'string' ? t.materials?.add_keywords : "Add keywords"}
                tags={formData.keywords}
                setTags={handleKeywordsChange}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="stage">{typeof t.materials?.stage === 'string' ? t.materials?.stage : "Stage"}</Label>
                <Select
                  value={formData.stage}
                  onValueChange={(value) => handleSelectChange("stage", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={typeof t.materials?.select_stage === 'string' ? t.materials?.select_stage : "Select stage"} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={MaterialStage.IDEA}>{typeof t.materials?.stages?.idea === 'string' ? t.materials?.stages?.idea : "Idea"}</SelectItem>
                    <SelectItem value={MaterialStage.REFINEMENT}>{typeof t.materials?.stages?.refinement === 'string' ? t.materials?.stages?.refinement : "Refinement"}</SelectItem>
                    <SelectItem value={MaterialStage.FINALIZATION}>{typeof t.materials?.stages?.finalization === 'string' ? t.materials?.stages?.finalization : "Finalization"}</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="status">{typeof t.materials?.status_label === 'string' ? t.materials?.status_label : "Status"}</Label>
                <Select
                  value={formData.status}
                  onValueChange={(value) => handleSelectChange("status", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={typeof t.materials?.select_status === 'string' ? t.materials?.select_status : "Select status"} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={MaterialStatus.DRAFT}>{typeof t.materials?.status?.draft === 'string' ? t.materials?.status?.draft : "Draft"}</SelectItem>
                    <SelectItem value={MaterialStatus.IN_PROGRESS}>{typeof t.materials?.status?.in_progress === 'string' ? t.materials?.status?.in_progress : "In Progress"}</SelectItem>
                    <SelectItem value={MaterialStatus.READY_FOR_REVIEW}>{typeof t.materials?.status?.ready_for_review === 'string' ? t.materials?.status?.ready_for_review : "Ready for Review"}</SelectItem>
                    <SelectItem value={MaterialStatus.COMPLETED}>{typeof t.materials?.status?.completed === 'string' ? t.materials?.status?.completed : "Completed"}</SelectItem>
                    <SelectItem value={MaterialStatus.ARCHIVED}>{typeof t.materials?.status?.archived === 'string' ? t.materials?.status?.archived : "Archived"}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="mt-6 flex justify-end space-x-4">
          <Button
            variant="outline"
            type="button"
            onClick={() => router.push(`/${locale}/materials/${materialId}`)}
            disabled={isSaving}
          >
            {typeof t.common?.cancel === 'string' ? t.common?.cancel : "Cancel"}
          </Button>
          <Button type="submit" disabled={isSaving}>
            {isSaving ? (
              <>
                <span className="spinner-sm mr-2" />
                {typeof t.common?.saving === 'string' ? t.common?.saving : "Saving..."}
              </>
            ) : (
              typeof t.common?.save === 'string' ? t.common?.save : "Save Changes"
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
