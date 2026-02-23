from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

RateType = Literal["EFFECTIVE", "NOMINAL"]
Period = Literal["MONTHLY", "QUARTERLY", "SEMIANNUAL", "ANNUAL"]


class RateSpec(BaseModel):
    value: float = Field(..., gt=0, le=1000)
    rate_type: RateType
    period: Period
    nominal_capitalization_period: Period | None = None

    @model_validator(mode="after")
    def validate_nominal_requirements(self) -> "RateSpec":
        if self.rate_type == "NOMINAL" and self.nominal_capitalization_period is None:
            raise ValueError("nominal_capitalization_period is required when rate_type is NOMINAL")
        return self


class ConvertRequest(BaseModel):
    from_rate: RateSpec
    to_rate_type: RateType
    to_period: Period
    to_nominal_capitalization_period: Period | None = None

    @model_validator(mode="after")
    def validate_target_nominal_requirements(self) -> "ConvertRequest":
        if self.to_rate_type == "NOMINAL" and self.to_nominal_capitalization_period is None:
            raise ValueError("to_nominal_capitalization_period is required when to_rate_type is NOMINAL")
        return self


class ConvertResponse(BaseModel):
    converted_value: float
    to_rate_type: RateType
    to_period: Period
    effective_annual: float
    details: list[str]


class CompareRequest(BaseModel):
    option_a_name: str = Field(..., min_length=1)
    option_a: RateSpec
    option_b_name: str = Field(..., min_length=1)
    option_b: RateSpec


class CompareResponse(BaseModel):
    winner: Literal["A", "B", "TIE"]
    effective_annual_a: float
    effective_annual_b: float
    difference: float
    summary: str
    details: list[str]


class NewsItem(BaseModel):
    title: str
    summary: str
    source: str
    date: str
    url: str


class NewsResponse(BaseModel):
    items: list[NewsItem]
    stale: bool = False
    generated_at: datetime
