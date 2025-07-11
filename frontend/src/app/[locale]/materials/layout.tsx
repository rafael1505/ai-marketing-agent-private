export default function AuthenticatedLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: { locale: string }
}) {
  // Temporarily bypass auth protection for development
  return <>{children}</>;
}
