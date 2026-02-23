"use client";

import { useMemo, useState } from "react";
import { ArrowRight } from "lucide-react";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";

type NewsCategory = "tasas" | "economia" | "ahorro" | "all";

type NewsItem = {
  id: number;
  title: string;
  summary: string;
  category: NewsCategory;
  date: string;
};

const newsData: NewsItem[] = [
  {
    id: 1,
    title: "Tasas de interés: Lo que debes saber este mes",
    summary: "El banco central mantiene tasas estables. Te explicamos qué significa para tus créditos y ahorros.",
    category: "tasas",
    date: "22 Feb 2026",
  },
  {
    id: 2,
    title: "5 consejos simples para ahorrar más este año",
    summary: "Estrategias prácticas que puedes aplicar hoy mismo sin complicaciones ni fórmulas difíciles.",
    category: "ahorro",
    date: "20 Feb 2026",
  },
  {
    id: 3,
    title: "Cómo funciona la inflación y por qué te importa",
    summary: "Entender la inflación es más simple de lo que crees. Te lo explicamos de forma clara.",
    category: "economia",
    date: "18 Feb 2026",
  },
  {
    id: 4,
    title: "Comparar tasas antes de pedir un crédito",
    summary: "Un pequeño cambio en la tasa puede significar miles de pesos. Te mostramos cómo comparar.",
    category: "tasas",
    date: "15 Feb 2026",
  },
  {
    id: 5,
    title: "El impacto de las tasas en tu presupuesto mensual",
    summary: "Entiende cómo las tasas de interés afectan directamente tu bolsillo cada mes.",
    category: "economia",
    date: "12 Feb 2026",
  },
  {
    id: 6,
    title: "Ahorrar vs. Invertir: ¿Cuál es la diferencia?",
    summary: "Descubre las diferencias básicas y cuál opción puede ser mejor para ti según tu situación.",
    category: "ahorro",
    date: "10 Feb 2026",
  },
];

export default function NoticiasPage() {
  const [activeCategory, setActiveCategory] = useState<NewsCategory>("all");

  const filteredNews = useMemo(
    () => (activeCategory === "all" ? newsData : newsData.filter((item) => item.category === activeCategory)),
    [activeCategory],
  );

  const getCategoryColor = (category: NewsCategory) => {
    if (category === "tasas") return "bg-blue-100 text-blue-700";
    if (category === "economia") return "bg-green-100 text-green-700";
    if (category === "ahorro") return "bg-teal-100 text-teal-700";
    return "bg-gray-100 text-gray-700";
  };

  return (
    <div className="container mx-auto px-4 py-8 md:py-12">
      <div className="mx-auto max-w-6xl">
        <div className="mb-10 text-center">
          <h1 className="mb-4 text-3xl text-gray-900 md:text-5xl">Noticias</h1>
          <p className="text-lg text-gray-600">Informacion clara sobre lo que afecta tu dinero</p>
        </div>

        <div className="mb-12 flex flex-wrap justify-center gap-3">
          <Button onClick={() => setActiveCategory("all")} variant={activeCategory === "all" ? "primary" : "outline"} className={`rounded-full px-6 ${activeCategory === "all" ? "bg-blue-600 hover:bg-blue-700" : "border-2 hover:bg-gray-50"}`}>
            Todas
          </Button>
          <Button onClick={() => setActiveCategory("tasas")} variant={activeCategory === "tasas" ? "primary" : "outline"} className={`rounded-full px-6 ${activeCategory === "tasas" ? "bg-blue-600 hover:bg-blue-700" : "border-2 hover:bg-gray-50"}`}>
            Tasas
          </Button>
          <Button onClick={() => setActiveCategory("economia")} variant={activeCategory === "economia" ? "primary" : "outline"} className={`rounded-full px-6 ${activeCategory === "economia" ? "bg-green-600 hover:bg-green-700" : "border-2 hover:bg-gray-50"}`}>
            Economía
          </Button>
          <Button onClick={() => setActiveCategory("ahorro")} variant={activeCategory === "ahorro" ? "primary" : "outline"} className={`rounded-full px-6 ${activeCategory === "ahorro" ? "bg-teal-600 hover:bg-teal-700" : "border-2 hover:bg-gray-50"}`}>
            Ahorro
          </Button>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredNews.map((item) => (
            <Card key={item.id} className="group overflow-hidden rounded-2xl border-0 shadow-lg transition-all duration-300 hover:shadow-xl">
              <div className="aspect-video overflow-hidden bg-gray-100">
                <img
                  src="https://images.unsplash.com/photo-1554224311-beee460ae6fb?w=600&h=400&fit=crop"
                  alt={item.title}
                  className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
              </div>
              <div className="p-6">
                <div className="mb-3 flex items-center gap-2">
                  <span className={`rounded-full px-2 py-1 text-xs font-medium ${getCategoryColor(item.category)}`}>
                    {item.category.charAt(0).toUpperCase() + item.category.slice(1)}
                  </span>
                  <span className="text-sm text-gray-500">{item.date}</span>
                </div>
                <h3 className="mb-3 text-xl leading-tight text-gray-900">{item.title}</h3>
                <p className="mb-4 line-clamp-2 text-gray-600">{item.summary}</p>
                <Button variant="ghost" className="px-0 text-blue-600 hover:bg-blue-50 hover:text-blue-700">
                  Leer más
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </Card>
          ))}
        </div>

        {filteredNews.length === 0 && (
          <div className="py-12 text-center">
            <p className="text-xl text-gray-500">No hay noticias en esta categoría</p>
          </div>
        )}
      </div>
    </div>
  );
}
