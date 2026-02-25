"use client";

import { useMemo, useState } from "react";
import { Calculator, ChevronDown, Loader2 } from "lucide-react";

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

// Función auxiliar para formatear a pesos colombianos
function formatCOP(value: number): string {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
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

  // Estado para el slider interactivo
  const [months, setMonths] = useState<number>(12);

  const toLabel = useMemo(() => {
    const base = `${toRateType === "EFFECTIVE" ? "Efectiva" : "Nominal"} ${periodLabel(toPeriod)}`;
    if (toRateType === "NOMINAL") {
      return `${base} (cap. ${periodLabel(toNominalCap)})`;
    }
    return base;
  }, [toRateType, toPeriod, toNominalCap]);

  // Cálculos matemáticos derivados en el frontend para el tablero interactivo
  const projections = useMemo(() => {
    if (!response) return null;

    // 1. Convertimos la EA a decimal (Ej: 12.5% -> 0.125)
    const eaDecimal = response.effective_annual / 100;

    // 2. Calculamos la Efectiva Mensual usando la fórmula: EM = (1 + EA)^(1/12) - 1
    const emDecimal = Math.pow(1 + eaDecimal, 1 / 12) - 1;

    const baseAmount = 1000000;

    // 3. Regla del millón (Primer mes)
    const firstMonthInterest = baseAmount * emDecimal;

    // 4. Proyección interactiva (Interés compuesto)
    const futureValue = baseAmount * Math.pow(1 + emDecimal, months);
    const totalInterest = futureValue - baseAmount;

    return {
      firstMonthInterest,
      futureValue,
      totalInterest,
    };
  }, [response, months]);

  const onConvert = async () => {
    const rate = parseFloat(inputRate);
    if (Number.isNaN(rate)) {
      setError("Ingresa una tasa válida.");
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null); // Ocultamos el resultado anterior mientras carga
    setMonths(12); // Reiniciamos el slider

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
      setError(err instanceof Error ? err.message : "No se pudo convertir la tasa.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 md:py-12">
      <div className="mx-auto max-w-2xl">
        <div className="mb-10 text-center">
          <h1 className="mb-4 text-3xl font-semibold text-gray-900 md:text-5xl">Convertidor de tasas</h1>
          <p className="text-lg text-gray-600">Convierte tasas de interes de un tipo a otro fácilmente</p>
        </div>

        <Card className="rounded-2xl border-0 bg-white p-8 shadow-xl md:p-10 transition-all duration-300">
          <div className="space-y-6">
            {/* Formulario de Entrada */}
            <div className="space-y-3">
              <label htmlFor="rate" className="text-lg font-medium">Ingresa la tasa</label>
              <div className="relative">
                <input
                  id="rate"
                  type="number"
                  step="0.01"
                  value={inputRate}
                  onChange={(e) => setInputRate(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 py-6 pr-12 pl-4 text-2xl outline-none transition-colors focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  placeholder="0.00"
                />
                <span className="absolute top-1/2 right-4 -translate-y-1/2 text-2xl text-gray-400">%</span>
              </div>
            </div>

            <div className="space-y-3 rounded-xl border border-slate-100 bg-slate-50/50 p-5">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Tasa de Origen</p>
              <div className="grid gap-3 sm:grid-cols-2">
                <select
                  value={fromRateType}
                  onChange={(e) => setFromRateType(e.target.value as ApiRateType)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-base outline-none focus:border-blue-500"
                >
                  {RATE_TYPE_OPTIONS.map((type) => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>

                <select
                  value={fromPeriod}
                  onChange={(e) => setFromPeriod(e.target.value as ApiPeriod)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-base outline-none focus:border-blue-500"
                >
                  {PERIOD_OPTIONS.map((period) => (
                    <option key={period.value} value={period.value}>{period.label}</option>
                  ))}
                </select>
              </div>

              {fromRateType === "NOMINAL" && (
                <select
                  value={fromNominalCap}
                  onChange={(e) => setFromNominalCap(e.target.value as ApiPeriod)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-base outline-none focus:border-blue-500 mt-3"
                >
                  {PERIOD_OPTIONS.map((period) => (
                    <option key={period.value} value={period.value}>Capitalización {period.label}</option>
                  ))}
                </select>
              )}
            </div>

            <div className="space-y-3 rounded-xl border border-slate-100 bg-slate-50/50 p-5">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Convertir a</p>
              <div className="grid gap-3 sm:grid-cols-2">
                <select
                  value={toRateType}
                  onChange={(e) => setToRateType(e.target.value as ApiRateType)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-base outline-none focus:border-blue-500"
                >
                  {RATE_TYPE_OPTIONS.map((type) => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>

                <select
                  value={toPeriod}
                  onChange={(e) => setToPeriod(e.target.value as ApiPeriod)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-base outline-none focus:border-blue-500"
                >
                  {PERIOD_OPTIONS.map((period) => (
                    <option key={period.value} value={period.value}>{period.label}</option>
                  ))}
                </select>
              </div>

              {toRateType === "NOMINAL" && (
                <select
                  value={toNominalCap}
                  onChange={(e) => setToNominalCap(e.target.value as ApiPeriod)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-base outline-none focus:border-blue-500 mt-3"
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
              className="w-full rounded-xl bg-blue-600 py-6 text-lg font-medium text-white shadow-lg shadow-blue-200 hover:bg-blue-700 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-6 w-6 animate-spin" />
                  Calculando...
                </>
              ) : (
                <>
                  <Calculator className="mr-2 h-5 w-5" />
                  Convertir
                </>
              )}
            </Button>

            {error ? <p className="text-sm text-red-600 text-center bg-red-50 p-3 rounded-lg">{error}</p> : null}
          </div>

          {/* Pantalla de Carga (Loading Screen) */}
          {loading && (
            <div className="mt-8 flex flex-col items-center justify-center rounded-2xl border-2 border-slate-100 bg-slate-50 py-16 animate-pulse">
              <Loader2 className="h-10 w-10 animate-spin text-blue-500 mb-4" />
              <p className="text-lg font-medium text-slate-500">Procesando matemáticas...</p>
            </div>
          )}

          {/* Tablero de Resultados Interactivos */}
          {response && projections && !loading && (
            <div className="mt-8 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              
              {/* Resultado Principal */}
              <div className="rounded-2xl border-2 border-blue-100 bg-gradient-to-br from-blue-50 to-white p-6 md:p-8 text-center shadow-sm">
                <p className="mb-2 text-lg font-medium text-gray-500">Tu tasa equivale a:</p>
                <h2 className="text-5xl font-bold text-blue-600 mb-2">{response.converted_value.toFixed(4)}%</h2>
                <p className="text-xl font-medium text-gray-700 mb-4">{toLabel}</p>
                <div className="inline-block bg-white px-4 py-2 rounded-lg border border-blue-100 text-sm text-gray-600 shadow-sm">
                  EA Equivalente: <span className="font-bold text-gray-900">{response.effective_annual.toFixed(4)}%</span>
                </div>
              </div>

              {/* Explicación Visual  */}
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-green-100 text-green-600">
                    $
                  </span>
                  Si tu deuda o inversión fuera de <strong>$1.000.000 COP</strong>...
                </h3>
                <p className="text-gray-600 leading-relaxed text-lg">
                  Si aplicamos esta tasa a un capital de <strong>$1.000.000 COP</strong>, 
                  durante el primer mes representará un interés aproximado de{" "}
                  <strong className="text-green-600 text-xl bg-green-50 px-2 py-1 rounded">
                    {formatCOP(projections.firstMonthInterest)}
                  </strong>.
                </p>
              </div>

              {/* Tablero Interactivo (Slider de Interés Compuesto) */}
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Proyección en el tiempo</h3>
                <p className="text-sm text-gray-500 mb-6">
                  Descubre el efecto del interés compuesto. Mueve la barra para ver cómo crece el dinero.
                </p>
                
                <div className="mb-8">
                  <input
                    type="range"
                    min="1"
                    max="36"
                    value={months}
                    onChange={(e) => setMonths(Number(e.target.value))}
                    className="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  />
                  <div className="flex justify-between text-xs font-medium text-gray-400 mt-3">
                    <span>1 mes</span>
                    <span>1 año</span>
                    <span>2 años</span>
                    <span>3 años</span>
                  </div>
                </div>

                <div className="text-center bg-slate-50 rounded-xl p-6 border border-slate-100">
                  <p className="text-sm font-medium text-gray-500 uppercase tracking-widest mb-2">
                    Mes {months}
                  </p>
                  <p className="text-4xl font-bold text-gray-900 mb-2">
                    {formatCOP(projections.futureValue)}
                  </p>
                  <p className="text-sm font-medium text-blue-600">
                    +{formatCOP(projections.totalInterest)} generados en interés
                  </p>
                </div>
              </div>

              {/* Explicación Matemática (Para los curiosos) */}
              <button
                onClick={() => setShowDetails((v) => !v)}
                className="mx-auto flex w-full items-center justify-between rounded-xl border border-slate-200 bg-white p-4 text-left font-medium text-gray-700 hover:bg-slate-50 transition-colors"
              >
                <span>¿Cómo calculamos esto? (Proceso matemático)</span>
                <ChevronDown className={`h-5 w-5 text-gray-400 transition-transform duration-300 ${showDetails ? "rotate-180" : ""}`} />
              </button>

              {showDetails && (
                <div className="rounded-xl border border-blue-100 bg-blue-50/50 p-5 text-sm text-gray-700 shadow-inner">
                  <p className="mb-4">
                    Las finanzas usan fórmulas exponenciales, no lineales. Para asegurar precisión milimétrica, tu tasa pasó por este flujo en nuestros servidores:
                  </p>
                  <ul className="space-y-3">
                    {response.details.map((line, idx) => (
                      <li key={`${line}-${idx}`} className="flex gap-3">
                        <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-blue-200 text-xs font-bold text-blue-700">
                          {idx + 1}
                        </span>
                        <span>{line}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}