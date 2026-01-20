import flet as ft   

def main(page: ft.Page):
    page.title = "AnaDec - Prototipo"
    page.add(ft.Text(value="El contenedor de Docker está funcionando.", size=30))
    page.update()

# CAMBIO AQUÍ: Quitamos 'view=ft.WEB_BROWSER'
# Docker ya sabe qué hacer gracias a las variables de entorno.
ft.app(target=main, port=8080)