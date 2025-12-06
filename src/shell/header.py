import flet as ft
from src.services.kube_service import kube_service
from src.views.namespace_manager import NamespaceManager
from src.views.context_manager import ContextManager

class Header(ft.AppBar):
    def __init__(self):
        super().__init__()
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.elevation = 4
        
        # Context Selector
        self.context_dropdown = ft.Dropdown(
            width=200,
            options=[ft.dropdown.Option(c) for c in kube_service.get_contexts()],
            value=kube_service.get_active_context_name(),
            on_change=self.on_context_change,
            text_size=12,
            content_padding=5,
            filled=True,
            bgcolor=ft.Colors.SURFACE,
            border_color=ft.Colors.OUTLINE_VARIANT,
        )

        # Namespace Selector
        self.namespace_dropdown = ft.Dropdown(
            width=200,
            options=[ft.dropdown.Option(ns) for ns in kube_service.get_namespaces()],
            value="default", # Default value, should be dynamic
            on_change=self.on_namespace_change,
            text_size=12,
            content_padding=5,
            filled=True,
            bgcolor=ft.Colors.SURFACE,
            border_color=ft.Colors.OUTLINE_VARIANT,
        )

        self.title = ft.Row([
            ft.IconButton(
                icon=ft.Icons.HOME,
                tooltip="Home",
                on_click=self.go_home
            ),
            ft.Text("KubeSight", size=20, weight=ft.FontWeight.BOLD),
        ])
        
        self.actions = [
            ft.Row(
                [
                    ft.Icon(ft.Icons.DNS, size=16),
                    self.context_dropdown,
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        tooltip="Manage Contexts",
                        on_click=self.open_context_manager
                    ),
                    ft.VerticalDivider(width=10),
                    ft.Icon(ft.Icons.FOLDER_OPEN, size=16),
                    self.namespace_dropdown,
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        tooltip="Manage Namespaces",
                        on_click=self.open_namespace_manager
                    ),
                    ft.Container(width=10),
                    ft.Icon(ft.Icons.PERSON_ROUNDED),
                    ft.Container(width=20),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ]

    def go_home(self, e):
        self.page.pubsub.send_all("show_controllers")

    def on_context_change(self, e):
        if kube_service.set_context(self.context_dropdown.value):
            # Reload namespaces
            self.refresh_namespaces()
            
            # Notify listeners
            self.page.pubsub.send_all("refresh_resources")
            print(f"Context switched to {self.context_dropdown.value}")
        else:
            print(f"Failed to switch context to {self.context_dropdown.value}")

    def on_namespace_change(self, e):
        kube_service.set_namespace(self.namespace_dropdown.value)
        # Notify listeners
        self.page.pubsub.send_all("refresh_resources")
        print(f"Namespace switched to {self.namespace_dropdown.value}")

    def open_namespace_manager(self, e):
        try:
            dialog = NamespaceManager(e.page, on_update=self.refresh_namespaces)
            e.page.open(dialog)
        except Exception as ex:
            print(f"Error opening dialog: {ex}")

    def open_context_manager(self, e):
        try:
            dialog = ContextManager(e.page, on_update=self.refresh_contexts)
            e.page.open(dialog)
        except Exception as ex:
            print(f"Error opening context manager: {ex}")

    def refresh_contexts(self):
        self.context_dropdown.options = [ft.dropdown.Option(c) for c in kube_service.get_contexts()]
        # Check if current value still exists
        current_ctx = self.context_dropdown.value
        if current_ctx not in [opt.key for opt in self.context_dropdown.options]:
             # If current context was deleted, switch to first available or reset
             if self.context_dropdown.options:
                 new_ctx = self.context_dropdown.options[0].key
                 self.context_dropdown.value = new_ctx
                 kube_service.set_context(new_ctx)
             else:
                 self.context_dropdown.value = None
                 
        self.context_dropdown.update()

    def refresh_namespaces(self):
        self.namespace_dropdown.options = [ft.dropdown.Option(ns) for ns in kube_service.get_namespaces()]
        # Check if current value still exists
        current_ns = self.namespace_dropdown.value
        if current_ns not in [opt.key for opt in self.namespace_dropdown.options]:
             self.namespace_dropdown.value = "default"
             kube_service.set_namespace("default")
        self.namespace_dropdown.update()
