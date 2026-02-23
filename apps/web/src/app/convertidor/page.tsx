"use client";

import { useMemo, useState } from "react";
import { Calculator, ChevronDown } from "lucide-react";

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

export default function ConvertidorPage() {
  const [inputRate, setInputRate] = useState("");
  const [fromType, setFromType] = useState<RateType>("ea");
  const [toType, setToType] = useState<RateType>("em");
  const [result, setResult] = useState<number | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const selectedFrom = useMemo(
    () => rateTypes.find((t) => t.value === fromType)?.label.toLowerCase() ?? "",
    [fromType],
  );
  const selectedTo = useMemo(
    () => rateTypes.find((t) => t.value === toType)?.label.toLowerCase() ?? "",
    [toType],
  );

  const onConvert = () => {
    const rate = parseFloat(inputRate);
    if (Number.isNaN(rate)) return;

    let effectiveAnnual = rate;

    if (fromType === "em") effectiveAnnual = (Math.pow(1 + rate / 100, 12) - 1) * 100;
    if (fromType === "et") effectiveAnnual = (Math.pow(1 + rate / 100, 4) - 1) * 100;
    if (fromType === "na") effectiveAnnual = (Math.pow(1 + rate / 1200, 12) - 1) * 100;
    if (fromType === "nm") effectiveAnnual = (Math.pow(1 + rate / 100, 12) - 1) * 100;

    let convertedRate = effectiveAnnual;
    if (toType === "em") convertedRate = (Math.pow(1 + effectiveAnnual / 100, 1 / 12) - 1) * 100;
    if (toType === "et") convertedRate = (Math.pow(1 + effectiveAnnual / 100, 1 / 4) - 1) * 100;
    if (toType === "na") convertedRate = (Math.pow(1 + effectiveAnnual / 100, 1 / 12) - 1) * 1200;
    if (toType === "nm") convertedRate = (Math.pow(1 + effectiveAnnual / 100, 1 / 12) - 1) * 100;

    setResult(convertedRate);
  };

  const explanation =
    result == null
      ? ""
      : toType === "em" || toType === "nm"
        ? `Esto significa que cada mes pagarías o ganarías aproximadamente ${result.toFixed(4)}% sobre el capital.`
        : `Tu tasa ${selectedTo} sería de ${result.toFixed(4)}%.`;

  return (
    <div className="container mx-auto px-4 py-8 md:py-12">
      <div className="mx-auto max-w-2xl">
        <div className="mb-10 text-center">
          <h1 className="mb-4 text-3xl text-gray-900 md:text-5xl">Convertidor de tasas</h1>
          <p className="text-lg text-gray-600">Convierte tasas de interes de un tipo a otro facilmente</p>
        </div>

        <Card className="rounded-2xl border-0 bg-white p-8 shadow-xl md:p-10">
          <div className="space-y-6">
            <div className="space-y-3">
              <label htmlFor="rate" className="text-lg font-medium">Ingresa la tasa</label>
              <div className="relative">
                <input
                  id="rate"
                  type="number"
                  step="0.01"
                  value={inputRate}
                  onChange={(e) => setInputRate(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 py-6 pr-12 pl-4 text-2xl outline-none focus:border-blue-400"
                  placeholder="0.00"
                />
                <span className="absolute top-1/2 right-4 -translate-y-1/2 text-2xl text-gray-400">%</span>
              </div>
            </div>

            <div className="space-y-3">
              <label className="text-lg font-medium">Tipo de tasa actual</label>
              <select
                value={fromType}
                onChange={(e) => setFromType(e.target.value as RateType)}
                className="w-full rounded-xl border border-slate-200 px-4 py-4 text-lg outline-none focus:border-blue-400"
              >
                {rateTypes.map((type) => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>

            <div className="space-y-3">
              <label className="text-lg font-medium">Convertir a</label>
              <select
                value={toType}
                onChange={(e) => setToType(e.target.value as RateType)}
                className="w-full rounded-xl border border-slate-200 px-4 py-4 text-lg outline-none focus:border-blue-400"
              >
                {rateTypes.map((type) => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>

            <Button
              onClick={onConvert}
              size="lg"
              className="w-full rounded-xl bg-blue-600 py-6 text-lg text-white shadow-lg shadow-blue-200 hover:bg-blue-700"
            >
              <Calculator className="h-5 w-5" />
              Convertir
            </Button>
          </div>

          {result != null && (
            <div className="mt-8 rounded-2xl border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-green-50 p-6">
              <div className="mb-4 text-center">
                <p className="mb-2 text-lg text-gray-600">Equivale a:</p>
                <p className="text-4xl text-blue-600">{result.toFixed(4)}%</p>
                <p className="mt-1 text-gray-500">{rateTypes.find((t) => t.value === toType)?.label}</p>
              </div>
              <p className="mb-4 text-center text-gray-600">{explanation}</p>

              <button
                onClick={() => setShowDetails((v) => !v)}
                className="mx-auto flex items-center justify-center gap-2 text-blue-600 hover:text-blue-700"
              >
                <span>Ver detalle del cálculo</span>
                <ChevronDown className={`h-4 w-4 transition-transform ${showDetails ? "rotate-180" : ""}`} />
              </button>

              {showDetails && (
                <div className="mt-4 rounded-xl bg-white p-4 text-sm text-gray-600">
                  <p className="mb-2">
                    <strong>Paso 1:</strong> Se convirtio la tasa {selectedFrom} ({inputRate}%) a efectiva anual.
                  </p>
                  <p>
                    <strong>Paso 2:</strong> Se convirtio la efectiva anual a {selectedTo}, obteniendo {result.toFixed(4)}%.
                  </p>
                </div>
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
