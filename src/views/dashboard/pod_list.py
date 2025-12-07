import flet as ft
import datetime

class PodList(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 20
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.border_radius = 10
        self.pods = []
        self.sort_column_index = 0
        self.sort_ascending = True
        
        self.datatable = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Namespace"), on_sort=self._on_sort),
                ft.DataColumn(ft.Text("Name"), on_sort=self._on_sort),
                ft.DataColumn(ft.Text("Controller"), on_sort=self._on_sort),
                ft.DataColumn(ft.Text("Status"), on_sort=self._on_sort),
                ft.DataColumn(ft.Text("Age"), on_sort=self._on_sort),
            ],
            width=float("inf"), # Expand to fill width
            heading_row_height=40,
            data_row_max_height=50,
            sort_column_index=0,
            sort_ascending=True,
        )

        self.content = ft.Column(
            [self.datatable],
            scroll=ft.ScrollMode.AUTO
        )

    def _on_sort(self, e):
        self.sort_column_index = e.column_index
        self.sort_ascending = e.ascending
        self.datatable.sort_column_index = self.sort_column_index
        self.datatable.sort_ascending = self.sort_ascending
        self.refresh_rows()

    def update_data(self, pods):
        self.pods = pods
        self.refresh_rows()

    def refresh_rows(self):
        if not self.pods:
            self.datatable.rows = []
            self.update()
            return

        # Helper to safely get values for sorting
        def get_sort_key(pod):
            # 0: Namespace
            # 1: Name
            # 2: Controller
            # 3: Status
            # 4: Age
            
            if self.sort_column_index == 0:
                return (pod.metadata.namespace or "", pod.metadata.name or "")
            elif self.sort_column_index == 1:
                return pod.metadata.name or ""
            elif self.sort_column_index == 2:
                controller = ""
                if pod.metadata.owner_references:
                     controller = pod.metadata.owner_references[0].name
                return controller
            elif self.sort_column_index == 3:
                return pod.status.phase or ""
            elif self.sort_column_index == 4:
                if pod.metadata.creation_timestamp:
                    return pod.metadata.creation_timestamp.timestamp()
                return 0
            return ""

        sorted_pods = sorted(self.pods, key=get_sort_key, reverse=not self.sort_ascending)
        
        # Secondary sort by name if first key is equal (stable sort property of python helps, but good to be explicit if needed)
        # Python sort is stable, so if we sort by name first then by column, it works. 
        # But here I'm using complex keys for specific needs.
        
        rows = []
        for pod in sorted_pods: # removed [:10] limit to show all pods as requested "muestre los pods todo el cluster"
            rows.append(self._build_row(pod))
            
        self.datatable.rows = rows
        self.update()

    def _build_row(self, pod):
        name = pod.metadata.name
        namespace = pod.metadata.namespace
        status = pod.status.phase
        
        # Controller
        controller = "N/A"
        if pod.metadata.owner_references:
            controller = pod.metadata.owner_references[0].name

        # Age
        age = "Unknown"
        age_sort_value = 0
        if pod.metadata.creation_timestamp:
            delta = datetime.datetime.now(datetime.timezone.utc) - pod.metadata.creation_timestamp
            if delta.days > 0:
                age = f"{delta.days}d"
            elif delta.seconds > 3600:
                age = f"{delta.seconds // 3600}h"
            else:
                age = f"{delta.seconds // 60}m"

        is_error = status not in ["Running", "Succeeded"]
        
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(namespace)),
                ft.DataCell(ft.Text(name)),
                ft.DataCell(ft.Text(controller)),
                ft.DataCell(ft.Text(status, color=ft.Colors.RED if is_error else ft.Colors.GREEN)),
                ft.DataCell(ft.Text(age)),
            ],
        )
