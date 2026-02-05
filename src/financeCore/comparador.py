#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd

from .convertidor import Convertidor
from .tasa_interes import TasaInteres
#aaa

class Comparador:
    """
    Compara opciones por tasa y guarda un ranking en un DataFrame.

    Atributos:
        convertidor: Servicio de conversión a EA.
        ranking: Último ranking calculado.
    """

    def __init__(self, precision: int = 6) -> None:
        self.convertidor = Convertidor(precision=precision)
        self.ranking: Optional[pd.DataFrame] = None

    def comparar_escenarios(self, lista_opciones: List[Dict]) -> pd.DataFrame:
        """
        Crédito: menor EA = mejor (menor costo).

        Cada opción debe ser un dict con:
            - "nombre": str
            - "tasa": TasaInteres

        Args:
            lista_opciones: Lista de opciones a comparar.

        Returns:
            DataFrame ordenado con columnas: Nombre, EA, Ranking.
        """
        filas = []
        for opcion in lista_opciones:
            nombre = opcion.get("nombre", "Sin nombre")
            tasa = opcion.get("tasa")

            if not isinstance(tasa, TasaInteres):
                raise ValueError(
                    "Cada opción debe incluir una `tasa` tipo TasaInteres."
                )

            ea = self.convertidor.tasa_a_ea_std(tasa)
            filas.append({"Nombre": nombre, "EA": round(ea, 6)})

        df = pd.DataFrame(filas).sort_values(by="EA", ascending=True)
        df = df.reset_index(drop=True)
        df["Ranking"] = range(1, len(df) + 1)

        self.ranking = df
        return df

    def comparar_mejor_rentabilidad(self, lista_opciones: List[Dict]) -> pd.DataFrame:
        """
        Inversión: mayor EA = mejor (mayor rentabilidad).

        Cada opción debe ser un dict con:
            - "nombre": str
            - "tasa": TasaInteres

        Args:
            lista_opciones: Lista de opciones a comparar.

        Returns:
            DataFrame ordenado con columnas: Nombre, EA, Ranking.
        """
        filas = []
        for opcion in lista_opciones:
            nombre = opcion.get("nombre", "Sin nombre")
            tasa = opcion.get("tasa")

            if not isinstance(tasa, TasaInteres):
                raise ValueError(
                    "Cada opción debe incluir una tasa efectiva o nominal."
                )

            ea = self.convertidor.tasa_a_ea_std(tasa)
            filas.append({"Nombre": nombre, "EA": round(ea, 6)})

        df = pd.DataFrame(filas).sort_values(by="EA", ascending=False)
        df = df.reset_index(drop=True)
        df["Ranking"] = range(1, len(df) + 1)

        self.ranking = df
        return df

    def mejor_opcion(self) -> Optional[Dict]:
        """
        Devuelve la primera fila del último ranking.

        Returns:
            Dict con {"Nombre", "EA", "Ranking"} o None si no hay ranking.
        """
        if self.ranking is None or self.ranking.empty:
            return None
        return self.ranking.iloc[0].to_dict()


if __name__ == "__main__":
    comp = Comparador()

    prestamos = [
        {"nombre": "Banco A", "tasa": TasaInteres.from_string("24% NA/MV")},
        {"nombre": "Banco B", "tasa": TasaInteres.from_string("2% MV")},
        {"nombre": "Banco C", "tasa": TasaInteres.from_string("30% NA/MV")},
    ]

    print("Crédito (menor EA es mejor):")
    print(comp.comparar_escenarios(prestamos))
    print("Mejor opción:", comp.mejor_opcion())

    inversiones = [
        {"nombre": "CDT X", "tasa": TasaInteres.from_string("10% EA")},
        {"nombre": "Fondo Y", "tasa": TasaInteres.from_string("0.8% MV")},
    ]

    print("\nInversión (mayor EA es mejor):")
    print(comp.comparar_mejor_rentabilidad(inversiones))
    print("Mejor opción:", comp.mejor_opcion())
