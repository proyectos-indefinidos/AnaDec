#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Dict, List, Optional, Union

import pandas as pd

from .convertidor import Convertidor
from .tasa_interes import TasaInteres

Number = Union[int, float]


class Estandarizador:
    
    """Utilidades para estandarizar tasas y preparar datos para gráficas."""

    def __init__(self, precision: int = 6, money_round: int = 2) -> None:
        if precision < 0:
            raise ValueError("precision no puede ser negativa.")
        if money_round < 0:
            raise ValueError("money_round no puede ser negativa.")

        self.convertidor = Convertidor(precision=precision)
        self.precision = precision
        self.money_round = money_round

    
    def tasa_periodica_vencida(self, tasa: TasaInteres) -> float:
        """
        Devuelve tasa periódica efectiva vencida (float) desde TasaInteres.

        Reglas:
        - efectiva: i = valor
        - nominal:  i = valor / m, donde m = periodo_nominal / periodo

        Si es anticipada:
            i = d / (1 - d)

        Raises:
            ValueError: Si la tasa es inválida.
        """
        if not isinstance(tasa, TasaInteres):
            raise TypeError("tasa debe ser una efectiva o nominal.")

        if tasa.valor <= -1:
            raise ValueError("La tasa no puede ser <= -100% (valor <= -1).")

        tipo = str(tasa.tipo).strip().lower()

        if tipo == "efectiva":
            i = float(tasa.valor)

        elif tipo == "nominal":
            periodo_nominal = getattr(tasa, "periodo_nominal", None)
            if periodo_nominal is None:
                raise ValueError("Tasa nominal requiere periodo nominal.")
            if periodo_nominal <= 0 or tasa.periodo <= 0:
                raise ValueError("Los periodos deben ser positivos.")

            m = float(periodo_nominal) / float(tasa.periodo)
            if m <= 0:
                raise ValueError("Relación de periodos inválida (m <= 0).")

            i = float(tasa.valor) / m

        else:
            raise ValueError("Tipo de tasa no reconocido. Use 'efectiva' o 'nominal'.")

        es_anticipada = bool(getattr(tasa, "es_anticipada", False))
        if es_anticipada:
            if i >= 1:
                raise ValueError("Tasa anticipada inválida: debe ser < 1 por período.")
            i = i / (1 - i)

        return round(i, self.precision)

    @staticmethod
    
    def validar_monto_periodos(valor: Number, periodos: int) -> None:
        
        """Validaciones mínimas para Valor presente, valor futuro y series."""
        
        if not isinstance(valor, (int, float)):
            raise TypeError("valor debe ser numérico.")
        if float(valor) < 0:
            raise ValueError("valor debe ser >= 0.")

        if not isinstance(periodos, int):
            raise TypeError("periodos debe ser un entero.")
        if periodos < 0:
            raise ValueError("periodos debe ser >= 0.")

    
    def estandarizar_a_ea(self, tasa: TasaInteres) -> float:
        """
        Convierte cualquier tasa a EA (efectiva anual).

        Args:
            tasa: TasaInteres nominal o efectiva.

        Returns:
            EA como float decimal (ej. 0.2682).
        """
        return float(self.convertidor.tasa_a_ea_std(tasa))

    def estandarizar_lista_a_ea(self, opciones: List[Dict]) -> pd.DataFrame:
        """
        Convierte una lista de opciones con tasas a EA y devuelve un DataFrame.

        Cada opción debe ser dict con:
            - "nombre": str
            - "tasa": TasaInteres

        Args:
            opciones: Lista de opciones.

        Returns:
            DataFrame con columnas: Nombre, EA.
        """
        filas = []
        for op in opciones:
            nombre = op.get("nombre", "Sin nombre")
            tasa = op.get("tasa")

            if not isinstance(tasa, TasaInteres):
                raise ValueError("Cada opción debe incluir una tasa nominal o efectiva.")

            ea = self.estandarizar_a_ea(tasa)
            filas.append({"Nombre": nombre, "EA": round(ea, self.precision)})

        return pd.DataFrame(filas)

    
    def calcular_retorno_a_futuro(self,valor_presente: Number, periodos: int,tasa: TasaInteres ) -> float:
        """
        Calcula el valor futuro (VF) desde un valor presente (VP) con interés compuesto.

        Fórmula:
            VF = VP * (1 + i)^n

        Importante:
        - `periodos` debe estar en la misma unidad periódica de la tasa.
        - Si la tasa es nominal/anticipada, se normaliza internamente a vencida.

        Args:
            valor_presente: Valor presente.
            periodos: Número de períodos (>= 0).
            tasa: TasaInteres.

        Returns:
            Valor futuro (VF).
        """
        self.validar_monto_periodos(valor_presente, periodos)
        i = self.tasa_periodica_vencida(tasa)

        vf = float(valor_presente) * ((1 + i) ** periodos)
        return round(vf, self.money_round)

    
    def graficador_interes_simple(self, principal: Number,tasa: TasaInteres,periodos: int) -> pd.DataFrame:
        """
        Devuelve una serie (DataFrame) lista para graficar con interés simple.

        Serie:
            Valor(t) = P * (1 + i * t)

        Args:
            principal: Monto inicial.
            tasa: TasaInteres (en la periodicidad correcta).
            periodos: Número de períodos.

        Returns:
            DataFrame con columnas: Periodo, Valor.
        """
        self.validar_monto_periodos(principal, periodos)
        i = self.tasa_periodica_vencida(tasa)

        filas = []
        for t in range(0, periodos + 1):
            valor_t = float(principal) * (1 + i * t)
            filas.append({"Periodo": t, "Valor": round(valor_t, self.money_round)})

        return pd.DataFrame(filas)

    def graficador_interes_compuesto(self,principal: Number,tasa: TasaInteres,periodos: int) -> pd.DataFrame:
        """
        Devuelve una serie (DataFrame) lista para graficar con interés compuesto.

        Serie:
            Valor(t) = P * (1 + i)^t

        Args:
            principal: Monto inicial.
            tasa: TasaInteres (en la periodicidad correcta).
            periodos: Número de períodos.

        Returns:
            DataFrame con columnas: Periodo, Valor.
        """
        self.validar_monto_periodos(principal, periodos)
        i = self.tasa_periodica_vencida(tasa)

        filas = []
        for t in range(0, periodos + 1):
            valor_t = float(principal) * ((1 + i) ** t)
            filas.append({"Periodo": t, "Valor": round(valor_t, self.money_round)})

        return pd.DataFrame(filas)

    
    def mostrar_mejor_tasa_de_interes(self, opciones: List[Dict], modo: str = "credito") -> Optional[Dict]:
        
        """
        Devuelve la mejor opción según el modo.

        - modo="credito": menor EA es mejor.
        - modo="inversion": mayor EA es mejor.

        Args:
            opciones: Lista de dicts con {"nombre", "tasa"}.
            modo: "credito" o "inversion".

        Returns:
            Dict con {"Nombre", "EA"} o None si no hay opciones.
        """
        
        if modo not in {"credito", "inversion"}:
            raise ValueError("modo debe ser 'credito' o 'inversion'.")
        if not opciones:
            return None

        df = self.estandarizar_lista_a_ea(opciones)

        if modo == "credito":
            df = df.sort_values(by="EA", ascending=True)
        else:
            df = df.sort_values(by="EA", ascending=False)

        return df.iloc[0].to_dict()


if __name__ == "__main__":
    est = Estandarizador()

    opciones_credito = [
        {"nombre": "Banco A", "tasa": TasaInteres.from_string("24% NA/MV")},
        {"nombre": "Banco B", "tasa": TasaInteres.from_string("2% MV")},
    ]

    print("Mejor crédito (menor EA):", est.mostrar_mejor_tasa_de_interes(opciones_credito))

    vp = 5000000
    t_eff = TasaInteres.from_string("6% TV")
    print("VF:", est.calcular_retorno_a_futuro(vp, 24, t_eff))

    print("\nSerie simple:")
    print(est.graficador_interes_simple(1000000, t_eff, 12))

    print("\nSerie compuesta:")
    print(est.graficador_interes_compuesto(1000000, t_eff, 12))
