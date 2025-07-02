"use client";

import React, { useEffect, useState } from "react";
import { getMaterial } from "@/services/materials";
import { Material } from "@/types";

export default function MaterialDetailPage({
  params
}: {
  params: { locale: string; id: string }
}) {
  console.log('🔥 SIMPLE DEBUG: Component started');
  const materialId = params.id;
  const [material, setMaterial] = useState<Material | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    console.log('🔥 SIMPLE DEBUG: useEffect triggered');
    const fetchMaterial = async () => {
      try {
        console.log('🔥 SIMPLE DEBUG: Fetching material:', materialId);
        const data = await getMaterial(materialId);
        console.log('🔥 SIMPLE DEBUG: Material received:', data);
        console.log('🔥 SIMPLE DEBUG: Has api_error?', data.api_error);
        setMaterial(data);
      } catch (error) {
        console.error('🔥 SIMPLE DEBUG: Error:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchMaterial();
  }, [materialId]);

  console.log('🔥 SIMPLE DEBUG: Rendering with material:', material);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!material) {
    return <div>Material not found</div>;
  }

  if (material.api_error) {
    console.log('🔥 SIMPLE DEBUG: Showing connection error because api_error =', material.api_error);
    return (
      <div style={{ padding: '2rem', backgroundColor: '#ffe6e6', border: '2px solid red' }}>
        <h2 style={{ color: 'red' }}>Connection Error</h2>
        <p>{material.description}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h1>{material.title}</h1>
      <p>{material.description}</p>
      <p><strong>Stage:</strong> {material.stage}</p>
      <p><strong>Status:</strong> {material.status}</p>
      <p><strong>API Error:</strong> {String(material.api_error)}</p>
    </div>
  );
}
