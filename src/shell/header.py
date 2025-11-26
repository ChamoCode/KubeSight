import flet as ft
from src.services.kube_service import kube_service

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
            self.namespace_dropdown.options = [ft.dropdown.Option(ns) for ns in kube_service.get_namespaces()]
            self.namespace_dropdown.value = "default" # Reset to default or first available
            self.namespace_dropdown.update()
            print(f"Context switched to {self.context_dropdown.value}")
        else:
            print(f"Failed to switch context to {self.context_dropdown.value}")
