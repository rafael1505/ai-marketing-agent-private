"use client";

import { getTranslations } from "@/i18n";
import { LoginForm } from "@/components/forms/login-form";
import { useEffect } from "react";

export default function LoginPage({
  params
}: {
  params: { locale: string }
}) {
  const locale = params.locale || "en";
  const t = getTranslations(locale === "pt" ? "pt" : "en");
  
  useEffect(() => {
    // Import our style debugger client-side
    import('@/lib/style-debugger');
  }, []);
  return (
    <div className="flex min-h-screen flex-col items-center justify-center py-12 directFadeIn">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h1 
          className="text-center text-3xl font-bold tracking-tight directGradientText"
          style={{
            background: "linear-gradient(90deg, #3B82F6, #A855F7)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
            color: "transparent"
          }}
        >
          {t.app.title}
        </h1>
        <h2 className="mt-2 text-center text-sm text-gray-500">
          {t.app.description}
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <LoginForm locale={locale} />
      </div>
    </div>
  );
}
