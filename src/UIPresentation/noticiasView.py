#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Módulo de Vista para Noticias.
Se encarga de renderizar los datos financieros en controles de Flet.
"""
import flet as ft
import pandas as pd

class NoticiasView:
    """
    Clase de Presentación.
    Responsabilidad única: Convertir datos (DataFrame) en controles visuales.
    No contiene lógica de negocio ni llamadas a APIs.
    """

    # NOTA: Borramos el __init__ porque estaba vacío.
    # Python usa el constructor por defecto automáticamente.
    @staticmethod
    def _safe_icon(name: str, fallback: str = "HELP_OUTLINE"):
        icon = getattr(ft.icons, name, None)
        if icon is not None:
            return icon
        icon = getattr(ft.icons, fallback, None)
        if icon is not None:
            return icon
        return "help_outline"

    def list_tarjetas(self, noticias_df: pd.DataFrame) -> ft.Control:
        """
        Recibe el DataFrame del Repo y devuelve una lista visual.
        """
        # 1. Validación de Tabla Vacía o Nula
        if noticias_df is None or noticias_df.empty:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(self._safe_icon("WARNING_AMBER_ROUNDED", "WARNING"), color="#F59E0B", size=40),
                        ft.Text("No hay noticias financieras recientes.", color="#64748B"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                expand=True,
                padding=20
            )

        # 2. Construcción de la Lista
        lista_controles = []

        for _, row in noticias_df.iterrows():
            # Extracción segura de datos con valores por defecto
            titulo = row.get("Título", "Sin título")
            fuente = row.get("Fuente", "Fuente desconocida")
            fecha = row.get("Fecha", "")
            desc = row.get("Descripción", "Haz clic para leer más...")

            tarjeta = ft.Card(
                elevation=1,
                margin=ft.margin.symmetric(vertical=6, horizontal=2),
                content=ft.Container(
                    bgcolor="#F8FAFC",
                    border_radius=12,
                    padding=12,
                    content=ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Container(
                                    bgcolor="#DCFCE7",
                                    border_radius=8,
                                    padding=8,
                                    content=ft.Icon(self._safe_icon("MONETIZATION_ON", "ATTACH_MONEY"), color="#16A34A"),
                                ),
                                title=ft.Text(
                                    titulo,
                                    weight=ft.FontWeight.BOLD,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS
                                ),
                                subtitle=ft.Text(f"{fuente} • {fecha}", size=12, color="#64748B", italic=True),
                            ),
                            ft.Container(
                                content=ft.Text(
                                    desc,
                                    size=13,
                                    color="#334155",
                                    max_lines=3,
                                    overflow=ft.TextOverflow.ELLIPSIS
                                ),
                                padding=ft.padding.only(left=15, right=15, bottom=10)
                            )
                        ],
                        spacing=6
                    )
                )
            )
            lista_controles.append(tarjeta)

        return ft.ListView(
            controls=lista_controles,
            expand=True,
            spacing=10,
            padding=10
        )
