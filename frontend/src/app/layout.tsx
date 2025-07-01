import type { Metadata, Viewport } from "next";
import "./globals.css";
import "./custom-styles.css";
import "./direct-styles.css"; // Add direct CSS that doesn't rely on CSS modules

// Use system fonts instead of Google Fonts to avoid network issues
const fontConfig = {
  variable: "--font-inter",
  className: "font-system",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#3B82F6",
};

export const metadata: Metadata = {
  title: "AI Marketing Agent",
  description: "Generate marketing materials with AI assistance",
  keywords: ["AI", "Marketing", "Content Generation", "Automation"],
  authors: [{ name: "AI Marketing Team" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${fontConfig.variable} font-sans antialiased`}>
        <a href="#main-content" className="skip-to-content">Skip to content</a>
        <div id="root-container">
          {children}
        </div>
        
        {/* Include debug auth script only in development */}
        {process.env.NODE_ENV === 'development' && (
          <script src="/debug-auth.js" defer async></script>
        )}
      </body>
    </html>
  );
}
