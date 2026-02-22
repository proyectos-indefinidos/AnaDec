from __future__ import annotations

try:
    from api.schemas import Period, RateSpec
    from financeCore.tasa_interes import TasaInteres
except ModuleNotFoundError:
    from src.api.schemas import Period, RateSpec
    from src.financeCore.tasa_interes import TasaInteres


_PERIOD_TO_CORE: dict[str, str] = {
    "MONTHLY": "MV",
    "QUARTERLY": "TV",
    "SEMIANNUAL": "SV",
    "ANNUAL": "EA",
}

_CORE_CODE_TO_MONTHS: dict[str, int] = {
    "MV": 1,
    "TV": 3,
    "SV": 6,
    "EA": 12,
}


def map_period_to_financecore(period: Period) -> str:
    """Mapea Period de la API al codigo usado por financeCore (MV/TV/SV/EA)."""
    code = _PERIOD_TO_CORE.get(period)
    if code is None:
        raise ValueError(f"Periodo no soportado por financeCore: {period}")
    return code


def map_rate_spec_to_tasainteres(rate: RateSpec) -> TasaInteres:
    """Convierte un RateSpec de API a TasaInteres del dominio financeCore.

    La API expone `value` en porcentaje (ej. 24 = 24%), mientras que
    financeCore almacena `valor` en decimal (0.24).
    """
    try:
        value_pct = float(rate.value)
    except (TypeError, ValueError) as ex:
        raise ValueError("RateSpec.value debe ser numérico.") from ex

    if value_pct <= 0:
        raise ValueError("RateSpec.value debe ser mayor que 0.")

    value_decimal = value_pct / 100.0

    if rate.rate_type == "EFFECTIVE":
        core_period_code = map_period_to_financecore(rate.period)
        period_months = _CORE_CODE_TO_MONTHS[core_period_code]
        return TasaInteres(
            valor=value_decimal,
            periodo=period_months,
            tipo="efectiva",
            es_anticipada=False,
        )

    if rate.rate_type == "NOMINAL":
        if rate.nominal_capitalization_period is None:
            raise ValueError(
                "nominal_capitalization_period es obligatorio cuando rate_type es NOMINAL."
            )

        nominal_period_code = map_period_to_financecore(rate.period)
        cap_period_code = map_period_to_financecore(rate.nominal_capitalization_period)

        nominal_period_months = _CORE_CODE_TO_MONTHS[nominal_period_code]
        cap_period_months = _CORE_CODE_TO_MONTHS[cap_period_code]

        if nominal_period_months < cap_period_months:
            raise ValueError(
                "En financeCore, el periodo nominal debe ser mayor o igual al de capitalizacion."
            )

        return TasaInteres(
            valor=value_decimal,
            periodo=cap_period_months,
            tipo="nominal",
            es_anticipada=False,
            periodo_nominal=nominal_period_months,
        )

    raise ValueError(f"Tipo de tasa no soportado por financeCore: {rate.rate_type}")
