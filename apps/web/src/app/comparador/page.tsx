"use client";

import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { CheckCircle, ChevronDown, Plus, Scale, TrendingUp, X } from "lucide-react";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { apiPost } from "@/lib/api";

type ApiRateType = "EFFECTIVE" | "NOMINAL";
type ApiPeriod = "MONTHLY" | "QUARTERLY" | "SEMIANNUAL" | "ANNUAL";

type RateSpec = {
  value: number;
  rate_type: ApiRateType;
  period: ApiPeriod;
  nominal_capitalization_period?: ApiPeriod;
};

type CompareRequest = {
  option_a_name: string;
  option_a: RateSpec;
  option_b_name: string;
  option_b: RateSpec;
};

type CompareResponse = {
  winner: "A" | "B" | "TIE";
  effective_annual_a: number;
  effective_annual_b: number;
  difference: number;
  summary: string;
  details: string[];
};

const RATE_TYPE_OPTIONS: { value: ApiRateType; label: string }[] = [
  { value: "EFFECTIVE", label: "Efectiva" },
  { value: "NOMINAL", label: "Nominal" },
];

const PERIOD_OPTIONS: { value: ApiPeriod; label: string }[] = [
  { value: "MONTHLY", label: "Mensual" },
  { value: "QUARTERLY", label: "Trimestral" },
  { value: "SEMIANNUAL", label: "Semestral" },
  { value: "ANNUAL", label: "Anual" },
];

const colors = [
  { bg: "bg-blue-100", border: "border-blue-200", text: "text-blue-600", chart: "#3b82f6" },
  { bg: "bg-green-100", border: "border-green-200", text: "text-green-600", chart: "#10b981" },
  { bg: "bg-purple-100", border: "border-purple-200", text: "text-purple-600", chart: "#a855f7" },
  { bg: "bg-orange-100", border: "border-orange-200", text: "text-orange-600", chart: "#f97316" },
  { bg: "bg-pink-100", border: "border-pink-200", text: "text-pink-600", chart: "#ec4899" },
  { bg: "bg-teal-100", border: "border-teal-200", text: "text-teal-600", chart: "#14b8a6" },
];

type RateInput = {
  id: string;
  value: string;
  name: string;
  rate_type: ApiRateType;
  period: ApiPeriod;
  nominal_capitalization_period: ApiPeriod;
};

type ResultRate = {
  id: string;
  name: string;
  effective: number;
  original: number;
  type: string;
};

function toRateSpec(rate: RateInput): RateSpec {
  return {
    value: parseFloat(rate.value),
    rate_type: rate.rate_type,
    period: rate.period,
    ...(rate.rate_type === "NOMINAL"
      ? { nominal_capitalization_period: rate.nominal_capitalization_period }
      : {}),
  };
}

function typeLabel(rate: RateInput): string {
  const t = RATE_TYPE_OPTIONS.find((x) => x.value === rate.rate_type)?.label ?? rate.rate_type;
  const p = PERIOD_OPTIONS.find((x) => x.value === rate.period)?.label ?? rate.period;
  if (rate.rate_type === "NOMINAL") {
    const cap = PERIOD_OPTIONS.find((x) => x.value === rate.nominal_capitalization_period)?.label ?? rate.nominal_capitalization_period;
    return `${t} ${p} (cap. ${cap})`;
  }
  return `${t} ${p}`;
}

export default function ComparadorPage() {
  const [rates, setRates] = useState<RateInput[]>([
    {
      id: "a",
      value: "",
      name: "Opción A",
      rate_type: "EFFECTIVE",
      period: "ANNUAL",
      nominal_capitalization_period: "MONTHLY",
    },
    {
      id: "b",
      value: "",
      name: "Opción B",
      rate_type: "EFFECTIVE",
      period: "MONTHLY",
      nominal_capitalization_period: "MONTHLY",
    },
  ]);

  const [showDetails, setShowDetails] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    rates: ResultRate[];
    bestIndex: number;
    summary: string;
    details: string[];
    difference: number;
  } | null>(null);

  const addRate = () => {
    if (rates.length >= 6) return;
    const letter = String.fromCharCode(65 + rates.length);
    setRates((prev) => [
      ...prev,
      {
        id: `${Date.now()}`,
        value: "",
        name: `Opción ${letter}`,
        rate_type: "EFFECTIVE",
        period: "ANNUAL",
        nominal_capitalization_period: "MONTHLY",
      },
    ]);
  };

  const removeRate = (id: string) => {
    if (rates.length <= 2) return;
    setRates((prev) => prev.filter((r) => r.id !== id));
  };

  const updateRate = <K extends keyof RateInput>(id: string, key: K, value: RateInput[K]) => {
    setRates((prev) => prev.map((r) => (r.id === id ? { ...r, [key]: value } : r)));
  };

  const growthData = useMemo(() => {
    if (!result) return [] as Array<Record<string, string | number>>;
    return [0, 1, 2, 3, 4, 5].map((year) => {
      const point: Record<string, string | number> = { year };
      result.rates.forEach((rate) => {
        point[rate.name] = (100 * Math.pow(1 + rate.effective / 100, year)).toFixed(2);
      });
      return point;
    });
  }, [result]);

  const onCompare = async () => {
    const valid = rates.filter((r) => !Number.isNaN(parseFloat(r.value)) && parseFloat(r.value) > 0);

    if (valid.length < 2) {
      setError("Agrega al menos 2 tasas válidas para comparar.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const base = valid[0];
      const eaById: Record<string, number> = {};
      const details: string[] = [];

      for (let i = 1; i < valid.length; i += 1) {
        const candidate = valid[i];

        const req: CompareRequest = {
          option_a_name: base.name,
          option_a: toRateSpec(base),
          option_b_name: candidate.name,
          option_b: toRateSpec(candidate),
        };

        const cmp = await apiPost<CompareResponse>("/api/compare", req);

        eaById[base.id] = cmp.effective_annual_a;
        eaById[candidate.id] = cmp.effective_annual_b;

        if (details.length === 0) details.push(...cmp.details);
      }

      const normalized: ResultRate[] = valid.map((r) => ({
        id: r.id,
        name: r.name,
        effective: eaById[r.id],
        original: parseFloat(r.value),
        type: typeLabel(r),
      }));

      if (normalized.some((r) => Number.isNaN(r.effective))) {
        throw new Error("No se pudo estimar EA para todas las opciones.");
      }

      const bestIndex = normalized.reduce(
        (best, curr, idx, arr) => (curr.effective < arr[best].effective ? idx : best),
        0,
      );

      const maxEA = Math.max(...normalized.map((r) => r.effective));
      const minEA = Math.min(...normalized.map((r) => r.effective));
      const difference = maxEA - minEA;

      setResult({
        rates: normalized,
        bestIndex,
        summary: `La opción ${normalized[bestIndex].name} es más conveniente por menor EA.`,
        details:
          details.length > 0
            ? details
            : [
                "Se validaron todas las tasas recibidas.",
                "Se estandarizaron las opciones a EA usando el backend.",
                "Se eligió la opción con menor EA.",
              ],
        difference,
      });
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : "No se pudo comparar las tasas.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 md:py-12">
      <div className="mx-auto max-w-6xl">
        <div className="mb-10 text-center">
          <h1 className="mb-4 text-3xl text-gray-900 md:text-5xl">Comparador de tasas</h1>
          <p className="text-lg text-gray-600">Compara varias tasas y descubre cual te conviene mas</p>
        </div>

        <div className="mb-8 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {rates.map((rate, index) => (
            <Card key={rate.id} className={`relative rounded-2xl border-2 p-6 shadow-lg ${colors[index % colors.length].border}`}>
              {rates.length > 2 && (
                <Button
                  onClick={() => removeRate(rate.id)}
                  variant="ghost"
                  size="sm"
                  className="absolute top-3 right-3 h-8 w-8 rounded-full p-0 hover:bg-red-100"
                >
                  <X className="h-4 w-4 text-red-600" />
                </Button>
              )}

              <div className="mb-6 flex items-center gap-3">
                <div className={`flex h-10 w-10 items-center justify-center rounded-full text-lg font-semibold ${colors[index % colors.length].bg} ${colors[index % colors.length].text}`}>
                  {String.fromCharCode(65 + index)}
                </div>
                <input
                  value={rate.name}
                  onChange={(e) => updateRate(rate.id, "name", e.target.value)}
                  className="h-auto w-full border-0 p-0 text-xl font-semibold outline-none"
                  placeholder="Nombre"
                />
              </div>

              <div className="space-y-3">
                <div className="relative">
                  <input
                    type="number"
                    step="0.01"
                    value={rate.value}
                    onChange={(e) => updateRate(rate.id, "value", e.target.value)}
                    className="w-full rounded-xl border border-slate-200 py-4 pr-12 pl-4 text-lg outline-none focus:border-blue-400"
                    placeholder="Tasa %"
                  />
                  <span className="absolute top-1/2 right-4 -translate-y-1/2 text-lg text-gray-400">%</span>
                </div>

                <select
                  value={rate.rate_type}
                  onChange={(e) => updateRate(rate.id, "rate_type", e.target.value as ApiRateType)}
                  className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base outline-none focus:border-blue-400"
                >
                  {RATE_TYPE_OPTIONS.map((type) => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>

                <select
                  value={rate.period}
                  onChange={(e) => updateRate(rate.id, "period", e.target.value as ApiPeriod)}
                  className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base outline-none focus:border-blue-400"
                >
                  {PERIOD_OPTIONS.map((period) => (
                    <option key={period.value} value={period.value}>{period.label}</option>
                  ))}
                </select>

                {rate.rate_type === "NOMINAL" && (
                  <select
                    value={rate.nominal_capitalization_period}
                    onChange={(e) =>
                      updateRate(rate.id, "nominal_capitalization_period", e.target.value as ApiPeriod)
                    }
                    className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base outline-none focus:border-blue-400"
                  >
                    {PERIOD_OPTIONS.map((period) => (
                      <option key={period.value} value={period.value}>Capitalización {period.label}</option>
                    ))}
                  </select>
                )}
              </div>
            </Card>
          ))}

          {rates.length < 6 && (
            <Card className="flex cursor-pointer items-center justify-center rounded-2xl border-2 border-dashed border-gray-300 bg-gray-50 p-6 shadow-lg transition-colors hover:bg-gray-100">
              <Button onClick={addRate} variant="ghost" className="h-full w-full flex-col gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-200">
                  <Plus className="h-6 w-6 text-gray-600" />
                </div>
                <span className="text-lg text-gray-600">Agregar tasa</span>
              </Button>
            </Card>
          )}
        </div>

        <div className="mb-8 text-center">
          <Button
            onClick={onCompare}
            disabled={loading}
            size="lg"
            className="rounded-xl bg-blue-600 px-12 py-6 text-lg text-white shadow-lg shadow-blue-200 hover:bg-blue-700"
          >
            <Scale className="h-5 w-5" />
            {loading ? "Comparando..." : "Comparar"}
          </Button>
          {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
        </div>

        {result && (
          <div className="space-y-8">
            <Card className="rounded-2xl border-0 bg-gradient-to-r from-blue-50 to-green-50 p-8 shadow-xl">
              <div className="mb-6 text-center">
                <CheckCircle className="mx-auto mb-4 h-16 w-16 text-green-600" />
                <h3 className="mb-2 text-2xl text-gray-900 md:text-3xl">
                  {result.rates[result.bestIndex].name} es la más económica
                </h3>
                <p className="text-xl text-gray-600">{result.summary}</p>
              </div>

              <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
                {result.rates.map((rate, index) => (
                  <div key={rate.id} className={`rounded-xl bg-white p-4 text-center ${index === result.bestIndex ? "ring-2 ring-green-500" : ""}`}>
                    <p className="mb-1 text-sm text-gray-600">{rate.name}</p>
                    <p className={`text-2xl ${colors[index % colors.length].text}`}>{rate.effective.toFixed(4)}%</p>
                    <p className="mt-1 text-xs text-gray-500">efectiva anual</p>
                  </div>
                ))}
              </div>

              <button onClick={() => setShowDetails((v) => !v)} className="mx-auto flex items-center justify-center gap-2 text-blue-600 hover:text-blue-700">
                <span>¿Cómo se hizo la comparación?</span>
                <ChevronDown className={`h-4 w-4 transition-transform ${showDetails ? "rotate-180" : ""}`} />
              </button>

              {showDetails && (
                <div className="mt-4 rounded-xl bg-white p-6 text-gray-600">
                  {result.details.map((line, idx) => (
                    <p key={`${line}-${idx}`} className="mb-2">• {line}</p>
                  ))}
                  <p className="mt-2 text-sm">Diferencia entre mejor y peor: {result.difference.toFixed(6)} puntos porcentuales.</p>
                </div>
              )}
            </Card>

            <Card className="rounded-2xl border-0 bg-white p-6 shadow-xl md:p-8">
              <div className="mb-6 flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-blue-600" />
                <h3 className="text-2xl text-gray-900">Comparación de tasas efectivas</h3>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={result.rates}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip formatter={(value: number) => `${Number(value).toFixed(4)}%`} />
                  <Bar dataKey="effective" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card className="rounded-2xl border-0 bg-white p-6 shadow-xl md:p-8">
              <h3 className="mb-2 text-2xl text-gray-900">Proyección: Crecimiento de $100 a través del tiempo</h3>
              <p className="mb-6 text-gray-600">Así crecería tu dinero con cada tasa si inviertes $100 hoy</p>
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={growthData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="year" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip formatter={(value: number | string) => `$${Number(value).toFixed(2)}`} />
                  <Legend />
                  {result.rates.map((rate, index) => (
                    <Line
                      key={rate.id}
                      type="monotone"
                      dataKey={rate.name}
                      stroke={colors[index % colors.length].chart}
                      strokeWidth={3}
                      dot={{ r: 5 }}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
