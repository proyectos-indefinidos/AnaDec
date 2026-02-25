import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import Link from "next/link";

import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  variable: "--font-jakarta",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AnaDec | Herramientas Financieras y Comparador",
  description: "Convierte tasas de interés y compara los mejores créditos y CDTs del mercado colombiano. Toma el control de tus finanzas fácilmente.",
  keywords: "convertidor de tasas, comparar créditos colombia, efectiva anual, finanzas personales, calculadora financiera",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body
        
        className={`${jakarta.variable} font-sans min-h-screen bg-brand-bg text-brand-text antialiased flex flex-col`}
      >
        
        {/* Header */}
        <header className="bg-white border-b border-brand-pale shadow-soft sticky top-0 z-50">
          <div className="container mx-auto px-4 h-16 flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold text-brand-dark tracking-tight">
              Ana<span className="text-brand-action">Dec</span>
            </Link>
            <nav className="hidden md:flex gap-6 font-medium text-brand-slate">
              <Link href="/" className="hover:text-brand-action transition-colors">Inicio</Link>
              <Link href="/convertidor" className="hover:text-brand-action transition-colors">Convertidor</Link>
              <Link href="/comparador" className="hover:text-brand-action transition-colors">Comparador</Link>
            </nav>
          </div>
        </header>

        <main className="flex-1 flex flex-col">
          {children}
        </main>

        {/*footer*/}
          <footer className="bg-brand-jet text-white py-8 mt-auto">
          <div className="container mx-auto px-4 text-center">
            <p className="text-brand-pale text-lg font-bold mb-2">AnaDec</p>
            <p className="text-sm text-gray-300">
              Ingeniería financiera simplificada para el mundo real.
            </p>
            <p className="text-xs text-gray-400 mt-4">
              © {new Date().getFullYear()} Todos los derechos reservados.
            </p>
          </div>
        </footer>

      </body>
    </html>
  );
}