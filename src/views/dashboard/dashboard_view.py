import flet as ft
import threading
import time
from src.services.kube_service import kube_service
from .cluster_status import ClusterStatus
from .cpu_memory_utilization import CpuMemoryUtilization
from .resource_overview import ResourceOverview
from .alerts import Alerts
from .pod_list import PodList

class DashboardView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 20
        self.running = False
        
        self.cluster_status = ClusterStatus()
        self.cpu_memory_utilization = CpuMemoryUtilization()
        self.resource_overview = ResourceOverview()
        self.alerts = Alerts()
        self.pod_list = PodList()

        self.content = ft.Column(
            [
                ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row(
                    [
                        ft.Container(content=self.cluster_status, expand=1),
                        ft.Container(content=self.resource_overview, expand=1),
                        ft.Container(content=self.cpu_memory_utilization, expand=2),
                    ],
                    spacing=20,
                ),
                ft.Container(height=10),
                ft.Row(
                    [
                        ft.Container(content=self.alerts, expand=1),
                    ],
                    spacing=20,
                ),
                ft.Container(height=10),
                self.pod_list,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    def did_mount(self):
        self.running = True
        self.refresh_thread = threading.Thread(target=self._auto_refresh_loop, daemon=True)
        self.refresh_thread.start()

    def will_unmount(self):
        self.running = False

    def _auto_refresh_loop(self):
        while self.running:
            try:
                self._fetch_and_update_data()
            except Exception as e:
                print(f"Error in dashboard auto-refresh: {e}")
            
            # Wait for 5 seconds
            for _ in range(50):
                if not self.running: break
                time.sleep(0.1)

    def _fetch_and_update_data(self):
        # Fetch data
        nodes = kube_service.list_nodes()
        pods = kube_service.list_pods("") # All pods in namespace
        events = kube_service.list_events()
        metrics_map = kube_service.get_pod_metrics(namespace="all")

        # Update components
        if hasattr(self.cluster_status, 'update_data'):
            self.cluster_status.update_data(nodes, pods)
        
        if hasattr(self.cpu_memory_utilization, 'update_data'):
             self.cpu_memory_utilization.update_data(metrics_map)

        if hasattr(self.resource_overview, 'update_data'):
            self.resource_overview.update_data(nodes, metrics_map)

        if hasattr(self.alerts, 'update_data'):
            self.alerts.update_data(events)

        if hasattr(self.pod_list, 'update_data'):
            self.pod_list.update_data(pods)
        
        self.update()
