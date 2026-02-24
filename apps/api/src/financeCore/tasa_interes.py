#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
tasa_interes.py

Modelo de dominio para representar tasas de interés de forma uniforme.

Soporta parsing desde texto para:
- Nominal:  "24% NA/MV"
- Efectiva: "6% TV", "10% EA"

Convenciones:
- El atributo `valor` se almacena en formato decimal (p. ej. 24% -> 0.24).
- Los periodos se representan en "meses por periodo": 1, 3, 6, 12.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar, Dict


@dataclass(frozen=True)
class TasaInteres:
    """Representa una tasa de interés nominal o efectiva.

    Attributes:
        valor: Valor en decimal. Ej: 24% -> 0.24.
        periodo: Meses por periodo.
            - Si tipo="efectiva": MV=1, TV=3, SV=6, EA=12.
            - Si tipo="nominal": periodo de capitalización (MV=1, TV=3, SV=6, AV/EA=12).
        tipo: "efectiva" o "nominal".
        es_anticipada: True si la tasa es anticipada (A), False si es vencida (V).
        periodo_nominal: Meses del periodo nominal de referencia (solo nominal):
            NM=1, NT=3, NS=6, NA=12.
    """

    valor: float
    periodo: int
    tipo: str
    es_anticipada: bool = False
    periodo_nominal: int | None = None

    PERIODOS: ClassVar[Dict[str, int]] = {"M": 1, "T": 3, "S": 6, "A": 12}
    EFECTIVAS: ClassVar[Dict[str, int]] = {"MV": 1, "TV": 3, "SV": 6, "EA": 12, "AV": 12}

    _RE_NOMINAL: ClassVar[re.Pattern] = re.compile(
        r"^([0-9]+(?:[.,][0-9]+)?)%?N([MTSA])\/([MTSA])([VA])$"
    )
    _RE_EFECTIVA: ClassVar[re.Pattern] = re.compile(
        r"^([0-9]+(?:[.,][0-9]+)?)%?(MV|TV|SV|EA|AV)$"
    )

    def __post_init__(self) -> None:
        """Valida invariantes del objeto."""
        tipo_norm = (self.tipo or "").strip().lower()
        object.__setattr__(self, "tipo", tipo_norm)

        if self.valor <= -1:
            raise ValueError("La tasa no puede ser <= -100% (valor <= -1).")
        if self.periodo <= 0:
            raise ValueError("El periodo debe ser positivo (1, 3, 6, 12).")
        if self.tipo not in {"efectiva", "nominal"}:
            raise ValueError("tipo debe ser 'efectiva' o 'nominal'.")

        if self.tipo == "nominal":
            if self.periodo_nominal is None:
                raise ValueError("Una tasa nominal requiere periodo_nominal (1, 3, 6, 12).")
            if self.periodo_nominal <= 0:
                raise ValueError("periodo_nominal debe ser positivo.")
            if self.periodo_nominal < self.periodo:
                raise ValueError(
                    "periodo_nominal no puede ser menor que el periodo de capitalización."
                )

    @staticmethod
    def _percent_to_decimal(pct_str: str) -> float:
        """Convierte string de porcentaje a decimal.

        Args:
            pct_str: Porcentaje como string, ej. "24", "24.5", "24,5".

        Returns:
            Decimal equivalente. Ej: "24" -> 0.24.
        """
        return float(pct_str.replace(",", ".")) / 100.0

    @classmethod
    def from_string(cls, text: str) -> "TasaInteres":
        """Crea una tasa a partir de un string nominal o efectivo.

        Soporta:
            - Nominal:  "24% NA/MV", "18.5% NS/SV"
            - Efectiva: "6% TV", "10% EA", "6TV", "10EA"

        Args:
            text: String con la tasa.

        Returns:
            Instancia de TasaInteres.

        Raises:
            ValueError: Si el formato no es reconocido.
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Entrada inválida. Ej: '24% NA/MV' o '6% TV' o '10% EA'.")

        raw = text.strip().upper().replace(" ", "")

        m_nom = cls._RE_NOMINAL.fullmatch(raw)
        if m_nom:
            pct_str, p_nom, p_cap, va = m_nom.groups()
            valor = cls._percent_to_decimal(pct_str)
            periodo_nominal = cls.PERIODOS[p_nom]
            periodo_cap = cls.PERIODOS[p_cap]
            es_anticipada = (va == "A")

            return cls(
                valor=valor,
                periodo=periodo_cap,
                tipo="nominal",
                es_anticipada=es_anticipada,
                periodo_nominal=periodo_nominal,
            )

        m_eff = cls._RE_EFECTIVA.fullmatch(raw)
        if m_eff:
            pct_str, code = m_eff.groups()
            valor = cls._percent_to_decimal(pct_str)
            periodo = cls.EFECTIVAS[code]

            return cls(valor=valor, periodo=periodo, tipo="efectiva", es_anticipada=False)

        raise ValueError(
            "Formato no reconocido. Use: '24% NA/MV' (nominal) o '6% TV' / '10% EA' (efectiva)."
        )

    def to_string(self, precision: int = 6) -> str:
        """Serializa la tasa a un formato legible.

        Args:
            precision: Número de decimales a mostrar en el porcentaje.

        Returns:
            String en formato nominal o efectiva.
        """
        pct = round(self.valor * 100.0, precision)
        pct_str = f"{pct}".rstrip("0").rstrip(".")

        if self.tipo == "efectiva":
            inv_eff = {1: "MV", 3: "TV", 6: "SV", 12: "EA"}
            code = inv_eff.get(self.periodo, str(self.periodo))
            return f"{pct_str}% {code}"

        inv_p = {v: k for k, v in self.PERIODOS.items()}
        suf = "A" if self.es_anticipada else "V"
        return f"{pct_str}% N{inv_p[self.periodo_nominal]}/{inv_p[self.periodo]}{suf}"