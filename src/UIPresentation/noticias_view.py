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

    def list_tarjetas(self, noticias_df: pd.DataFrame) -> ft.Control:
        """
        Recibe el DataFrame del Repo y devuelve una lista visual.
        """
        # 1. Validación de Tabla Vacía o Nula
        if noticias_df is None or noticias_df.empty:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color="orange", size=40),
                    ft.Text("No hay noticias financieras recientes.", color="grey")
                ], alignment=ft.MainAxisAlignment.CENTER),
                alignment=ft.alignment.center,
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

            # Validación extra por si la API devuelve None explícito
            if desc is None:
                desc = "Sin descripción disponible."

            tarjeta = ft.Card(
                elevation=5,
                margin=10,
                content=ft.Container(
                    padding=10,
                    content=ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.MONETIZATION_ON, color="green"),
                                title=ft.Text(
                                    titulo,
                                    weight="bold",
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS
                                ),
                                subtitle=ft.Text(f"{fuente} • {fecha}", size=12, italic=True),
                            ),
                            ft.Container(
                                content=ft.Text(
                                    desc,
                                    size=13,
                                    max_lines=3,
                                    overflow=ft.TextOverflow.ELLIPSIS
                                ),
                                padding=ft.padding.only(left=15, right=15, bottom=10)
                            )
                        ],
                        spacing=5
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