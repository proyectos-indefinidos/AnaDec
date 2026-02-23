"use client";

import { useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CheckCircle, ChevronDown, Plus, Scale, TrendingUp, X } from "lucide-react";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";

type RateType = "ea" | "nm" | "na" | "em" | "et";

const rateTypes: { value: RateType; label: string }[] = [
  { value: "ea", label: "Efectiva anual" },
  { value: "em", label: "Efectiva mensual" },
  { value: "et", label: "Efectiva trimestral" },
  { value: "na", label: "Nominal anual" },
  { value: "nm", label: "Nominal mensual" },
];

type Rate = {
  id: string;
  value: string;
  type: RateType;
  name: string;
};

const colors = [
  { bg: "bg-blue-100", border: "border-blue-200", text: "text-blue-600", chart: "#3b82f6" },
  { bg: "bg-green-100", border: "border-green-200", text: "text-green-600", chart: "#10b981" },
  { bg: "bg-purple-100", border: "border-purple-200", text: "text-purple-600", chart: "#a855f7" },
  { bg: "bg-orange-100", border: "border-orange-200", text: "text-orange-600", chart: "#f97316" },
  { bg: "bg-pink-100", border: "border-pink-200", text: "text-pink-600", chart: "#ec4899" },
  { bg: "bg-teal-100", border: "border-teal-200", text: "text-teal-600", chart: "#14b8a6" },
];

export default function ComparadorPage() {
  const [rates, setRates] = useState<Rate[]>([
    { id: "1", value: "", type: "ea", name: "Opción A" },
    { id: "2", value: "", type: "em", name: "Opción B" },
  ]);
  const [showDetails, setShowDetails] = useState(false);
  const [result, setResult] = useState<{
    rates: Array<{ name: string; effective: number; original: number; type: string }>;
    bestIndex: number;
  } | null>(null);

  const toEffectiveAnnual = (rate: number, type: RateType): number => {
    if (type === "ea") return rate;
    if (type === "em") return (Math.pow(1 + rate / 100, 12) - 1) * 100;
    if (type === "et") return (Math.pow(1 + rate / 100, 4) - 1) * 100;
    if (type === "na") return (Math.pow(1 + rate / 1200, 12) - 1) * 100;
    return (Math.pow(1 + rate / 100, 12) - 1) * 100;
  };

  const addRate = () => {
    if (rates.length >= 6) return;
    const letter = String.fromCharCode(65 + rates.length);
    setRates((prev) => [...prev, { id: String(Date.now()), value: "", type: "ea", name: `Opción ${letter}` }]);
  };

  const removeRate = (id: string) => {
    if (rates.length <= 2) return;
    setRates((prev) => prev.filter((r) => r.id !== id));
  };

  const updateRate = (id: string, field: "value" | "type" | "name", value: string) => {
    setRates((prev) => prev.map((r) => (r.id === id ? { ...r, [field]: value } : r)));
  };

  const onCompare = () => {
    const valid = rates.filter((r) => !Number.isNaN(parseFloat(r.value)));
    if (valid.length < 2) return;

    const normalized = valid.map((r) => ({
      name: r.name,
      effective: toEffectiveAnnual(parseFloat(r.value), r.type),
      original: parseFloat(r.value),
      type: rateTypes.find((t) => t.value === r.type)?.label ?? "",
    }));

    const bestIndex = normalized.reduce((best, curr, idx, arr) => (curr.effective < arr[best].effective ? idx : best), 0);
    setResult({ rates: normalized, bestIndex });
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

  return (
    <div className="container mx-auto px-4 py-8 md:py-12">
      <div className="mx-auto max-w-6xl">
        <div className="mb-10 text-center">
          <h1 className="mb-4 text-3xl text-gray-900 md:text-5xl">Comparador de tasas</h1>
          <p className="text-lg text-gray-600">Compara multiples tasas para saber cual te conviene mas</p>
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

              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-base font-medium">Tasa</label>
                  <div className="relative">
                    <input
                      type="number"
                      step="0.01"
                      value={rate.value}
                      onChange={(e) => updateRate(rate.id, "value", e.target.value)}
                      className="w-full rounded-xl border border-slate-200 py-5 pr-12 pl-4 text-xl outline-none focus:border-blue-400"
                      placeholder="0.00"
                    />
                    <span className="absolute top-1/2 right-4 -translate-y-1/2 text-xl text-gray-400">%</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-base font-medium">Tipo de tasa</label>
                  <select
                    value={rate.type}
                    onChange={(e) => updateRate(rate.id, "type", e.target.value)}
                    className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base outline-none focus:border-blue-400"
                  >
                    {rateTypes.map((type) => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
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
            size="lg"
            className="rounded-xl bg-blue-600 px-12 py-6 text-lg text-white shadow-lg shadow-blue-200 hover:bg-blue-700"
          >
            <Scale className="h-5 w-5" />
            Comparar
          </Button>
        </div>

        {result && (
          <div className="space-y-8">
            <Card className="rounded-2xl border-0 bg-gradient-to-r from-blue-50 to-green-50 p-8 shadow-xl">
              <div className="mb-6 text-center">
                <CheckCircle className="mx-auto mb-4 h-16 w-16 text-green-600" />
                <h3 className="mb-2 text-2xl text-gray-900 md:text-3xl">
                  {result.rates[result.bestIndex].name} es la más económica
                </h3>
                <p className="text-xl text-gray-600">
                  Con una tasa efectiva anual de {result.rates[result.bestIndex].effective.toFixed(4)}%
                </p>
              </div>

              <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
                {result.rates.map((rate, index) => (
                  <div key={rate.name} className={`rounded-xl bg-white p-4 text-center ${index === result.bestIndex ? "ring-2 ring-green-500" : ""}`}>
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
                  <p className="mb-3">
                    Para comparar tasas de manera justa, primero convertimos todas a <strong>efectiva anual</strong>.
                  </p>
                  {result.rates.map((rate) => (
                    <p key={rate.name} className="mb-2">
                      • {rate.name}: {rate.original}% ({rate.type}) = {rate.effective.toFixed(4)}% efectiva anual
                    </p>
                  ))}
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
                      key={rate.name}
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
