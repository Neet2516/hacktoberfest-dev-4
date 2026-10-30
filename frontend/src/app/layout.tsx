import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SPECTER — The Ghost Maintainer [Hacktoberfest 2026]",
  description:
    "Autonomous multi-agent system for resurrecting abandoned open-source repositories.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen text-black select-none antialiased">
        {children}
      </body>
    </html>
  );
}
