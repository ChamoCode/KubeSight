import flet as ft
from .header import Header

from src.views.resource_view import ResourceView
from src.views.controllers_view import ControllersView

class AppLayout(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.spacing = 0
        self.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        
        from src.views.dashboard.dashboard_view import DashboardView
        self.main_content = ft.Container(
            content=DashboardView(),
            expand=True,
            padding=20,
            alignment=ft.alignment.top_left
        )
        
        # Set the AppBar
        self.page.appbar = Header()

        # Define Controller Submenu Items
        controllers_submenu = ft.PopupMenuButton(
            content=ft.Row([
                ft.Icon(ft.Icons.MEMORY),
                ft.Text("Controllers")
            ]),
            items=[
                ft.PopupMenuItem(text="Deployments", on_click=lambda _: self.page.pubsub.send_all(("show_controllers_filtered", "deployments"))),
                ft.PopupMenuItem(text="CronJobs", on_click=lambda _: self.page.pubsub.send_all(("show_controllers_filtered", "cronjobs"))),
                ft.PopupMenuItem(text="StatefulSets", on_click=lambda _: self.page.pubsub.send_all(("show_controllers_filtered", "statefulsets"))),
                ft.PopupMenuItem(text="All", on_click=lambda _: self.page.pubsub.send_all(("show_controllers_filtered", "all"))),
            ]
        )
        
        # Set the BottomAppBar
        self.page.bottom_appbar = ft.BottomAppBar(
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            shape=ft.NotchShape.CIRCULAR,
            content=ft.Row(
                controls=[
                    ft.IconButton(icon=ft.Icons.HOME, icon_color=ft.Colors.WHITE, on_click=lambda _: self.page.pubsub.send_all("show_dashboard")),
                    ft.Container(expand=True), # Spacer
                    controllers_submenu,
                    ft.Container(expand=True), # Spacer
                    ft.IconButton(icon=ft.Icons.SEARCH, icon_color=ft.Colors.WHITE), # Placeholder
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            height=60,
            padding=ft.padding.symmetric(horizontal=10)
        )
        
        self.controls = [
            ft.Row(
                [
                    self.main_content,
                ],
                expand=True,
                spacing=0
            ),
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
            elif topic == "show_controllers_filtered":
                 self.main_content.content = ControllersView(filter_type=message)
                 self.main_content.update()
        elif data == "show_controllers":
             self.main_content.content = ControllersView(filter_type="all")
             self.main_content.update()
        elif data == "show_dashboard":
             from src.views.dashboard.dashboard_view import DashboardView
             self.main_content.content = DashboardView()
             self.main_content.update()
        elif data == "refresh_resources":
            # Refresh current view if it's ControllersView
            if isinstance(self.main_content.content, ControllersView):
                # We need to preserve the filter type
                current_filter = self.main_content.content.filter_type
                self.main_content.content = ControllersView(filter_type=current_filter)
                self.main_content.update()
