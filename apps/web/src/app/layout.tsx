import type { Metadata } from "next";
import Link from "next/link";
import { Geist, Geist_Mono } from "next/font/google";
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
  description: "Plataforma para convertir y comparar tasas.",
};

const navItems = [
  { href: "/", label: "Home" },
  { href: "/convertidor", label: "Convertidor" },
  { href: "/comparador", label: "Comparador" },
  { href: "/noticias", label: "Noticias" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-slate-50 text-slate-900`}>
        <header className="border-b border-slate-200 bg-white">
          <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-4">
            <p className="text-lg font-semibold">AnaDec</p>
            <nav className="flex items-center gap-4 text-sm">
              {navItems.map((item) => (
                <Link key={item.href} href={item.href} className="text-slate-700 hover:text-slate-900">
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>

        <main className="mx-auto w-full max-w-5xl px-6 py-10">{children}</main>
      </body>
    </html>
  );
}
