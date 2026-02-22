#!/usr/bin/python
# -*- coding: utf-8 -*-

import flet as ft
import pandas as pd

try:
    from dataAccess.newsRepo import NewsRepo
    from financeCore.convertidor import Convertidor
    from financeCore.calculador import Calculador
    from financeCore.comparador import Comparador
    from financeCore.tasa_interes import TasaInteres
    from UIPresentation.convertidorView import ConvertidorView
    from UIPresentation.homeView import HomeView
    from UIPresentation.noticiasView import NoticiasView
except ModuleNotFoundError:
    from src.dataAccess.newsRepo import NewsRepo
    from src.financeCore.convertidor import Convertidor
    from src.financeCore.calculador import Calculador
    from src.financeCore.comparador import Comparador
    from src.financeCore.tasa_interes import TasaInteres
    from src.UIPresentation.convertidorView import ConvertidorView
    from src.UIPresentation.homeView import HomeView
    from src.UIPresentation.noticiasView import NoticiasView


class MainApp:
    def __init__(self):
        self.page: ft.Page | None = None

        # Servicios / Core
        self.convertidor = Convertidor()
        self.calculador = Calculador()
        self.comparador = Comparador()
        self.servicio_noticias = NewsRepo()

        # Presentación
        self.home_view = HomeView()
        self.noticias_view = NoticiasView()
        self.convertidor_view = ConvertidorView(
            convertidor=self.convertidor,
            tasa_builder=self._build_tasa,
            period_to_months=self._period_to_months,
            show_error=self.mostrar_error,
        )

        # Estado de navegación
        self.current_view = 0
        self.nav_buttons: list[ft.OutlinedButton] = []

        # Contenido principal
        self.content = ft.Container(expand=True, padding=20)

        # Calculator UI refs
        self.tf_monto = ft.TextField(
            label="Monto",
            hint_text="Ej: 10000000",
        )
        self.tf_plazos = ft.TextField(
            label="Plazos (n)",
            hint_text="Ej: 12",
        )
        self.tf_tasa = ft.TextField(
            label="Valor de tasa (%)",
            hint_text="Ej: 24",
        )
        self.dd_tasa_tipo = ft.Dropdown(
            label="Tipo de tasa",
            options=[
                ft.dropdown.Option("nominal"),
                ft.dropdown.Option("efectiva"),
            ],
            value="nominal",
        )
        self.dd_tasa_eff_periodo = ft.Dropdown(
            label="Período efectiva",
            options=[
                ft.dropdown.Option("MV"),
                ft.dropdown.Option("TV"),
                ft.dropdown.Option("SV"),
                ft.dropdown.Option("EA"),
            ],
            value="MV",
        )
        self.dd_tasa_nom_periodo = ft.Dropdown(
            label="Período nominal (N?)",
            options=[
                ft.dropdown.Option("M"),
                ft.dropdown.Option("T"),
                ft.dropdown.Option("S"),
                ft.dropdown.Option("A"),
            ],
            value="A",
        )
        self.dd_tasa_cap_periodo = ft.Dropdown(
            label="Capitalización (/?)",
            options=[
                ft.dropdown.Option("M"),
                ft.dropdown.Option("T"),
                ft.dropdown.Option("S"),
                ft.dropdown.Option("A"),
            ],
            value="M",
        )
        self.dd_tasa_vencida = ft.Dropdown(
            label="Modalidad",
            options=[
                ft.dropdown.Option("V"),
                ft.dropdown.Option("A"),
            ],
            value="V",
        )
        self.dd_operacion = ft.Dropdown(
            label="Operación",
            options=[
                ft.dropdown.Option("cuota_fija"),
                ft.dropdown.Option("interes_simple"),
                ft.dropdown.Option("valor_futuro"),
                ft.dropdown.Option("valor_presente"),
            ],
            value="cuota_fija",
        )
        self.calc_result = ft.Text(
            "Ingresa datos y haz clic en Calcular.",
            size=15,
            color="#334155",
        )

        # Comparador UI refs
        self.comparador_rows: list[dict] = []
        self.comp_best_text = ft.Text(
            "Aún no hay ranking calculado.",
            size=14,
            color="#334155",
        )
        self.comp_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("EA")),
                ft.DataColumn(ft.Text("Ranking")),
            ],
            rows=[],
        )

        # Noticias UI refs
        self.tf_news_filter = ft.TextField(
            label="Filtro de noticias (opcional)",
            hint_text="Ej: inflación Colombia",
            expand=True,
        )
        self.news_list_container = ft.Container(expand=True)

    # ---------- UI BASE ----------

    def build_ui(self):
        assert self.page is not None

        self.page.title = "AnaDec"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.spacing = 0
        self.page.bgcolor = "#F1F5F9"

        self.page.appbar = ft.AppBar(
            title=ft.Text("AnaDec", weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor="#0F172A",
        )

        self.nav_buttons = [
            ft.OutlinedButton(
                "Home",
                icon=self._safe_icon("HOME", "HOME_OUTLINED"),
                on_click=lambda e: self.cambiar_vista(0),
            ),
            ft.OutlinedButton(
                "Convertidor",
                icon=self._safe_icon("SWAP_HORIZ", "SYNC"),
                on_click=lambda e: self.cambiar_vista(1),
            ),
            ft.OutlinedButton(
                "Comparador",
                icon=self._safe_icon("COMPARE_ARROWS", "BALANCE"),
                on_click=lambda e: self.cambiar_vista(2),
            ),
            ft.OutlinedButton(
                "Noticias",
                icon=self._safe_icon("NEWSPAPER", "ARTICLE"),
                on_click=lambda e: self.cambiar_vista(3),
            ),
        ]

        nav_bar = ft.Container(
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            bgcolor="#E2E8F0",
            content=ft.Row(controls=self.nav_buttons, wrap=True, spacing=8),
        )

        body = ft.Column(
            controls=[
                nav_bar,
                self.content,
            ],
            expand=True,
            spacing=0,
        )

        if len(self.comparador_rows) == 0:
            self._add_comp_row()
            self._add_comp_row()

        self.page.add(body)
        self.cambiar_vista(0)

    @staticmethod
    def _safe_icon(name: str, fallback: str) -> str:
        return getattr(ft.icons, name, getattr(ft.icons, fallback, fallback))

    def _card(self, title: str, subtitle: str, content: ft.Control) -> ft.Control:
        return ft.Container(
            expand=True,
            bgcolor="#FFFFFF",
            border_radius=14,
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color="#0F172A"),
                    ft.Text(subtitle, size=13, color="#475569"),
                    ft.Divider(height=16),
                    content,
                ],
                spacing=8,
            ),
        )

    @staticmethod
    def _period_to_months(code: str) -> int:
        return {"M": 1, "T": 3, "S": 6, "A": 12}.get((code or "").upper(), 0)

    def _build_tasa(self, valor_raw: str, tipo: str, eff: str, nom: str, cap: str, modalidad: str) -> TasaInteres:
        valor = (valor_raw or "").replace(",", ".").strip()
        if not valor:
            raise ValueError("Ingresa el valor de la tasa en %.")

        try:
            float(valor)
        except ValueError as ex:
            raise ValueError("El valor de tasa debe ser numérico.") from ex

        tipo_norm = (tipo or "").strip().lower()
        if tipo_norm == "efectiva":
            return TasaInteres.from_string(f"{valor}% {eff}")

        if self._period_to_months(nom) < self._period_to_months(cap):
            raise ValueError("En tasa nominal, el período nominal debe ser >= al de capitalización.")
        return TasaInteres.from_string(f"{valor}% N{nom}/{cap}{modalidad}")

    def cambiar_vista(self, index: int):
        self.current_view = index

        for i, btn in enumerate(self.nav_buttons):
            btn.disabled = (i == index)

        if index == 0:
            self.content.content = self._view_home()
        elif index == 1:
            self.content.content = self._view_convertidor()
        elif index == 2:
            self.content.content = self._view_comparador()
        elif index == 3:
            self.content.content = self._view_noticias()
        else:
            self.content.content = ft.Text("Vista no implementada")

        self.page.update()

    def mostrar_error(self, msg: str):
        assert self.page is not None
        self.page.snack_bar = ft.SnackBar(
            ft.Text(msg, color="#FFFFFF"),
            bgcolor="#B91C1C",
            open=True,
        )
        self.page.update()

    # ---------- VISTAS ----------

    def _view_home(self) -> ft.Control:
        return self.home_view.build(
            on_nav=self.cambiar_vista,
            card_builder=self._card,
        )

    def _view_convertidor(self) -> ft.Control:
        assert self.page is not None
        return self.convertidor_view.build(
            page=self.page,
            card_builder=self._card,
        )

    def _view_calculos(self) -> ft.Control:
        try:
            tasa_controls = [
                self.tf_tasa,
                self.dd_tasa_tipo,
                ft.Text("Si eliges efectiva, usa 'Período efectiva'.", size=12, color="#64748B"),
                self.dd_tasa_eff_periodo,
                ft.Text("Si eliges nominal, usa N? / ? y modalidad V/A.", size=12, color="#64748B"),
                self.dd_tasa_nom_periodo,
                self.dd_tasa_cap_periodo,
                self.dd_tasa_vencida,
            ]

            content = ft.Column(
                spacing=12,
                controls=[
                    self.tf_monto,
                    self.tf_plazos,
                    ft.Container(
                        bgcolor="#F8FAFC",
                        border_radius=10,
                        padding=10,
                        content=ft.Column(
                            controls=[
                                ft.Text("Configura la tasa", weight=ft.FontWeight.W_600),
                                ft.Text("Selecciona solo tasas permitidas por el sistema.", size=12, color="#64748B"),
                            ] + tasa_controls,
                            spacing=8,
                        ),
                    ),
                    self.dd_operacion,
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "Calcular",
                                on_click=self.on_calcular,
                            ),
                            ft.OutlinedButton("Limpiar", on_click=lambda e: self._clear_calc()),
                        ],
                    ),
                    ft.Container(
                        bgcolor="#E0F2FE",
                        border_radius=10,
                        padding=12,
                        content=self.calc_result,
                    ),
                ],
            )
            return self._card(
                "Calculadora financiera",
                "Calcula cuota fija, interés simple, valor futuro y valor presente.",
                content,
            )
        except Exception as ex:
            return self._card(
                "Calculadora financiera",
                "Error renderizando controles.",
                ft.Text(f"Detalle: {ex}", color="#B91C1C"),
            )

    def _view_comparador(self) -> ft.Control:
        rows_ui = ft.Column(
            expand=False,
            spacing=10,
            controls=[self._comp_row_ui(r) for r in self.comparador_rows],
        )

        controls = [
            ft.Text(
                "Define cada opción con tasa seleccionable (tipo y períodos válidos).",
                size=13,
                color="#475569",
            ),
            ft.Row(
                [self._comp_actions_left(), self._comp_actions_right()],
                wrap=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Container(content=rows_ui, padding=ft.padding.only(top=8, bottom=8)),
            ft.Divider(),
            ft.Text("Ranking (EA)", weight=ft.FontWeight.W_600),
            ft.Container(content=self.comp_table, expand=True),
            ft.Container(
                bgcolor="#ECFEFF",
                border_radius=10,
                padding=12,
                content=self.comp_best_text,
            ),
        ]

        if len(self.comparador_rows) == 0:
            controls.insert(0, ft.Text("No hay opciones todavía. Agrega al menos dos.", color="#64748B"))

        return self._card(
            "Comparador de tasas",
            "Compara opciones de crédito o inversión usando EA estandarizada.",
            ft.Column(expand=True, spacing=10, controls=controls),
        )

    def _comp_actions_left(self) -> ft.Control:
        return ft.Row(
            controls=[
                ft.ElevatedButton(
                    "Agregar opción",
                    on_click=lambda e: self._add_comp_row(),
                ),
            ],
            spacing=8,
        )

    def _comp_actions_right(self) -> ft.Control:
        return ft.Row(
            controls=[
                ft.OutlinedButton("Comparar crédito", on_click=lambda e: self._run_comp(modo="credito")),
                ft.OutlinedButton("Comparar inversión", on_click=lambda e: self._run_comp(modo="inversion")),
            ],
            spacing=8,
        )

    def _view_noticias(self) -> ft.Control:
        if self.news_list_container.content is None:
            self.news_list_container.content = self.noticias_view.list_tarjetas(pd.DataFrame())

        api_hint = None
        if not self.servicio_noticias.api_key:
            api_hint = ft.Container(
                bgcolor="#FEF3C7",
                border_radius=10,
                padding=10,
                content=ft.Text(
                    "No se encontró NEWS_API_KEY. Define la variable para cargar noticias reales.",
                    color="#92400E",
                    size=12,
                ),
            )

        controls = [
            ft.Row(
                [
                    self.tf_news_filter,
                    ft.ElevatedButton(
                        "Actualizar",
                        on_click=self.on_actualizar_noticias,
                    ),
                ],
                wrap=True,
            ),
            ft.Divider(),
        ]
        if api_hint:
            controls.append(api_hint)
        controls.append(ft.Container(content=self.news_list_container, expand=True))

        return self._card(
            "Noticias financieras",
            "Actualiza titulares recientes y filtra por tema específico.",
            ft.Column(expand=True, spacing=12, controls=controls),
        )

    # ---------- HANDLERS ----------

    def _clear_calc(self):
        self.tf_monto.value = ""
        self.tf_plazos.value = ""
        self.tf_tasa.value = ""
        self.dd_tasa_tipo.value = "nominal"
        self.dd_tasa_eff_periodo.value = "MV"
        self.dd_tasa_nom_periodo.value = "A"
        self.dd_tasa_cap_periodo.value = "M"
        self.dd_tasa_vencida.value = "V"
        self.dd_operacion.value = "cuota_fija"
        self.calc_result.value = "Ingresa datos y haz clic en Calcular."
        self.page.update()

    def on_calcular(self, e):
        try:
            monto = float((self.tf_monto.value or "").replace(",", "").strip())
            n = int((self.tf_plazos.value or "").strip())
            tasa = self._build_tasa(
                valor_raw=self.tf_tasa.value,
                tipo=self.dd_tasa_tipo.value,
                eff=self.dd_tasa_eff_periodo.value,
                nom=self.dd_tasa_nom_periodo.value,
                cap=self.dd_tasa_cap_periodo.value,
                modalidad=self.dd_tasa_vencida.value,
            )

            op = self.dd_operacion.value
            if op == "cuota_fija":
                out = self.calculador.calcular_cuota_fija(monto, tasa, n)
                label = "Cuota fija"
            elif op == "interes_simple":
                out = self.calculador.interes_simple(monto, tasa, n)
                label = "Interés simple acumulado"
            elif op == "valor_futuro":
                out = self.calculador.valor_futuro(monto, tasa, n)
                label = "Valor futuro"
            elif op == "valor_presente":
                out = self.calculador.valor_presente(monto, tasa, n)
                label = "Valor presente"
            else:
                raise ValueError("Operación no soportada.")

            self.calc_result.value = f"{label}: {out:,.2f}"
            self.calc_result.color = "#0F172A"
            self.page.update()
        except Exception as ex:
            self.mostrar_error(f"Error en cálculo: {ex}")

    def _add_comp_row(self):
        row = {
            "name": ft.TextField(label="Nombre", hint_text="Ej: Banco A", expand=True),
            "valor": ft.TextField(label="Tasa (%)", hint_text="Ej: 24"),
            "tipo": ft.Dropdown(
                label="Tipo",
                options=[ft.dropdown.Option("nominal"), ft.dropdown.Option("efectiva")],
                value="nominal",
            ),
            "eff": ft.Dropdown(
                label="Efectiva",
                options=[
                    ft.dropdown.Option("MV"),
                    ft.dropdown.Option("TV"),
                    ft.dropdown.Option("SV"),
                    ft.dropdown.Option("EA"),
                ],
                value="MV",
            ),
            "nom": ft.Dropdown(
                label="N?",
                options=[
                    ft.dropdown.Option("M"),
                    ft.dropdown.Option("T"),
                    ft.dropdown.Option("S"),
                    ft.dropdown.Option("A"),
                ],
                value="A",
            ),
            "cap": ft.Dropdown(
                label="/?",
                options=[
                    ft.dropdown.Option("M"),
                    ft.dropdown.Option("T"),
                    ft.dropdown.Option("S"),
                    ft.dropdown.Option("A"),
                ],
                value="M",
            ),
            "mod": ft.Dropdown(
                label="V/A",
                options=[ft.dropdown.Option("V"), ft.dropdown.Option("A")],
                value="V",
            ),
        }
        self.comparador_rows.append(row)
        if self.current_view == 2 and self.page is not None:
            self.cambiar_vista(2)

    def _comp_row_ui(self, row: dict) -> ft.Control:
        del_btn = ft.IconButton(
            icon="delete",
            tooltip="Eliminar",
            on_click=lambda e: self._remove_comp_row(row),
        )
        return ft.Row(
            wrap=True,
            controls=[
                ft.Container(
                    content=ft.Column(
                        spacing=6,
                        controls=[
                            row["name"],
                            row["valor"],
                            row["tipo"],
                            ft.Text("Para efectiva usa este período:", size=11, color="#64748B"),
                            row["eff"],
                            ft.Text("Para nominal usa N? / ? y V/A:", size=11, color="#64748B"),
                            ft.Row([row["nom"], row["cap"], row["mod"]], spacing=6, wrap=True),
                        ],
                    ),
                    width=520,
                ),
                del_btn,
            ],
        )

    def _remove_comp_row(self, row: dict):
        self.comparador_rows = [r for r in self.comparador_rows if r is not row]
        if self.current_view == 2 and self.page is not None:
            self.cambiar_vista(2)

    def _run_comp(self, modo: str):
        try:
            opciones = []
            for r in self.comparador_rows:
                nombre = (r["name"].value or "").strip()
                valor = (r["valor"].value or "").strip()
                if not nombre or not valor:
                    continue
                tasa = self._build_tasa(
                    valor_raw=valor,
                    tipo=r["tipo"].value,
                    eff=r["eff"].value,
                    nom=r["nom"].value,
                    cap=r["cap"].value,
                    modalidad=r["mod"].value,
                )
                opciones.append({"nombre": nombre, "tasa": tasa})

            if len(opciones) < 2:
                raise ValueError("Agrega al menos 2 opciones válidas para comparar.")

            if modo == "credito":
                df = self.comparador.comparar_escenarios(opciones)
                criterio = "menor EA"
            else:
                df = self.comparador.comparar_mejor_rentabilidad(opciones)
                criterio = "mayor EA"

            self.comp_table.rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row["Nombre"]))),
                        ft.DataCell(ft.Text(f"{float(row['EA']) * 100:.2f}%")),
                        ft.DataCell(ft.Text(str(int(row["Ranking"])))),
                    ]
                )
                for _, row in df.iterrows()
            ]

            mejor = self.comparador.mejor_opcion()
            if mejor:
                self.comp_best_text.value = (
                    f"Mejor opción por {criterio}: {mejor['Nombre']} "
                    f"({float(mejor['EA']) * 100:.2f}% EA)."
                )
            else:
                self.comp_best_text.value = "No se pudo determinar una opción ganadora."
            self.comp_best_text.color = "#0F172A"

            self.page.update()
        except Exception as ex:
            self.mostrar_error(f"Error comparando tasas: {ex}")

    def on_actualizar_noticias(self, e):
        try:
            self.news_list_container.content = ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    controls=[ft.ProgressRing()],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                ),
            )
            self.page.update()

            filtro = (self.tf_news_filter.value or "").strip() or None
            self.servicio_noticias.force_update()
            df = self.servicio_noticias.get_noticias(filtro=filtro)
            self.news_list_container.content = self.noticias_view.list_tarjetas(df)

            if df.empty and not self.servicio_noticias.api_key:
                self.mostrar_error("Configura NEWS_API_KEY para traer noticias desde la API.")
                return

            self.page.update()
        except Exception as ex:
            self.mostrar_error(f"Error cargando noticias: {ex}")
