from __future__ import annotations

import sys
from pathlib import Path

from .schemas import Period, RateSpec

_PERIOD_TO_CORE = {
    "MONTHLY": "MV",
    "QUARTERLY": "TV",
    "SEMIANNUAL": "SV",
    "ANNUAL": "EA",
}

_PERIOD_TO_MONTHS = {
    "MONTHLY": 1,
    "QUARTERLY": 3,
    "SEMIANNUAL": 6,
    "ANNUAL": 12,
}

# Permite reutilizar el dominio existente en /src/financeCore desde apps/api.
_ROOT_SRC = Path(__file__).resolve().parents[4] / "src"
if str(_ROOT_SRC) not in sys.path:
    sys.path.append(str(_ROOT_SRC))

from financeCore.tasa_interes import TasaInteres


def map_period_to_financecore(period: Period) -> str:
    code = _PERIOD_TO_CORE.get(period)
    if code is None:
        raise ValueError(f"Unsupported period: {period}")
    return code


def map_period_to_months(period: Period) -> int:
    months = _PERIOD_TO_MONTHS.get(period)
    if months is None:
        raise ValueError(f"Unsupported period: {period}")
    return months


def map_rate_spec_to_tasainteres(rate: RateSpec) -> TasaInteres:
    value_decimal = float(rate.value) / 100.0

    if rate.rate_type == "EFFECTIVE":
        return TasaInteres(
            valor=value_decimal,
            periodo=map_period_to_months(rate.period),
            tipo="efectiva",
            es_anticipada=False,
        )

    if rate.nominal_capitalization_period is None:
        raise ValueError("nominal_capitalization_period is required when rate_type is NOMINAL")

    nominal_period = map_period_to_months(rate.period)
    cap_period = map_period_to_months(rate.nominal_capitalization_period)
    if nominal_period < cap_period:
        raise ValueError("For NOMINAL rates, period must be >= nominal_capitalization_period")

    return TasaInteres(
        valor=value_decimal,
        periodo=cap_period,
        tipo="nominal",
        es_anticipada=False,
        periodo_nominal=nominal_period,
    )
