import Link from "next/link";
import { ArrowRight, Newspaper, RefreshCw, Scale } from "lucide-react";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";

export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-12 md:py-20">
      <div className="mx-auto mb-16 max-w-3xl text-center md:mb-24">
        <h1 className="mb-6 text-4xl text-gray-900 md:text-6xl">
          Convierte y compara tasas facilmente
        </h1>
        <p className="mb-10 text-xl text-gray-600 md:text-2xl">
          Entiende cuanto estas pagando o ganando sin formulas complicadas.
        </p>
        <div className="flex flex-col justify-center gap-4 sm:flex-row">
          <Link href="/convertidor">
            <Button
              size="lg"
              className="w-full rounded-xl bg-blue-600 px-8 py-6 text-lg text-white shadow-lg shadow-blue-200 hover:bg-blue-700 sm:w-auto"
            >
              Convertir una tasa
              <ArrowRight className="h-5 w-5" />
            </Button>
          </Link>
          <Link href="/comparador">
            <Button
              size="lg"
              variant="outline"
              className="w-full rounded-xl border-2 border-blue-600 px-8 py-6 text-lg text-blue-600 hover:bg-blue-50 sm:w-auto"
            >
              Comparar tasas
            </Button>
          </Link>
        </div>
      </div>

      <div className="mx-auto grid max-w-6xl gap-8 md:grid-cols-3">
        <Link href="/convertidor" className="group">
          <Card className="h-full rounded-2xl border-0 bg-white p-8 shadow-lg transition-all duration-300 group-hover:shadow-xl">
            <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-100 transition-colors group-hover:bg-blue-200">
              <RefreshCw className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="mb-3 text-2xl text-gray-900">Convertidor de tasas</h3>
            <p className="text-lg leading-relaxed text-gray-600">Pasa de una tasa a otra en segundos.</p>
          </Card>
        </Link>

        <Link href="/comparador" className="group">
          <Card className="h-full rounded-2xl border-0 bg-white p-8 shadow-lg transition-all duration-300 group-hover:shadow-xl">
            <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-green-100 transition-colors group-hover:bg-green-200">
              <Scale className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="mb-3 text-2xl text-gray-900">Comparador</h3>
            <p className="text-lg leading-relaxed text-gray-600">Descubre cual opcion te conviene mas.</p>
          </Card>
        </Link>

        <Link href="/noticias" className="group">
          <Card className="h-full rounded-2xl border-0 bg-white p-8 shadow-lg transition-all duration-300 group-hover:shadow-xl">
            <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-teal-100 transition-colors group-hover:bg-teal-200">
              <Newspaper className="h-8 w-8 text-teal-600" />
            </div>
            <h3 className="mb-3 text-2xl text-gray-900">Noticias</h3>
            <p className="text-lg leading-relaxed text-gray-600">Informacion clara sobre lo que afecta tu dinero.</p>
          </Card>
        </Link>
      </div>
    </div>
  );
}
