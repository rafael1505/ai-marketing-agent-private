import { AuthProvider } from "@/contexts/auth-context";
import { MainLayout } from "@/components/layouts/main-layout";

export default function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: { locale: string }
}) {
  return (
    <AuthProvider> 
      <MainLayout locale={params.locale}>
        {children}
      </MainLayout>
    </AuthProvider> 
  );
}
