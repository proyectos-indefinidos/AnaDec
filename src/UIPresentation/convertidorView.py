#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Callable

import flet as ft

try:
    from financeCore.convertidor import Convertidor
except ModuleNotFoundError:
    from src.financeCore.convertidor import Convertidor


class ConvertidorView:
    def __init__(
        self,
        convertidor: Convertidor,
        tasa_builder: Callable[[str, str, str, str, str, str], object],
        period_to_months: Callable[[str], int],
        show_error: Callable[[str], None] | None = None,
    ) -> None:
        self.convertidor = convertidor
        self.tasa_builder = tasa_builder
        self.period_to_months = period_to_months
        self.show_error = show_error
        self.page: ft.Page | None = None

        self.tf_tasa = ft.TextField(label="Ingresa la tasa (%)", hint_text="Ej: 24")
        self.dd_tipo = ft.Dropdown(
            label="Tipo de tasa",
            options=[
                ft.dropdown.Option("efectiva", "Efectiva"),
                ft.dropdown.Option("nominal", "Nominal"),
            ],
            value="efectiva",
        )
        self.dd_periodo = ft.Dropdown(
            label="Periodo",
            options=self._period_options(),
            value="MV",
        )
        self.dd_convertir_a = ft.Dropdown(
            label="Convertir a",
            options=self._period_options(),
            value="EA",
        )
        self.resultado = ft.Text(
            "Ingresa los datos y presiona Convertir.",
            size=15,
            color="#334155",
        )

    @staticmethod
    def _period_options() -> list[ft.dropdown.Option]:
        return [
            ft.dropdown.Option("MV", "Mensual (MV)"),
            ft.dropdown.Option("TV", "Trimestral (TV)"),
            ft.dropdown.Option("SV", "Semestral (SV)"),
            ft.dropdown.Option("EA", "Anual (EA)"),
        ]

    @staticmethod
    def _code_to_main_period(code: str) -> str:
        return {
            "MV": "M",
            "TV": "T",
            "SV": "S",
            "EA": "A",
        }.get((code or "").upper(), "")

    def build(
        self,
        page: ft.Page,
        card_builder: Callable[[str, str, ft.Control], ft.Control],
    ) -> ft.Control:
        self.page = page

        content = ft.Column(
            spacing=12,
            controls=[
                self.tf_tasa,
                self.dd_tipo,
                self.dd_periodo,
                self.dd_convertir_a,
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Convertir", on_click=self.on_convertir),
                    ]
                ),
                ft.Container(
                    bgcolor="#E0F2FE",
                    border_radius=10,
                    padding=12,
                    content=self.resultado,
                ),
            ],
        )

        return card_builder(
            "Convertidor de tasas",
            "Convierte tasas entre MV, TV, SV y EA con el motor existente.",
            content,
        )

    def on_convertir(self, e):
        try:
            valor_raw = (self.tf_tasa.value or "").strip()
            if not valor_raw:
                raise ValueError("Ingresa el valor de la tasa en %.")
            float(valor_raw.replace(",", "."))

            tipo = (self.dd_tipo.value or "efectiva").lower()
            periodo_origen = (self.dd_periodo.value or "MV").upper()
            periodo_destino = (self.dd_convertir_a.value or "EA").upper()

            if tipo == "efectiva":
                tasa = self.tasa_builder(valor_raw, "efectiva", periodo_origen, "A", "M", "V")
            else:
                cap = self._code_to_main_period(periodo_origen)
                if not cap:
                    raise ValueError("Periodo origen invalido.")
                tasa = self.tasa_builder(valor_raw, "nominal", "MV", "A", cap, "V")

            meses_destino = self.period_to_months(self._code_to_main_period(periodo_destino))
            if meses_destino <= 0:
                raise ValueError("Periodo destino invalido.")

            convertida = self.convertidor.cambiar_frecuencia(tasa, meses_destino)
            ea = self.convertidor.tasa_a_ea_std(convertida)

            self.resultado.value = f"Equivale a: {convertida.to_string()} (EA: {ea * 100:.4f}%)"
            self.resultado.color = "#0F172A"
        except Exception as ex:
            self.resultado.value = f"Error: {ex}"
            self.resultado.color = "#B91C1C"
            if self.show_error is not None:
                self.show_error(f"Error en convertidor: {ex}")
        finally:
            if self.page is not None:
                self.page.update()
