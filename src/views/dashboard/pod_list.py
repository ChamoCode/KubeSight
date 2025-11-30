import flet as ft

class PodList(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 20
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.border_radius = 10
        self.content = ft.Column(
            [
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Type")),
                        ft.DataColumn(ft.Text("Name")),
                        ft.DataColumn(ft.Text("Status")),
                        ft.DataColumn(ft.Text("Status")), # Duplicate for visual match
                        ft.DataColumn(ft.Text("Age")),
                    ],
                    rows=[
                        self._build_row("Pod", "data-proc-01", "Running", "Running", "2d"),
                        self._build_row("Pod", "web-app", "Running", "Running", "5d"),
                        self._build_row("Pod", "Deployment", "Running", "Running", "5d"),
                        self._build_row("Pod", "db-backp-01", "Error", "Error", "1h", is_error=True),
                    ],
                    width=float("inf"), # Expand to fill width
                    heading_row_height=40,
                    data_row_max_height=50,
                )
            ],
            scroll=ft.ScrollMode.AUTO
        )

    def _build_row(self, type_, name, status, status_display, age, is_error=False):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(type_)),
                ft.DataCell(ft.Text(name)),
                ft.DataCell(ft.Text(status)),
                ft.DataCell(ft.Text(status_display, color=ft.Colors.RED if is_error else ft.Colors.GREEN)),
                ft.DataCell(ft.Text(age)),
            ],
        )

    def update_data(self, pods):
        import datetime
        
        rows = []
        # Sort by creation timestamp desc
        sorted_pods = sorted(pods, key=lambda p: p.metadata.creation_timestamp, reverse=True)
        
        for pod in sorted_pods[:10]: # Show top 10
            name = pod.metadata.name
            status = pod.status.phase
            
            # Age
            age = "Unknown"
            if pod.metadata.creation_timestamp:
                delta = datetime.datetime.now(datetime.timezone.utc) - pod.metadata.creation_timestamp
                if delta.days > 0:
                    age = f"{delta.days}d"
                elif delta.seconds > 3600:
                    age = f"{delta.seconds // 3600}h"
                else:
                    age = f"{delta.seconds // 60}m"

            is_error = status not in ["Running", "Succeeded"]
            
            rows.append(self._build_row("Pod", name, status, status, age, is_error))
            
        self.content.controls[0].rows = rows
        self.update()
