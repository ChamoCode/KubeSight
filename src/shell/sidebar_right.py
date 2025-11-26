import flet as ft

class SidebarRight(ft.Container):
    def __init__(self):
        super().__init__()
        self.width = 200
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.padding = 10
        self.shadow = ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.SHADOW,
            offset=ft.Offset(-5, 0),
        )
        self.content = ft.Column(
            [
                ft.Text("Actions", weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.GridView(
                    runs_count=2,
                    max_extent=100,
                    child_aspect_ratio=1.0,
                    spacing=10,
                    run_spacing=10,
                    controls=[
                        self._build_action_button("Logs", ft.Icons.ARTICLE),
                        self._build_action_button("Delete", ft.Icons.DELETE),
                        self._build_action_button("Edit", ft.Icons.EDIT),
                        self._build_action_button("Shell", ft.Icons.TERMINAL),
                    ]
                )
            ]
        )

    def _build_action_button(self, text, icon):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon),
                    ft.Text(text, size=12)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.SECONDARY_CONTAINER,
            border_radius=5,
            padding=5,
            ink=True,
            on_click=lambda e: print(f"Action: {text}")
        )
