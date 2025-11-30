import flet as ft

class Alerts(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 20
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.border_radius = 10
        self.content = ft.Column(
            [
                ft.Text("Alerts", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                self._build_alert_item("Node 'worker-03' Disk Full", ft.Colors.RED),
                ft.Container(height=10),
                self._build_alert_item("Pod 'data-proc-07' Restarting", ft.Colors.RED),
            ]
        )

    def _build_alert_item(self, message, color):
        return ft.Row(
            [
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=color, size=20),
                ft.Text(message, color=color, size=14, expand=True),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

    def update_data(self, events):
        # Filter for Warning events
        warnings = [e for e in events if e.type == "Warning"]
        
        # Take top 5
        top_warnings = warnings[:5]
        
        new_controls = [
            ft.Text("Alerts", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
        ]
        
        if not top_warnings:
            new_controls.append(ft.Text("No critical alerts", color=ft.Colors.GREEN))
        else:
            for w in top_warnings:
                msg = f"{w.involved_object.kind} '{w.involved_object.name}': {w.message}"
                new_controls.append(self._build_alert_item(msg, ft.Colors.RED))
                new_controls.append(ft.Container(height=10))
                
        self.content.controls = new_controls
        self.update()
