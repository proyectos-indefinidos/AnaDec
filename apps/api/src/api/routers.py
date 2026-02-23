from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException

from .adapters import map_rate_spec_to_payload
from .schemas import (
    CompareRequest,
    CompareResponse,
    ConvertRequest,
    ConvertResponse,
    NewsItem,
    NewsResponse,
)

router = APIRouter()

_NEWS_CACHE_TTL = timedelta(minutes=15)
_news_cache: dict[str, dict[str, object]] = {}


def _dummy_news(category: str | None) -> list[NewsItem]:
    tag = (category or "general").strip() or "general"
    return [
        NewsItem(
            title="Tasas del mercado hoy",
            summary=f"Resumen rapido de movimientos recientes en categoria {tag}.",
            source="AnaDec Demo",
            date="2026-02-22",
            url="https://example.com/news/market-rates",
        ),
        NewsItem(
            title="Inflacion y decisiones financieras",
            summary="Puntos clave para entender el impacto en creditos e inversiones.",
            source="AnaDec Demo",
            date="2026-02-22",
            url="https://example.com/news/inflation-impact",
        ),
        NewsItem(
            title="Como comparar dos opciones de tasa",
            summary="Guia corta para evaluar costos y rentabilidad.",
            source="AnaDec Demo",
            date="2026-02-22",
            url="https://example.com/news/compare-rates",
        ),
    ]


@router.post("/convert", response_model=ConvertResponse)
def convert_rate(payload: ConvertRequest) -> ConvertResponse:
    try:
        source = map_rate_spec_to_payload(payload.from_rate)

        # Stub temporal hasta integrar financeCore en apps/api.
        converted_value = round(float(source["value_percent"]) * 1.02, 6)
        effective_annual = round(converted_value * 1.01, 6)

        details = [
            "Se valido la tasa de origen.",
            "Se normalizo el periodo de entrada.",
            "Se genero una conversion temporal de ejemplo.",
        ]

        return ConvertResponse(
            converted_value=converted_value,
            to_rate_type=payload.to_rate_type,
            to_period=payload.to_period,
            effective_annual=effective_annual,
            details=details,
        )
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail="Internal server error.") from ex


@router.post("/compare", response_model=CompareResponse)
def compare_rates(payload: CompareRequest) -> CompareResponse:
    try:
        a = map_rate_spec_to_payload(payload.option_a)
        b = map_rate_spec_to_payload(payload.option_b)

        # Stub temporal hasta integrar financeCore en apps/api.
        ea_a = round(float(a["value_percent"]) * 1.01, 6)
        ea_b = round(float(b["value_percent"]) * 1.01, 6)
        difference = round(abs(ea_a - ea_b), 6)

        if difference == 0:
            winner = "TIE"
            summary = f"{payload.option_a_name} y {payload.option_b_name} son equivalentes."
        elif ea_a < ea_b:
            winner = "A"
            summary = f"La opcion {payload.option_a_name} es mas conveniente."
        else:
            winner = "B"
            summary = f"La opcion {payload.option_b_name} es mas conveniente."

        details = [
            "Se validaron ambas tasas recibidas.",
            "Se estandarizaron ambas opciones a un formato comparable.",
            "Se calculo la diferencia y se determino una opcion ganadora.",
        ]

        return CompareResponse(
            winner=winner,
            effective_annual_a=ea_a,
            effective_annual_b=ea_b,
            difference=difference,
            summary=summary,
            details=details,
        )
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail="Internal server error.") from ex


@router.get("/news", response_model=NewsResponse)
def get_news(category: str | None = None) -> NewsResponse:
    cache_key = (category or "").strip().lower() or "__default__"
    now = datetime.now(timezone.utc)
    cached = _news_cache.get(cache_key)

    if cached is not None:
        cached_at = cached.get("generated_at")
        if isinstance(cached_at, datetime) and now - cached_at <= _NEWS_CACHE_TTL:
            return NewsResponse(
                items=cached.get("items", []),  # type: ignore[arg-type]
                stale=False,
                generated_at=cached_at,
            )

    try:
        items = _dummy_news(category)
        response = NewsResponse(items=items, stale=False, generated_at=now)
        _news_cache[cache_key] = {"items": items, "generated_at": now}
        return response
    except ValueError as ex:
        if cached is not None:
            stale_at = cached.get("generated_at")
            if isinstance(stale_at, datetime):
                return NewsResponse(
                    items=cached.get("items", []),  # type: ignore[arg-type]
                    stale=True,
                    generated_at=stale_at,
                )
        raise HTTPException(status_code=400, detail=str(ex)) from ex
    except Exception as ex:
        if cached is not None:
            stale_at = cached.get("generated_at")
            if isinstance(stale_at, datetime):
                return NewsResponse(
                    items=cached.get("items", []),  # type: ignore[arg-type]
                    stale=True,
                    generated_at=stale_at,
                )
        raise HTTPException(status_code=500, detail="Internal server error.") from ex
