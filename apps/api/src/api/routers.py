from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException

from .adapters import map_period_to_months, map_rate_spec_to_tasainteres
from .schemas import (
    CompareRequest,
    CompareResponse,
    ConvertRequest,
    ConvertResponse,
    NewsItem,
    NewsResponse,
)

# Permite reutilizar el dominio existente en /src/financeCore desde apps/api.
_ROOT_SRC = Path(__file__).resolve().parents[4] / "src"
if str(_ROOT_SRC) not in sys.path:
    sys.path.append(str(_ROOT_SRC))

from dataAccess.newsRepo import NewsRepo
from financeCore.comparador import Comparador
from financeCore.convertidor import Convertidor
from financeCore.tasa_interes import TasaInteres

router = APIRouter()

_NEWS_CACHE_TTL = timedelta(minutes=15)
_news_cache: dict[str, dict[str, object]] = {}


def _df_to_news_items(df) -> list[NewsItem]:
    items: list[NewsItem] = []
    for _, row in df.iterrows():
        title = str(row.get("Título", row.get("Title", "")) or "").strip()
        summary = str(row.get("Descripción", row.get("Description", "")) or "").strip()
        source = str(row.get("Fuente", row.get("Source", "")) or "").strip()
        date = str(row.get("Fecha", row.get("Date", "")) or "").strip()
        url = str(
            row.get("URL", row.get("Url", row.get("url", row.get("Link", row.get("link", "")))))
            or ""
        ).strip()

        items.append(
            NewsItem(
                title=title,
                summary=summary,
                source=source,
                date=date,
                url=url,
            )
        )
    return items


@router.post("/convert", response_model=ConvertResponse)
def convert_rate(payload: ConvertRequest) -> ConvertResponse:
    try:
        convertidor = Convertidor()
        tasa_origen = map_rate_spec_to_tasainteres(payload.from_rate)
        ea_origen = convertidor.tasa_a_ea_std(tasa_origen)
        tasa_ea = TasaInteres(valor=ea_origen, periodo=12, tipo="efectiva", es_anticipada=False)

        details = [
            "Se validó la tasa de origen.",
            "Se estandarizó la tasa a efectiva anual (EA).",
        ]

        if payload.to_rate_type == "EFFECTIVE":
            target_months = map_period_to_months(payload.to_period)
            tasa_destino = convertidor.cambiar_temporalidad_en_efectivo(tasa_ea, target_months)
            details.append("Se convirtió la EA a tasa efectiva del período solicitado.")
        else:
            if payload.to_nominal_capitalization_period is None:
                raise ValueError(
                    "to_nominal_capitalization_period is required when to_rate_type is NOMINAL"
                )

            nominal_months = map_period_to_months(payload.to_period)
            cap_months = map_period_to_months(payload.to_nominal_capitalization_period)

            periodic_effective = convertidor.cambiar_temporalidad_en_efectivo(tasa_ea, cap_months)
            tasa_destino = convertidor.efectiva_periodica_a_nominal(
                tasa=periodic_effective,
                periodo_nominal=nominal_months,
                periodo_capitalizacion=cap_months,
                es_anticipada=False,
            )
            details.append("Se convirtió la EA a efectiva periódica de capitalización.")
            details.append("Se transformó la efectiva periódica a nominal según los períodos solicitados.")

        ea_destino = convertidor.tasa_a_ea_std(tasa_destino)

        return ConvertResponse(
            converted_value=round(tasa_destino.valor * 100.0, 6),
            to_rate_type=payload.to_rate_type,
            to_period=payload.to_period,
            effective_annual=round(ea_destino * 100.0, 6),
            details=details,
        )
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail="Internal server error.") from ex


@router.post("/compare", response_model=CompareResponse)
def compare_rates(payload: CompareRequest) -> CompareResponse:
    try:
        tasa_a = map_rate_spec_to_tasainteres(payload.option_a)
        tasa_b = map_rate_spec_to_tasainteres(payload.option_b)
        comparador = Comparador()

        df = comparador.comparar_escenarios(
            [
                {"nombre": "__A__", "tasa": tasa_a},
                {"nombre": "__B__", "tasa": tasa_b},
            ]
        )

        row_a = df[df["Nombre"] == "__A__"]
        row_b = df[df["Nombre"] == "__B__"]
        if row_a.empty or row_b.empty:
            raise ValueError("Could not extract compared options from ranking result")

        ea_a = float(row_a.iloc[0]["EA"]) * 100.0
        ea_b = float(row_b.iloc[0]["EA"]) * 100.0
        difference = round(abs(ea_a - ea_b), 6)

        if difference <= 1e-12:
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
            "Se estandarizaron ambas opciones a EA con el motor financiero.",
            "Se compararon los resultados y se determinó la opción ganadora.",
        ]

        return CompareResponse(
            winner=winner,
            effective_annual_a=round(ea_a, 6),
            effective_annual_b=round(ea_b, 6),
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
        cached_at = cached.get("fetched_at")
        if isinstance(cached_at, datetime) and now - cached_at <= _NEWS_CACHE_TTL:
            return NewsResponse(
                items=cached.get("items", []),  # type: ignore[arg-type]
                stale=False,
                generated_at=cached_at,
            )

    try:
        repo = NewsRepo()
        df = repo.get_noticias(filtro=category.strip() if category else None)
        if df is None:
            raise ValueError("No se recibieron datos de noticias.")

        items = _df_to_news_items(df)
        if len(items) == 0 and cached is not None:
            stale_at = cached.get("fetched_at")
            if isinstance(stale_at, datetime):
                return NewsResponse(
                    items=cached.get("items", []),  # type: ignore[arg-type]
                    stale=True,
                    generated_at=stale_at,
                )

        _news_cache[cache_key] = {"items": items, "fetched_at": now}
        return NewsResponse(items=items, stale=False, generated_at=now)
    except ValueError as ex:
        if cached is not None:
            stale_at = cached.get("fetched_at")
            if isinstance(stale_at, datetime):
                return NewsResponse(
                    items=cached.get("items", []),  # type: ignore[arg-type]
                    stale=True,
                    generated_at=stale_at,
                )
        raise HTTPException(status_code=400, detail=str(ex)) from ex
    except Exception as ex:
        if cached is not None:
            stale_at = cached.get("fetched_at")
            if isinstance(stale_at, datetime):
                return NewsResponse(
                    items=cached.get("items", []),  # type: ignore[arg-type]
                    stale=True,
                    generated_at=stale_at,
                )
        raise HTTPException(status_code=500, detail="Internal server error.") from ex
