import flet as ft
from .header import Header
from .sidebar_left import SidebarLeft
from .sidebar_right import SidebarRight
from .footer import Footer

from src.views.resource_view import ResourceView

class AppLayout(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.spacing = 0
        
        self.sidebar_left = SidebarLeft()
        self.sidebar_right = SidebarRight()
        self.main_content = ft.Container(
            content=ft.Text("Contenido Principal", size=20),
            expand=True,
            padding=20,
            alignment=ft.alignment.center
        )
        
        self.controls = [
            self.sidebar_left,
            ft.Column(
                [
                    Header(),
                    ft.Row(
                        [
                            self.main_content,
                            self.sidebar_right
                        ],
                        expand=True,
                        spacing=0
                    ),
                    Footer()
                ],
                expand=True,
                spacing=0
            )
        ]

    def did_mount(self):
        self.page.pubsub.subscribe(self.on_message)

    def on_message(self, data):
        if isinstance(data, tuple) and len(data) == 2:
            topic, message = data
            if topic == "resource_selected":
                self.main_content.content = ResourceView(
                    message["type"],
                    message["name"],
                    message["namespace"]
                )
                self.main_content.alignment = ft.alignment.top_left # Reset alignment
                self.main_content.update()
