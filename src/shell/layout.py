import flet as ft
from .header import Header
from .sidebar_left import SidebarLeft
from .sidebar_right import SidebarRight
from .footer import Footer

from src.views.resource_view import ResourceView
from src.views.controllers_view import ControllersView

class AppLayout(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.spacing = 0
        self.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        
        self.sidebar_left = SidebarLeft()
        self.sidebar_right = SidebarRight()
        self.main_content = ft.Container(
            content=ControllersView(),
            expand=True,
            padding=20,
            alignment=ft.alignment.top_left
        )
        
        self.controls = [
            Header(),
            ft.Row(
                [
                    self.sidebar_left,
                    self.main_content,
                    self.sidebar_right
                ],
                expand=True,
                spacing=0
            ),
            Footer()
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
                self.main_content.update()
        elif data == "show_controllers":
             self.main_content.content = ControllersView()
             self.main_content.update()
        elif data == "refresh_resources":
            # Refresh current view if it's ControllersView
            if isinstance(self.main_content.content, ControllersView):
                self.main_content.content = ControllersView()
                self.main_content.update()
