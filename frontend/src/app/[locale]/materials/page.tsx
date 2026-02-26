"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { getTranslations } from "@/i18n";
import { Button } from "@/components/ui/button";
import { getMaterials, deleteMaterial } from "@/services/materials";
import { Material, MaterialStage, MaterialStatus } from "@/types";
import { MaterialCard } from "@/components/ui/material-card";

export default function MaterialsPage({
  params
}: {
  params: { locale: string }
}) {
  const locale = params.locale || "en";
  const [t, setT] = useState<Record<string, any>>({});
  const [translationsLoaded, setTranslationsLoaded] = useState(false);  const [materials, setMaterials] = useState<Material[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isRefreshing, setIsRefreshing] = useState(false);
  const loadingGuardRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const fetchCompletedRef = useRef(false);

  useEffect(() => {
    const loadTranslations = async () => {
      try {
        const translations = await getTranslations(locale === "pt" ? "pt" : "en");
        setT(translations);
        setTranslationsLoaded(true);
      } catch {
        setT({
          errors: { server_error: "Server error. Please try again later." },
          common: { loading: "Loading..." }
        });
        setTranslationsLoaded(true);
      }
    };
    loadTranslations();
  }, [locale]);

  const fetchMaterials = async (forceRefresh = false) => {
    fetchCompletedRef.current = false;
    if (loadingGuardRef.current) {
      clearTimeout(loadingGuardRef.current);
      loadingGuardRef.current = null;
    }

    if (forceRefresh) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }

    const LOADING_MAX_MS = 30000; // 30s cap per FR-007
    loadingGuardRef.current = setTimeout(() => {
      loadingGuardRef.current = null;
      if (fetchCompletedRef.current) return;
      setError("Request took too long. Please try again.");
      setMaterials([]);
      setIsLoading(false);
      setIsRefreshing(false);
    }, LOADING_MAX_MS);

    try {
      const data = await getMaterials(undefined, undefined, 0, 100, forceRefresh);
      if (Array.isArray(data)) {
        setMaterials(data);
      } else {
        setMaterials([]);
      }
      setError("");
    } catch {
      setError("Unable to load materials. Please try again later.");
      setMaterials([]);
    } finally {
      fetchCompletedRef.current = true;
      if (loadingGuardRef.current) {
        clearTimeout(loadingGuardRef.current);
        loadingGuardRef.current = null;
      }
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  // Effect to fetch materials when translations are loaded
  useEffect(() => {
    if (Object.keys(t).length > 0) {
      fetchMaterials();
    }
  }, [t]);

  // Clear loading guard timer on unmount to prevent memory leaks and setState after unmount (005 verification)
  useEffect(() => {
    return () => {
      if (loadingGuardRef.current) {
        clearTimeout(loadingGuardRef.current);
        loadingGuardRef.current = null;
      }
    };
  }, []);

  // Handle delete material
  const handleDeleteMaterial = async (id: string) => {
    try {
      await deleteMaterial(id);
      await fetchMaterials(true);
    } catch {
      setError(t.materials?.delete_error || "Failed to delete material. Please try again.");
    }
  };

  // Show loading if translations aren't loaded yet or data is being fetched
  if (!translationsLoaded || (isLoading && Object.keys(t).length === 0)) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="spinner" />
        <span className="ml-2">Loading...</span>
      </div>
    );
  }

  if (!t.nav || !t.materials || !t.common) {
    return (
      <div className="flex justify-center items-center py-12 text-red-500">
        <p>Error loading page content. Please refresh the page.</p>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">{t.nav.materials}</h1>
        <div className="flex gap-2">
          {isRefreshing && (
            <div className="text-xs flex items-center text-gray-500">
              <div className="spinner-sm mr-1" />
              Refreshing...
            </div>
          )}
          <Button variant="outline" size="icon" onClick={() => fetchMaterials(true)} disabled={isRefreshing}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 2v6h-6"></path>
              <path d="M3 12a9 9 0 0 1 15-6.7L21 8"></path>
              <path d="M3 22v-6h6"></path>
              <path d="M21 12a9 9 0 0 1-15 6.7L3 16"></path>
            </svg>
            <span className="sr-only">Refresh</span>
          </Button>
          <Button asChild>
            <Link href={`/${locale}/materials/create`}>
              {t.materials.create}
            </Link>
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center py-12">
          <div className="spinner" />
          <span className="ml-2">{t.common.loading}</span>
        </div>      ) : error ? (
        <div className="text-center py-12">
          <div className="text-red-500 mb-4">
            <h2 className="text-xl font-bold">{error.includes("connection") ? "Connection Error" : error.includes("too long") ? "Request Timeout" : "Server Error"}</h2>
            <p>{error}</p>
          </div>
          <Button onClick={() => { setError(""); fetchMaterials(true); }} disabled={isRefreshing}>
            {t.common && t.common.retry ? t.common.retry : "Retry"}
          </Button>
        </div>
      ) : materials.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          {t.materials.empty}
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {materials.map((material) => (
            <MaterialCard 
              key={material.id} 
              material={material} 
              locale={locale}
              onDelete={handleDeleteMaterial}
            />
          ))}
        </div>
      )}
    </div>
  );
}
