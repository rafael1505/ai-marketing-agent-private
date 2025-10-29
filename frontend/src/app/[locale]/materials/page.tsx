"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { getTranslations } from "@/i18n";
import { Button } from "@/components/ui/button";
import { getMaterials } from "@/services/materials";
import { Material, MaterialStage, MaterialStatus } from "@/types";
import { MaterialCard } from "@/components/ui/material-card";

// Edge compatibility debug (only in development)
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  console.log('=== Materials Page - Edge Compatibility Check ===');
  console.log('User Agent:', navigator.userAgent);
  console.log('Location:', window.location.href);
  console.log('localStorage available:', typeof localStorage !== 'undefined');
}

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
  }, [locale]);  // Function to fetch materials that can be called on demand
  const fetchMaterials = async (forceRefresh = false) => {
    console.log('[Materials Page] fetchMaterials called, forceRefresh:', forceRefresh);
    
    if (forceRefresh) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    
    try {
      console.log('[Materials Page] Calling getMaterials...');
      const data = await getMaterials(undefined, undefined, 0, 100, forceRefresh);
      console.log('[Materials Page] getMaterials returned:', data);
      console.log('[Materials Page] Data is array?', Array.isArray(data));
      console.log('[Materials Page] Data length:', data?.length);
      
      // Defensive check: ensure data is an array
      if (Array.isArray(data)) {
        console.log('[Materials Page] Setting materials state with', data.length, 'items');
        setMaterials(data);
      } else {
        console.error('[Materials Page] getMaterials returned non-array data:', data);
        setMaterials([]); // Set empty array as fallback
      }
      
      setError(""); // Clear any previous errors
    } catch (err) {
      console.error("[Materials Page] Error fetching materials:", err);
      setError("Unable to load materials. Please try again later.");
      setMaterials([]); // Set empty array on error
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  // Effect to fetch materials when translations are loaded
  useEffect(() => {
    // Only fetch if translations are loaded
    if (Object.keys(t).length > 0) {
      fetchMaterials();
    }
  }, [t]); // Use t as dependency
  // Show loading if translations aren't loaded yet or data is being fetched
  if (!translationsLoaded || (isLoading && Object.keys(t).length === 0)) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="spinner" />
        <span className="ml-2">Loading...</span>
      </div>
    );
  }

  // Make sure translations are loaded before rendering
  if (!t.nav || !t.materials || !t.common) {
    console.error("Translation keys are missing", t);
    return (
      <div className="flex justify-center items-center py-12 text-red-500">
        <p>Error loading page content. Please refresh the page.</p>
      </div>
    );
  }
  
  // Check if we're in demo/mock mode (this happens when the backend has DB issues)
  // Defensive check: ensure materials is an array before calling .some()
  const isDemoMode = Array.isArray(materials) && materials.some(mat => mat.api_error === true);

  return (
    <div className="space-y-6">
      {isDemoMode && (
        <div className="bg-blue-50 p-3 rounded border border-blue-200 text-blue-800 text-sm mb-4">
          <div className="flex items-center mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2h-1V9z" clipRule="evenodd" />
            </svg>
            <strong>Demo Mode Active</strong>
          </div>
          <p>You're seeing demo materials for development and testing purposes.</p>
        </div>
      )}

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
            <h2 className="text-xl font-bold">{error.includes("connection") ? "Connection Error" : "Server Error"}</h2>
            <p>{error}</p>
          </div>
          <Button onClick={() => window.location.reload()}>
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
            />
          ))}
        </div>
      )}
    </div>
  );
}
