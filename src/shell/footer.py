import flet as ft

class Footer(ft.Container):
    def __init__(self):
        super().__init__()
        self.height = 30
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.shadow = ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.SHADOW,
            offset=ft.Offset(0, -5),
        )
        self.padding = ft.padding.symmetric(horizontal=10)
        self.content = ft.Row(
            [
                ft.Text("Cluster: local > Namespace: default", size=12),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
