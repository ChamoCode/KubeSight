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
                ft.ResponsiveRow(
                    [
                        ft.Container(content=ft.Text("Overview", size=24, weight=ft.FontWeight.BOLD), col=12),
                        ft.Container(content=ft.Divider(), col=12),
                        
                        # Row 1
                        self._create_dashboard_item(self.cluster_status, col_span_lg=3, col_span_sm=12),
                        self._create_dashboard_item(self.resource_overview, col_span_lg=3, col_span_sm=12),
                        self._create_dashboard_item(self.cpu_memory_utilization, col_span_lg=6, col_span_sm=12),
                        
                        # Row 2
                        self._create_dashboard_item(self.alerts, col_span_lg=12, col_span_sm=12),
                        
                        # Pod List (Full width)
                        ft.Container(
                            content=self.pod_list,
                            col={"xs": 12, "sm": 12, "md": 12, "lg": 12, "xl": 12},
                            padding=10,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            border_radius=10,
                        ),
                    ],
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
        )

    def _create_dashboard_item(self, content, col_span_lg=3, col_span_sm=6):
        CARD_HEIGHT = 300
        return ft.Container(
            content=content,
            col={"xs": 12, "sm": col_span_sm, "md": col_span_sm, "lg": col_span_sm, "xl": col_span_lg, "xxl": col_span_lg},
            height=CARD_HEIGHT,
            padding=10,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=10,
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
        # Check connection first
        if not kube_service.check_connection():
            self.clean()
            self.content = ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(name=ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED, size=50),
                                ft.Text("Cannot connect to cluster", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                                ft.Text("Please check your configuration.", size=14)
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        alignment=ft.alignment.center,
                        expand=True
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )
            self.update()
            return

        # Restore dashboard layout if it was showing error
        if len(self.content.controls) == 1 and isinstance(self.content.controls[0], ft.Container) and isinstance(self.content.controls[0].content, ft.Column) and len(self.content.controls[0].content.controls) == 3:
             self.content = ft.Column(
                [
                    ft.ResponsiveRow(
                        [
                            ft.Container(content=ft.Text("Overview", size=24, weight=ft.FontWeight.BOLD), col=12),
                            ft.Container(content=ft.Divider(), col=12),
                            
                            # Row 1
                            self._create_dashboard_item(self.cluster_status, col_span_lg=3, col_span_sm=12),
                            self._create_dashboard_item(self.resource_overview, col_span_lg=3, col_span_sm=12),
                            self._create_dashboard_item(self.cpu_memory_utilization, col_span_lg=6, col_span_sm=12),
                            
                            # Row 2
                            self._create_dashboard_item(self.alerts, col_span_lg=12, col_span_sm=12),
                            
                            # Pod List (Full width)
                            ft.Container(
                                content=self.pod_list,
                                col={"xs": 12, "sm": 12, "md": 12, "lg": 12, "xl": 12},
                                padding=10,
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                border_radius=10,
                            ),
                        ],
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH
            )

        # Fetch data
        nodes = kube_service.list_nodes()
        current_pods = kube_service.list_pods("") # Pods in current namespace
        all_pods = kube_service.list_pods("", namespace="all") # All pods in cluster
        events = kube_service.list_events()
        metrics_map = kube_service.get_pod_metrics(namespace="all")
        node_metrics = kube_service.get_node_metrics()

        # Update components
        if hasattr(self.cluster_status, 'update_data'):
            self.cluster_status.update_data(nodes, all_pods)
        
        if hasattr(self.cpu_memory_utilization, 'update_data'):
             self.cpu_memory_utilization.update_data(metrics_map)

        if hasattr(self.resource_overview, 'update_data'):
            self.resource_overview.update_data(nodes, node_metrics, all_pods)

        if hasattr(self.alerts, 'update_data'):
            self.alerts.update_data(events)

        # Only update pod list if it's actually in the view (mounted)
        if hasattr(self.pod_list, 'update_data') and self.pod_list.page:
            self.pod_list.update_data(all_pods)
        
        self.update()
