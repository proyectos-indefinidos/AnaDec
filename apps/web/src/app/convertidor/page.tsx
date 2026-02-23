"use client";

import { useMemo, useState } from "react";
import { Calculator, ChevronDown } from "lucide-react";

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

type ConvertRequest = {
  from_rate: RateSpec;
  to_rate_type: ApiRateType;
  to_period: ApiPeriod;
  to_nominal_capitalization_period?: ApiPeriod;
};

type ConvertResponse = {
  converted_value: number;
  to_rate_type: ApiRateType;
  to_period: ApiPeriod;
  effective_annual: number;
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

function periodLabel(value: ApiPeriod): string {
  return PERIOD_OPTIONS.find((p) => p.value === value)?.label ?? value;
}

export default function ConvertidorPage() {
  const [inputRate, setInputRate] = useState("");

  const [fromRateType, setFromRateType] = useState<ApiRateType>("EFFECTIVE");
  const [fromPeriod, setFromPeriod] = useState<ApiPeriod>("ANNUAL");
  const [fromNominalCap, setFromNominalCap] = useState<ApiPeriod>("MONTHLY");

  const [toRateType, setToRateType] = useState<ApiRateType>("EFFECTIVE");
  const [toPeriod, setToPeriod] = useState<ApiPeriod>("MONTHLY");
  const [toNominalCap, setToNominalCap] = useState<ApiPeriod>("MONTHLY");

  const [response, setResponse] = useState<ConvertResponse | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toLabel = useMemo(() => {
    const base = `${toRateType === "EFFECTIVE" ? "Efectiva" : "Nominal"} ${periodLabel(toPeriod)}`;
    if (toRateType === "NOMINAL") {
      return `${base} (cap. ${periodLabel(toNominalCap)})`;
    }
    return base;
  }, [toRateType, toPeriod, toNominalCap]);

  const onConvert = async () => {
    const rate = parseFloat(inputRate);
    if (Number.isNaN(rate)) {
      setError("Ingresa una tasa válida.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const req: ConvertRequest = {
        from_rate: {
          value: rate,
          rate_type: fromRateType,
          period: fromPeriod,
          ...(fromRateType === "NOMINAL" ? { nominal_capitalization_period: fromNominalCap } : {}),
        },
        to_rate_type: toRateType,
        to_period: toPeriod,
        ...(toRateType === "NOMINAL" ? { to_nominal_capitalization_period: toNominalCap } : {}),
      };

      const data = await apiPost<ConvertResponse>("/api/convert", req);
      setResponse(data);
    } catch (err) {
      setResponse(null);
      setError(err instanceof Error ? err.message : "No se pudo convertir la tasa.");
    } finally {
      setLoading(false);
    }
  };

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

            <div className="space-y-3 rounded-xl border border-slate-200 p-4">
              <p className="text-lg font-medium">Tasa origen</p>
              <select
                value={fromRateType}
                onChange={(e) => setFromRateType(e.target.value as ApiRateType)}
                className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base outline-none focus:border-blue-400"
              >
                {RATE_TYPE_OPTIONS.map((type) => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>

              <select
                value={fromPeriod}
                onChange={(e) => setFromPeriod(e.target.value as ApiPeriod)}
                className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base outline-none focus:border-blue-400"
              >
                {PERIOD_OPTIONS.map((period) => (
                  <option key={period.value} value={period.value}>{period.label}</option>
                ))}
              </select>

              {fromRateType === "NOMINAL" && (
                <select
                  value={fromNominalCap}
                  onChange={(e) => setFromNominalCap(e.target.value as ApiPeriod)}
                  className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base outline-none focus:border-blue-400"
                >
                  {PERIOD_OPTIONS.map((period) => (
                    <option key={period.value} value={period.value}>Capitalización {period.label}</option>
                  ))}
                </select>
              )}
            </div>

            <div className="space-y-3 rounded-xl border border-slate-200 p-4">
              <p className="text-lg font-medium">Convertir a</p>
              <select
                value={toRateType}
                onChange={(e) => setToRateType(e.target.value as ApiRateType)}
                className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base outline-none focus:border-blue-400"
              >
                {RATE_TYPE_OPTIONS.map((type) => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>

              <select
                value={toPeriod}
                onChange={(e) => setToPeriod(e.target.value as ApiPeriod)}
                className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base outline-none focus:border-blue-400"
              >
                {PERIOD_OPTIONS.map((period) => (
                  <option key={period.value} value={period.value}>{period.label}</option>
                ))}
              </select>

              {toRateType === "NOMINAL" && (
                <select
                  value={toNominalCap}
                  onChange={(e) => setToNominalCap(e.target.value as ApiPeriod)}
                  className="w-full rounded-xl border border-slate-200 px-4 py-3 text-base outline-none focus:border-blue-400"
                >
                  {PERIOD_OPTIONS.map((period) => (
                    <option key={period.value} value={period.value}>Capitalización {period.label}</option>
                  ))}
                </select>
              )}
            </div>

            <Button
              onClick={onConvert}
              disabled={loading}
              size="lg"
              className="w-full rounded-xl bg-blue-600 py-6 text-lg text-white shadow-lg shadow-blue-200 hover:bg-blue-700"
            >
              <Calculator className="h-5 w-5" />
              {loading ? "Convirtiendo..." : "Convertir"}
            </Button>

            {error ? <p className="text-sm text-red-600">{error}</p> : null}
          </div>

          {response && (
            <div className="mt-8 rounded-2xl border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-green-50 p-6">
              <div className="mb-4 text-center">
                <p className="mb-2 text-lg text-gray-600">Equivale a:</p>
                <p className="text-4xl text-blue-600">{response.converted_value.toFixed(4)}%</p>
                <p className="mt-1 text-gray-500">{toLabel}</p>
              </div>
              <p className="mb-4 text-center text-gray-600">EA equivalente: {response.effective_annual.toFixed(4)}%</p>

              <button
                onClick={() => setShowDetails((v) => !v)}
                className="mx-auto flex items-center justify-center gap-2 text-blue-600 hover:text-blue-700"
              >
                <span>Ver detalle del cálculo</span>
                <ChevronDown className={`h-4 w-4 transition-transform ${showDetails ? "rotate-180" : ""}`} />
              </button>

              {showDetails && (
                <div className="mt-4 rounded-xl bg-white p-4 text-sm text-gray-600">
                  {response.details.map((line, idx) => (
                    <p key={`${line}-${idx}`} className={idx < response.details.length - 1 ? "mb-2" : ""}>
                      <strong>Paso {idx + 1}:</strong> {line}
                    </p>
                  ))}
                </div>
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
