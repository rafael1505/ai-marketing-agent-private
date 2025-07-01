import AuthProtection from "@/components/layouts/auth-protection";

export default function AuthenticatedLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: { locale: string }
}) {
  return (
    <AuthProtection locale={params.locale}>
      {children}
    </AuthProtection>
  );
}
