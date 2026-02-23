"use client";

import { useEffect, useMemo, useState } from "react";
import { ArrowRight } from "lucide-react";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { apiGet } from "@/lib/api";

type NewsCategory = "tasas" | "economia" | "ahorro" | "all";

type NewsItem = {
  title: string;
  summary: string;
  source: string;
  date: string;
  url: string;
};

type NewsResponse = {
  items: NewsItem[];
  stale: boolean;
  generated_at?: string;
};

export default function NoticiasPage() {
  const [activeCategory, setActiveCategory] = useState<NewsCategory>("all");
  const [news, setNews] = useState<NewsItem[]>([]);
  const [stale, setStale] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const fetchNews = async () => {
      setLoading(true);
      setError(null);
      try {
        const query = activeCategory === "all" ? "" : `?category=${encodeURIComponent(activeCategory)}`;
        const data = await apiGet<NewsResponse>(`/api/news${query}`);
        if (!cancelled) {
          setNews(data.items ?? []);
          setStale(Boolean(data.stale));
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "No se pudieron cargar las noticias.");
          setNews([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchNews();
    return () => {
      cancelled = true;
    };
  }, [activeCategory]);

  const filteredNews = useMemo(() => news, [news]);

  const getCategoryColor = (category: NewsCategory) => {
    if (category === "tasas") return "bg-blue-100 text-blue-700";
    if (category === "economia") return "bg-green-100 text-green-700";
    if (category === "ahorro") return "bg-teal-100 text-teal-700";
    return "bg-gray-100 text-gray-700";
  };

  const currentCategoryLabel = (item: NewsItem): NewsCategory => {
    const t = `${item.title} ${item.summary}`.toLowerCase();
    if (t.includes("tasa") || t.includes("credito")) return "tasas";
    if (t.includes("ahorro") || t.includes("invert")) return "ahorro";
    return "economia";
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

        {loading ? <p className="mb-6 text-center text-gray-500">Cargando noticias...</p> : null}
        {error ? <p className="mb-6 text-center text-red-600">{error}</p> : null}
        {stale ? <p className="mb-6 text-center text-amber-700">Mostrando caché temporal por indisponibilidad de fuente.</p> : null}

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredNews.map((item, idx) => {
            const category = currentCategoryLabel(item);
            return (
              <Card key={`${item.title}-${idx}`} className="group overflow-hidden rounded-2xl border-0 shadow-lg transition-all duration-300 hover:shadow-xl">
                <div className="aspect-video overflow-hidden bg-gray-100">
                  <img
                    src="https://images.unsplash.com/photo-1554224311-beee460ae6fb?w=600&h=400&fit=crop"
                    alt={item.title}
                    className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                </div>
                <div className="p-6">
                  <div className="mb-3 flex items-center gap-2">
                    <span className={`rounded-full px-2 py-1 text-xs font-medium ${getCategoryColor(category)}`}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </span>
                    <span className="text-sm text-gray-500">{item.date || "Sin fecha"}</span>
                  </div>
                  <h3 className="mb-3 text-xl leading-tight text-gray-900">{item.title}</h3>
                  <p className="mb-2 line-clamp-2 text-gray-600">{item.summary}</p>
                  <p className="mb-4 text-sm text-gray-500">Fuente: {item.source || "N/A"}</p>
                  <a
                    href={item.url || "#"}
                    target={item.url ? "_blank" : undefined}
                    rel={item.url ? "noreferrer" : undefined}
                  >
                    <Button variant="ghost" className="px-0 text-blue-600 hover:bg-blue-50 hover:text-blue-700">
                      Leer más
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </a>
                </div>
              </Card>
            );
          })}
        </div>

        {!loading && !error && filteredNews.length === 0 && (
          <div className="py-12 text-center">
            <p className="text-xl text-gray-500">No hay noticias en esta categoría</p>
          </div>
        )}
      </div>
    </div>
  );
}
