import flet as ft
from .header import Header
from .sidebar_left import SidebarLeft
from .sidebar_right import SidebarRight
from .footer import Footer

class AppLayout(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.expand = True
        self.spacing = 0
        self.page = page
        
        # Components
        self.header = Header()
        self.sidebar_left = SidebarLeft()
        self.sidebar_right = SidebarRight()
        self.footer = Footer()
        self.main_content = ft.Container(
            content=ft.Text("Contenido Principal"),
            expand=True,
            bgcolor=ft.Colors.SURFACE,
            padding=20
        )

        # Assemble
        self.controls = [
            self.header,
            ft.Row(
                [
                    self.sidebar_left,
                    self.main_content,
                    self.sidebar_right,
                ],
                expand=True,
                spacing=0,
            ),
            self.footer,
        ]
