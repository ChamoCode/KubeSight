import flet as ft
from src.services.kube_service import kube_service
from src.views.namespace_manager import NamespaceManager

class Header(ft.Container):
    def __init__(self):
        super().__init__()
        self.height = 60
        self.padding = ft.padding.symmetric(horizontal=20)
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.shadow = ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.SHADOW,
            offset=ft.Offset(0, 5),
        )

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

        self.content = ft.Row(
            [
                ft.Text("KubeSight", size=20, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.DNS, size=16),
                        self.context_dropdown,
                        ft.VerticalDivider(width=10),
                        ft.Icon(ft.Icons.FOLDER_OPEN, size=16),
                        self.namespace_dropdown,
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            tooltip="Manage Namespaces",
                            on_click=self.open_namespace_manager
                        )
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Icon(ft.Icons.PERSON_ROUNDED),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

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

    def refresh_namespaces(self):
        self.namespace_dropdown.options = [ft.dropdown.Option(ns) for ns in kube_service.get_namespaces()]
        # Check if current value still exists
        current_ns = self.namespace_dropdown.value
        if current_ns not in [opt.key for opt in self.namespace_dropdown.options]:
             self.namespace_dropdown.value = "default"
             kube_service.set_namespace("default")
        self.namespace_dropdown.update()
