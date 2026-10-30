import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SPECTER — The Ghost Maintainer",
  description: "Autonomous multi-agent AI system for resurrecting abandoned open-source repositories.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
