from __future__ import annotations

from .schemas import Period, RateSpec

_PERIOD_TO_CORE = {
    "MONTHLY": "MV",
    "QUARTERLY": "TV",
    "SEMIANNUAL": "SV",
    "ANNUAL": "EA",
}


def map_period_to_financecore(period: Period) -> str:
    code = _PERIOD_TO_CORE.get(period)
    if code is None:
        raise ValueError(f"Unsupported period: {period}")
    return code


def map_rate_spec_to_payload(rate: RateSpec) -> dict[str, object]:
    payload = {
        "value_percent": float(rate.value),
        "rate_type": rate.rate_type,
        "period": map_period_to_financecore(rate.period),
        "nominal_capitalization_period": (
            map_period_to_financecore(rate.nominal_capitalization_period)
            if rate.nominal_capitalization_period
            else None
        ),
    }
    return payload
