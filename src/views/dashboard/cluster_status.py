import flet as ft

class ClusterStatus(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 20
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.border_radius = 10
        self.content = ft.Column(
            [
                ft.Text("Cluster Status", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.PieChart(
                            sections=[
                                ft.PieChartSection(
                                    0,
                                    title="",
                                    color=ft.Colors.GREEN,
                                    radius=40,
                                ),
                                ft.PieChartSection(
                                    0,
                                    title="",
                                    color=ft.Colors.RED,
                                    radius=40,
                                ),
                            ],
                            sections_space=0,
                            center_space_radius=20,
                            height=120,
                            width=120,
                        ),
                        ft.Column(
                            [
                                ft.Text("HEALTHY", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                                ft.Text("Nodes: 0/0 Up", size=12, color=ft.Colors.GREEN_200),
                                ft.Text("Pods: 0/0 Running", size=12, color=ft.Colors.GREEN_200),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND
                )
            ]
        )

    def update_data(self, nodes, pods):
        total_nodes = len(nodes)
        ready_nodes = sum(1 for n in nodes if any(c.type == "Ready" and c.status == "True" for c in n.status.conditions))
        
        total_pods = len(pods)
        running_pods = sum(1 for p in pods if p.status.phase == "Running")

        # Update Chart
        healthy_ratio = (ready_nodes / total_nodes * 100) if total_nodes > 0 else 0
        self.content.controls[2].controls[0].sections[0].value = healthy_ratio
        self.content.controls[2].controls[0].sections[1].value = 100 - healthy_ratio
        
        # Update Text
        status_col = self.content.controls[2].controls[1]
        status_col.controls[1].value = f"Nodes: {ready_nodes}/{total_nodes} Up"
        status_col.controls[2].value = f"Pods: {running_pods}/{total_pods} Running"
        
        self.update()
