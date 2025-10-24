'use client';

import { AuthProvider } from '@/contexts/auth-context';
import { MainLayout } from '@/components/layouts/main-layout';

interface LocaleLayoutProps {
  children: React.ReactNode;
  params: {
    locale: string;
  };
}

export default function LocaleLayout({ children, params }: LocaleLayoutProps) {
  return (
    <AuthProvider>
      <MainLayout locale={params.locale}>
        {children}
      </MainLayout>
    </AuthProvider>
  );
}
