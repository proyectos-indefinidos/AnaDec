#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Callable

import flet as ft


class HomeView:
    def _safe_icon(self, name: str, fallback: str) -> str:
        return getattr(ft.icons, name, getattr(ft.icons, fallback, fallback))

    def build(self, on_nav: Callable[[int], None], card_builder: Callable[[str, str, ft.Control], ft.Control]) -> ft.Control:
        hero = ft.Container(
            bgcolor="#E2E8F0",
            border_radius=12,
            padding=16,
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text("AnaDec", size=30, weight=ft.FontWeight.BOLD, color="#0F172A"),
                    ft.Text("Convierte y compara tasas facilmente", size=14, color="#334155"),
                ],
            ),
        )

        buttons = ft.Column(
            spacing=10,
            controls=[
                ft.ElevatedButton(
                    "Convertidor",
                    icon=self._safe_icon("SWAP_HORIZ", "SYNC"),
                    height=52,
                    width=260,
                    on_click=lambda e: on_nav(1),
                ),
                ft.ElevatedButton(
                    "Comparador",
                    icon=self._safe_icon("COMPARE_ARROWS", "BALANCE"),
                    height=52,
                    width=260,
                    on_click=lambda e: on_nav(2),
                ),
                ft.OutlinedButton(
                    "Noticias",
                    icon=self._safe_icon("NEWSPAPER", "ARTICLE"),
                    height=46,
                    width=260,
                    on_click=lambda e: on_nav(3),
                ),
            ],
        )

        content = ft.Column(
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[hero, buttons],
        )

        return card_builder(
            "Home",
            "Accede rapido a los modulos principales de la app.",
            content,
        )
