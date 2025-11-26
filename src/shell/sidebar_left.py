import flet as ft

class SidebarLeft(ft.Container):
    def __init__(self):
        super().__init__()
        self.width = 250
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.padding = 10
        self.animate = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Explorer", weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.MENU_OPEN,
                            on_click=self.toggle_sidebar,
                            tooltip="Collapse Sidebar"
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                ft.Text("Treeview Placeholder"),
            ]
        )

    def toggle_sidebar(self, e):
        if self.width == 250:
            self.width = 60
            self.content.controls[0].controls[0].visible = False # Hide title
            self.content.controls[1].visible = False # Hide divider
            self.content.controls[2].visible = False # Hide treeview
            self.content.controls[0].controls[1].icon = ft.Icons.MENU
        else:
            self.width = 250
            self.content.controls[0].controls[0].visible = True
            self.content.controls[1].visible = True
            self.content.controls[2].visible = True
            self.content.controls[0].controls[1].icon = ft.Icons.MENU_OPEN
        self.update()
