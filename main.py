import flet as ft

from src.shell.layout import AppLayout

def main(page: ft.Page):
    page.title = "KubeSight"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    
    layout = AppLayout(page)
    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main)
