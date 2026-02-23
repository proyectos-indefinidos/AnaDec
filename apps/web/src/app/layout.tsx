import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import BackToHome from "@/components/BackToHome";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AnaDec",
  description: "Convierte y compara tasas facilmente.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body
        className={`${geistSans.variable} ${geistMono.variable} min-h-screen bg-gradient-to-b from-blue-50 to-green-50 text-slate-900 antialiased`}
      >
        <BackToHome />
        {children}
      </body>
    </html>
  );
}
