"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ArrowLeft } from "lucide-react";

export default function BackToHome() {
  const pathname = usePathname();

  if (pathname === "/") return null;

  return (
    <div className="container mx-auto px-4 py-6">
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-blue-600 transition-colors hover:text-blue-700"
      >
        <ArrowLeft className="h-5 w-5" />
        <span>Volver al inicio</span>
      </Link>
    </div>
  );
}
