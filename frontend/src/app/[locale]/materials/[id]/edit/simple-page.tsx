"use client";

import React from "react";
import Link from "next/link";

export default function SimpleEditPage({
  params
}: {
  params: { locale: string; id: string }
}) {
  const { locale, id } = params;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Edit Material</h1>
      <p>Locale: {locale}</p>
      <p>Material ID: {id}</p>
      <Link href={`/${locale}/materials/${id}`} className="text-blue-500 underline">
        Back to Material
      </Link>
    </div>
  );
}
