import flet as ft
from src.services.kube_service import kube_service

class SidebarLeft(ft.Container):
    def __init__(self):
        super().__init__()
        self.width = 250
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.padding = 0
        self.animate = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        
        self.tree_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self._load_resources()

        self.content = ft.Column(
            [
                ft.Container(
                    padding=10,
                    content=ft.Row(
                        [
                            ft.Text("Explorer", weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.Icons.MENU_OPEN,
                                on_click=self.toggle_sidebar,
                                tooltip="Collapse Sidebar"
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                ),
                ft.Divider(height=1, thickness=1),
                self.tree_view,
            ],
            spacing=0,
            expand=True
        )

    def _load_resources(self):
        self.tree_view.controls.clear()
        
        # Deployments
        deployments = kube_service.list_deployments()
        deployment_tiles = [
            ft.ListTile(
                title=ft.Text(d, size=12),
                leading=ft.Icon(ft.Icons.APPS, size=14),
                content_padding=ft.padding.only(left=30),
                on_click=lambda e, name=d: print(f"Selected Deployment: {name}")
            ) for d in deployments
        ]
        
        # CronJobs
        cronjobs = kube_service.list_cronjobs()
        cronjob_tiles = [
            ft.ListTile(
                title=ft.Text(c, size=12),
                leading=ft.Icon(ft.Icons.SCHEDULE, size=14),
                content_padding=ft.padding.only(left=30),
                on_click=lambda e, name=c: print(f"Selected CronJob: {name}")
            ) for c in cronjobs
        ]

        self.tree_view.controls.extend([
            ft.ExpansionTile(
                title=ft.Text("Workloads", weight=ft.FontWeight.BOLD),
                leading=ft.Icon(ft.Icons.WORK),
                initially_expanded=True,
                controls=[
                    ft.ExpansionTile(
                        title=ft.Text("Deployments"),
                        leading=ft.Icon(ft.Icons.APPS),
                        controls=deployment_tiles,
                        initially_expanded=True if deployment_tiles else False
                    ),
                    ft.ExpansionTile(
                        title=ft.Text("CronJobs"),
                        leading=ft.Icon(ft.Icons.SCHEDULE),
                        controls=cronjob_tiles
                    )
                ]
            )
        ])

    def toggle_sidebar(self, e):
        if self.width == 250:
            self.width = 60
            self.content.controls[0].content.controls[0].visible = False # Hide title
            self.content.controls[1].visible = False # Hide divider
            self.tree_view.visible = False # Hide treeview
            self.content.controls[0].content.controls[1].icon = ft.Icons.MENU
        else:
            self.width = 250
            self.content.controls[0].content.controls[0].visible = True
            self.content.controls[1].visible = True
            self.tree_view.visible = True
            self.content.controls[0].content.controls[1].icon = ft.Icons.MENU_OPEN
        self.update()

    def did_mount(self):
        self.page.pubsub.subscribe(self.on_refresh)

    def on_refresh(self, topic):
        if topic == "refresh_resources":
            self._load_resources()
            self.update()
