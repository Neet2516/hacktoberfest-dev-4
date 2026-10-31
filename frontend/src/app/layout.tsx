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
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Host+Grotesk:wght@700;800;900&family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen text-black select-none antialiased">
        {children}
      </body>
    </html>
  );
}
