from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException

try:
    from api.adapters import map_period_to_financecore, map_rate_spec_to_tasainteres
    from api.schemas import (
        CompareRequest,
        CompareResponse,
        ConvertRequest,
        ConvertResponse,
        NewsItem,
        NewsResponse,
    )
    from dataAccess.newsRepo import NewsRepo
    from financeCore.comparador import Comparador
    from financeCore.convertidor import Convertidor
    from financeCore.tasa_interes import TasaInteres
except ModuleNotFoundError:
    from src.api.adapters import map_period_to_financecore, map_rate_spec_to_tasainteres
    from src.api.schemas import (
        CompareRequest,
        CompareResponse,
        ConvertRequest,
        ConvertResponse,
        NewsItem,
        NewsResponse,
    )
    from src.dataAccess.newsRepo import NewsRepo
    from src.financeCore.comparador import Comparador
    from src.financeCore.convertidor import Convertidor
    from src.financeCore.tasa_interes import TasaInteres

router = APIRouter()

_PERIOD_MONTHS: dict[str, int] = {
    "MV": 1,
    "TV": 3,
    "SV": 6,
    "EA": 12,
}

_NEWS_CACHE_TTL = timedelta(minutes=15)
_news_cache: dict[str, dict[str, object]] = {}


def _period_to_months(api_period: str) -> int:
    core_code = map_period_to_financecore(api_period)
    months = _PERIOD_MONTHS.get(core_code)
    if months is None:
        raise ValueError(f"No existe mapeo de meses para el periodo destino: {api_period}")
    return months


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

        # 1) Adaptar request al modelo de dominio del core.
        tasa_origen = map_rate_spec_to_tasainteres(payload.from_rate)

        # 2) Estandarizar a EA como paso intermedio comun para evitar formulas en API.
        ea_decimal = convertidor.tasa_a_ea_std(tasa_origen)
        tasa_ea = TasaInteres(valor=ea_decimal, periodo=12, tipo="efectiva", es_anticipada=False)

        details = [
            "Se recibio y valido la tasa de origen.",
            "Se estandarizo la tasa de origen a efectiva anual (EA).",
        ]

        # 3) Convertir desde EA al destino solicitado.
        if payload.to_rate_type == "EFFECTIVE":
            to_months = _period_to_months(payload.to_period)
            tasa_destino = convertidor.cambiar_temporalidad_en_efectivo(tasa_ea, to_months)
            details.append("Se convirtio EA a tasa efectiva en el periodo solicitado.")

        elif payload.to_rate_type == "NOMINAL":
            if payload.to_nominal_capitalization_period is None:
                raise ValueError(
                    "to_nominal_capitalization_period es obligatorio cuando to_rate_type es NOMINAL."
                )

            periodo_nominal_meses = _period_to_months(payload.to_period)
            periodo_cap_meses = _period_to_months(payload.to_nominal_capitalization_period)

            # EA -> efectiva periodica de capitalizacion -> nominal.
            tasa_periodica_cap = convertidor.cambiar_temporalidad_en_efectivo(tasa_ea, periodo_cap_meses)
            tasa_destino = convertidor.efectiva_periodica_a_nominal(
                tasa=tasa_periodica_cap,
                periodo_nominal=periodo_nominal_meses,
                periodo_capitalizacion=periodo_cap_meses,
                es_anticipada=False,
            )
            details.append("Se convirtio EA a efectiva periodica segun la capitalizacion destino.")
            details.append("Se transformo la efectiva periodica a nominal con los periodos solicitados.")

        else:
            raise ValueError(f"Tipo de tasa destino no soportado: {payload.to_rate_type}")

        ea_destino = convertidor.tasa_a_ea_std(tasa_destino)
        details.append("Se calculo la EA equivalente de la tasa convertida para referencia.")

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
        raise HTTPException(
            status_code=500,
            detail="Ocurrio un error interno al convertir la tasa.",
        ) from ex


@router.post("/compare", response_model=CompareResponse)
def compare_rates(payload: CompareRequest) -> CompareResponse:
    try:
        # 1) Adaptar request al dominio del core.
        tasa_a = map_rate_spec_to_tasainteres(payload.option_a)
        tasa_b = map_rate_spec_to_tasainteres(payload.option_b)

        comparador = Comparador()

        # 2) Usar el comparador del core para obtener EA y ranking.
        df = comparador.comparar_escenarios(
            [
                {"nombre": "__A__", "tasa": tasa_a},
                {"nombre": "__B__", "tasa": tasa_b},
            ]
        )

        row_a = df[df["Nombre"] == "__A__"]
        row_b = df[df["Nombre"] == "__B__"]
        if row_a.empty or row_b.empty:
            raise ValueError("No se pudieron extraer las opciones comparadas del resultado.")

        ea_a = float(row_a.iloc[0]["EA"])
        ea_b = float(row_b.iloc[0]["EA"])

        diff = abs(ea_a - ea_b)
        tol = 1e-12
        if diff <= tol:
            winner = "TIE"
            summary = (
                f"Las opciones {payload.option_a_name} y {payload.option_b_name} "
                "son equivalentes en EA."
            )
        elif ea_a < ea_b:
            winner = "A"
            summary = (
                f"La opcion {payload.option_a_name} es mas conveniente por menor EA "
                "(criterio de costo financiero)."
            )
        else:
            winner = "B"
            summary = (
                f"La opcion {payload.option_b_name} es mas conveniente por menor EA "
                "(criterio de costo financiero)."
            )

        details = [
            "Se validaron los datos de ambas tasas recibidas.",
            "Se adaptaron ambas tasas al modelo de dominio del core.",
            "Se estandarizaron y compararon las dos opciones usando EA.",
            f"EA opcion A ({payload.option_a_name}): {ea_a * 100:.6f}%.",
            f"EA opcion B ({payload.option_b_name}): {ea_b * 100:.6f}%.",
            f"Diferencia absoluta de EA: {diff * 100:.6f} puntos porcentuales.",
        ]

        return CompareResponse(
            winner=winner,
            effective_annual_a=round(ea_a * 100.0, 6),
            effective_annual_b=round(ea_b * 100.0, 6),
            difference=round(diff * 100.0, 6),
            summary=summary,
            details=details,
        )

    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex
    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail="Ocurrio un error interno al comparar tasas.",
        ) from ex


@router.get("/news", response_model=NewsResponse)
def get_news(category: str | None = None) -> NewsResponse:
    cache_key = (category or "").strip().lower() or "__default__"
    now = datetime.now(timezone.utc)
    cached = _news_cache.get(cache_key)

    if cached:
        fetched_at = cached.get("fetched_at")
        if isinstance(fetched_at, datetime) and now - fetched_at <= _NEWS_CACHE_TTL:
            return NewsResponse(
                items=cached.get("items", []),  # type: ignore[arg-type]
                stale=False,
            )

    try:
        repo = NewsRepo()
        df = repo.get_noticias(filtro=category.strip() if category else None)
        if df is None:
            raise ValueError("No se recibieron datos de noticias.")

        items = _df_to_news_items(df)
        if len(items) == 0 and cached:
            return NewsResponse(
                items=cached.get("items", []),  # type: ignore[arg-type]
                stale=True,
            )

        _news_cache[cache_key] = {"items": items, "fetched_at": now}
        return NewsResponse(items=items, stale=False)
    except ValueError as ex:
        if cached:
            return NewsResponse(
                items=cached.get("items", []),  # type: ignore[arg-type]
                stale=True,
            )
        raise HTTPException(status_code=400, detail=str(ex)) from ex
    except Exception as ex:
        if cached:
            return NewsResponse(
                items=cached.get("items", []),  # type: ignore[arg-type]
                stale=True,
            )
        raise HTTPException(
            status_code=500,
            detail="Ocurrio un error interno al obtener noticias.",
        ) from ex
