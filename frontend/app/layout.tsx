import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Senus PLC — Board Report",
  description: "AI-native Board Report platform for Senus PLC, built for Assiduous Corp.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans antialiased">{children}</body>
    </html>
  );
}
