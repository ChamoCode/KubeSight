import flet as ft

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
        self.content = ft.Row(
            [
                ft.Text("KubeSight", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True), # Spacer
                ft.Icon(ft.Icons.PERSON_ROUNDED),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
