import flet as ft
try:
    from src.UIPresentation.mainApp import MainApp
except ModuleNotFoundError:
    from UIPresentation.mainApp import MainApp

def main(page: ft.Page):
    app = MainApp()
    app.page = page
    app.build_ui()

if __name__ == "__main__":
    runner = getattr(ft, "run", None)
    if callable(runner):
        runner(main)
    else:
        ft.app(
            target=main,
            host="0.0.0.0",
            port=8080
        )
