export type RateType = "EFFECTIVE" | "NOMINAL";
export type Period = "MONTHLY" | "QUARTERLY" | "SEMIANNUAL" | "ANNUAL";

export type RateSpec = {
  value: number;
  rate_type: RateType;
  period: Period;
  nominal_capitalization_period?: Period;
};

export type ConvertRequest = {
  from_rate: RateSpec;
  to_rate_type: RateType;
  to_period: Period;
  to_nominal_capitalization_period?: Period;
};

export type ConvertResponse = {
  converted_value: number;
  to_rate_type: RateType;
  to_period: Period;
  effective_annual: number;
  details: string[];
};

export type CompareRequest = {
  option_a_name: string;
  option_a: RateSpec;
  option_b_name: string;
  option_b: RateSpec;
};

export type CompareResponse = {
  winner: "A" | "B" | "TIE";
  effective_annual_a: number;
  effective_annual_b: number;
  difference: number;
  summary: string;
  details: string[];
};

export type NewsItem = {
  title: string;
  summary: string;
  source: string;
  date: string;
  url: string;
};

export type NewsResponse = {
  items: NewsItem[];
  stale: boolean;
};

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8000/api";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return (await res.json()) as T;
}

export function convertRate(req: ConvertRequest): Promise<ConvertResponse> {
  return requestJson<ConvertResponse>("/convert", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export function compareRates(req: CompareRequest): Promise<CompareResponse> {
  return requestJson<CompareResponse>("/compare", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export function getNews(category?: string): Promise<NewsResponse> {
  const query = category ? `?category=${encodeURIComponent(category)}` : "";
  return requestJson<NewsResponse>(`/news${query}`, {
    method: "GET",
  });
}
