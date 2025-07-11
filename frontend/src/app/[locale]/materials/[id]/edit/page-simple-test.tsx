"use client";

import React from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function MaterialEditPageSimple({
  params
}: {
  params: { locale: string; id: string }
}) {
  const router = useRouter();
  const locale = params.locale || "en";
  const materialId = params.id;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Edit Material: {materialId}</h1>
      <p>Locale: {locale}</p>
      <p>This is a test edit page to verify routing works.</p>
      <Link href={`/${locale}/materials`} className="text-blue-500 hover:underline">
        Back to Materials
      </Link>
    </div>
  );
}
