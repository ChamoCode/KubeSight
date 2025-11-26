import flet as ft
from src.services.kube_service import kube_service
from src.views.tabs.pods_tab import PodsTab
from src.views.tabs.logs_tab import LogsTab
from src.views.tabs.yaml_tab import YamlTab
import datetime

class ResourceView(ft.Container):
    def __init__(self, resource_type, resource_name, namespace):
        super().__init__()
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.namespace = namespace
        self.expand = True
        
        # Fetch resource object for InfoBar
        self.resource_obj = self._fetch_resource()

        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Pods",
                    icon=ft.Icons.APPS,
                    content=PodsTab(resource_type, resource_name, namespace),
                ),
                ft.Tab(
                    text="Logs",
                    icon=ft.Icons.TERMINAL,
                    content=LogsTab(resource_type, resource_name, namespace),
                ),
                ft.Tab(
                    text="YAML",
                    icon=ft.Icons.CODE,
                    content=YamlTab(resource_type, resource_name, namespace),
                ),
            ],
            expand=True,
        )

        self.content = ft.Column(
            [
                self._build_header(),
                self._build_info_bar(),
                self.tabs
            ],
            expand=True,
            spacing=0
        )

    def _fetch_resource(self):
        if self.resource_type == "deployment":
            return kube_service.get_deployment(self.resource_name, self.namespace)
        elif self.resource_type == "cronjob":
            return kube_service.get_cronjob(self.resource_name, self.namespace)
        return None

    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.APPS if self.resource_type == "deployment" else ft.Icons.SCHEDULE, size=24),
                    ft.Text(f"{self.resource_type.capitalize()}: {self.resource_name}", size=20, weight=ft.FontWeight.BOLD),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=10,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST
        )

    def _build_info_bar(self):
        if not self.resource_obj:
            return ft.Container()

        info_items = []
        
        # Common: Age
        age = str(datetime.datetime.now(datetime.timezone.utc) - self.resource_obj.metadata.creation_timestamp).split('.')[0]
        info_items.append(self._build_info_chip("Age", age, ft.Icons.ACCESS_TIME))

        if self.resource_type == "deployment":
            # Replicas
            replicas = f"{self.resource_obj.status.available_replicas or 0}/{self.resource_obj.spec.replicas}"
            info_items.append(self._build_info_chip("Replicas", replicas, ft.Icons.COPY_ALL))
            
            # Strategy
            strategy = self.resource_obj.spec.strategy.type
            info_items.append(self._build_info_chip("Strategy", strategy, ft.Icons.SHUFFLE))
            
            # Images
            containers = self.resource_obj.spec.template.spec.containers
            images = [c.image.split(':')[-1] if ':' in c.image else c.image for c in containers] # Shorten image name
            info_items.append(self._build_info_chip("Images", ", ".join(images), ft.Icons.IMAGE))

        elif self.resource_type == "cronjob":
            # Schedule
            schedule = self.resource_obj.spec.schedule
            info_items.append(self._build_info_chip("Schedule", schedule, ft.Icons.SCHEDULE))
            
            # Suspend
            suspend = "Yes" if self.resource_obj.spec.suspend else "No"
            info_items.append(self._build_info_chip("Suspend", suspend, ft.Icons.PAUSE_CIRCLE))
            
            # Last Schedule
            last_schedule = "Never"
            if self.resource_obj.status.last_schedule_time:
                 last_schedule = str(datetime.datetime.now(datetime.timezone.utc) - self.resource_obj.status.last_schedule_time).split('.')[0] + " ago"
            info_items.append(self._build_info_chip("Last Run", last_schedule, ft.Icons.HISTORY))
            
            containers = self.resource_obj.spec.job_template.spec.template.spec.containers

        # Resources (CPU/Memory)
        cpu_req, cpu_lim, mem_req, mem_lim = self._calculate_resources(containers)
        
        if cpu_req or cpu_lim:
            val = f"{cpu_req or '-'} / {cpu_lim or '-'}"
            info_items.append(self._build_info_chip("CPU (Req/Lim)", val, ft.Icons.SPEED))
            
        if mem_req or mem_lim:
            val = f"{mem_req or '-'} / {mem_lim or '-'}"
            info_items.append(self._build_info_chip("Mem (Req/Lim)", val, ft.Icons.MEMORY))

        return ft.Container(
            content=ft.Row(info_items, wrap=True, spacing=10, run_spacing=10),
            padding=ft.padding.symmetric(horizontal=10, vertical=10),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        )

    def _calculate_resources(self, containers):
        # Simple string concatenation for now, or just taking the first if multiple
        # Real parsing is complex without a library
        cpu_reqs = []
        cpu_lims = []
        mem_reqs = []
        mem_lims = []
        
        for c in containers:
            resources = c.resources
            if resources:
                if resources.requests:
                    if 'cpu' in resources.requests: cpu_reqs.append(resources.requests['cpu'])
                    if 'memory' in resources.requests: mem_reqs.append(resources.requests['memory'])
                if resources.limits:
                    if 'cpu' in resources.limits: cpu_lims.append(resources.limits['cpu'])
                    if 'memory' in resources.limits: mem_lims.append(resources.limits['memory'])
        
        # Helper to join unique values
        def join_vals(vals):
            return "+".join(set(vals)) if vals else None

        return join_vals(cpu_reqs), join_vals(cpu_lims), join_vals(mem_reqs), join_vals(mem_lims)

    def _build_info_chip(self, label, value, icon):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=16, color=ft.Colors.PRIMARY),
                    ft.Column(
                        [
                            ft.Text(label, size=10, color=ft.Colors.OUTLINE),
                            ft.Text(value, size=12, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=0
                    )
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5
            ),
            padding=ft.padding.all(8),
            bgcolor=ft.Colors.SURFACE,
            border_radius=8,
        )
