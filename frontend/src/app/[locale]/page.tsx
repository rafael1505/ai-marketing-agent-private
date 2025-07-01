"use client";

// import { getTranslations } from "@/i18n";
import Link from "next/link";
import { Button } from "@/components/ui/button";
// import { useEffect, useState } from 'react';

export default function LocaleHomePage({
  params
}: {
  params: { locale: string }
}) {
  const locale = params.locale || "en";
  // const [translations, setTranslations] = useState<any>(null);
  
  // useEffect(() => {
  //   // Get translations on the client side
  //   const t = getTranslations(locale === "pt" ? "pt" : "en");
  //   setTranslations(t);
  // }, [locale]);

  // // Show loading state while translations are being loaded
  // if (!translations) {
  //   return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  // }

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] text-center px-4 fade-in">
      {/* <h1 className="text-4xl font-bold tracking-tight mb-4 bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">{translations.app.title}</h1> */}
      {/* <p className="text-xl text-muted-foreground mb-8 max-w-2xl">
        {translations.app.description}
      </p> */}
      <h1 className="text-4xl font-bold tracking-tight mb-4 bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">Welcome</h1>
      <p className="text-xl text-muted-foreground mb-8 max-w-2xl">
        This is a test page.
      </p>
      <div className="flex flex-col sm:flex-row gap-4">
        <Button asChild size="lg">
          <Link href={`/${locale}/login`}>
            {/* {translations.login.title} */}
            Login
          </Link>
        </Button>
        <Button asChild variant="outline" size="lg">
          <Link href={`/${locale}/dashboard`}>
            {/* {translations.nav.dashboard} */}
            Dashboard
          </Link>
        </Button>
      </div>
    </div>
  );
}
