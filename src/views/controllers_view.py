import flet as ft
from src.services.kube_service import kube_service
import datetime

import threading
import time

class ControllersView(ft.Container):
    def __init__(self, filter_type="all"):
        super().__init__()
        self.expand = True
        self.padding = 20
        self.running = False
        self.filter_type = filter_type
        
        self.deployments_container = ft.Container()
        self.cronjobs_container = ft.Container()
        self.statefulsets_container = ft.Container()
        
        controls = []
        if self.filter_type == "all":
            controls.append(ft.Text("Workloads", size=24, weight=ft.FontWeight.BOLD))
            controls.append(ft.Divider())
        
        if self.filter_type in ["all", "deployments"]:
            if self.filter_type == "deployments":
                 controls.append(ft.Text("Deployments", size=24, weight=ft.FontWeight.BOLD))
            else:
                 controls.append(ft.Text("Deployments", size=18, weight=ft.FontWeight.W_600))
            controls.append(self.deployments_container)
            if self.filter_type == "all": controls.append(ft.Divider())

        if self.filter_type in ["all", "statefulsets"]:
            if self.filter_type == "statefulsets":
                 controls.append(ft.Text("StatefulSets", size=24, weight=ft.FontWeight.BOLD))
            else:
                 controls.append(ft.Text("StatefulSets", size=18, weight=ft.FontWeight.W_600))
            controls.append(self.statefulsets_container)
            if self.filter_type == "all": controls.append(ft.Divider())

        if self.filter_type in ["all", "cronjobs"]:
            if self.filter_type == "cronjobs":
                 controls.append(ft.Text("CronJobs", size=24, weight=ft.FontWeight.BOLD))
            else:
                 controls.append(ft.Text("CronJobs", size=18, weight=ft.FontWeight.W_600))
            controls.append(self.cronjobs_container)

        self.content = ft.Column(
            controls,
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
                # Update deployments grid
                if self.filter_type in ["all", "deployments"]:
                    self.deployments_container.content = self._build_deployments_grid()
                    self.deployments_container.update()

                # Update statefulsets grid
                if self.filter_type in ["all", "statefulsets"]:
                    self.statefulsets_container.content = self._build_statefulsets_grid()
                    self.statefulsets_container.update()

                # Update cronjobs grid
                if self.filter_type in ["all", "cronjobs"]:
                    self.cronjobs_container.content = self._build_cronjobs_grid()
                    self.cronjobs_container.update()
                    
            except Exception as e:
                print(f"Error in auto-refresh: {e}")
            
            # Wait for 5 seconds
            for _ in range(50):
                if not self.running: break
                time.sleep(0.1)

    def _build_deployments_grid(self):
        deployments = kube_service.list_deployments()
        if not deployments:
            return ft.Text("No deployments found in this namespace.")
        
        # Fetch all metrics for the namespace once
        metrics_map = kube_service.get_pod_metrics()
        
        return ft.GridView(
            runs_count=3,
            max_extent=400,
            child_aspect_ratio=0.8, # Adjusted for taller cards with bigger pod cards
            spacing=10,
            run_spacing=10,
            controls=[
                self._build_deployment_card(d, metrics_map) for d in deployments
            ]
        )

    def _build_statefulsets_grid(self):
        statefulsets = kube_service.list_statefulsets()
        if not statefulsets:
            return ft.Text("No statefulsets found in this namespace.")
        
        # Fetch all metrics for the namespace once
        metrics_map = kube_service.get_pod_metrics()
        
        return ft.GridView(
            runs_count=3,
            max_extent=400,
            child_aspect_ratio=0.8,
            spacing=10,
            run_spacing=10,
            controls=[
                self._build_statefulset_card(s, metrics_map) for s in statefulsets
            ]
        )

    def _build_cronjobs_grid(self):
        cronjobs = kube_service.list_cronjobs()
        if not cronjobs:
            return ft.Text("No cronjobs found in this namespace.")

        return ft.GridView(
            runs_count=3,
            max_extent=400,
            child_aspect_ratio=1.5,
            spacing=10,
            run_spacing=10,
            controls=[
                self._build_cronjob_card(c) for c in cronjobs
            ]
        )

    def _build_deployment_card(self, deployment, metrics_map):
        name = deployment.metadata.name
        replicas = deployment.spec.replicas or 0
        available = deployment.status.available_replicas or 0
        
        # Status Color Logic
        if available == replicas:
            status_color = ft.Colors.GREEN
        elif available > (replicas * 0.5):
            status_color = ft.Colors.YELLOW
        else:
            status_color = ft.Colors.RED

        # Resources
        containers = deployment.spec.template.spec.containers
        cpu_req, cpu_lim, mem_req, mem_lim = self._calculate_resources(containers)

        # Fetch Pods for this deployment
        selector = deployment.spec.selector.match_labels
        pods = kube_service.list_pods(selector)
        
        pod_cards = []
        for pod in pods:
            pod_name = pod.metadata.name
            pod_status = pod.status.phase
            pod_metrics = metrics_map.get(pod_name)
            
            usage_cpu = "N/A"
            usage_mem = "N/A"
            
            if pod_metrics:
                p_containers = pod_metrics.get('containers', [])
                if p_containers:
                    usage_cpu = p_containers[0]['usage']['cpu']
                    usage_mem = p_containers[0]['usage']['memory']

            pod_cards.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(pod_name, size=12, weight=ft.FontWeight.BOLD, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1),
                            ft.Row(
                                [
                                    ft.Column([
                                        ft.Text("CPU", size=8, color=ft.Colors.OUTLINE),
                                        ft.Text(usage_cpu, size=10, weight=ft.FontWeight.BOLD)
                                    ]),
                                    ft.Column([
                                        ft.Text("MEM", size=8, color=ft.Colors.OUTLINE),
                                        ft.Text(usage_mem, size=10, weight=ft.FontWeight.BOLD)
                                    ]),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    padding=8,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    border_radius=8,
                    border=ft.border.all(2, ft.Colors.GREEN if pod_status == "Running" else ft.Colors.RED),
                    width=140,
                    height=60
                )
            )

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.APPS, size=24, color=ft.Colors.PRIMARY),
                                ft.Text(name, size=16, weight=ft.FontWeight.BOLD, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                                ft.Container(
                                    content=ft.Text(f"{available}/{replicas}", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=12),
                                    bgcolor=status_color,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=12
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Divider(height=10, thickness=1),
                        ft.Row(
                            [
                                self._build_resource_chip("CPU", f"{cpu_req or '-'}/{cpu_lim or '-'}", ft.Icons.SPEED),
                                self._build_resource_chip("Mem", f"{mem_req or '-'}/{mem_lim or '-'}", ft.Icons.MEMORY),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Container(height=10),
                        ft.Text("Pods", size=12, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            pod_cards,
                            wrap=True,
                            spacing=5,
                            run_spacing=5
                        )
                    ],
                ),
                padding=15,
                on_click=lambda e: self._on_card_click("deployment", name),
                border_radius=10,
            ),
            elevation=3,
        )

    def _build_statefulset_card(self, statefulset, metrics_map):
        name = statefulset.metadata.name
        replicas = statefulset.spec.replicas or 0
        available = statefulset.status.ready_replicas or 0 # StatefulSet uses ready_replicas
        
        # Status Color Logic
        if available == replicas:
            status_color = ft.Colors.GREEN
        elif available > (replicas * 0.5):
            status_color = ft.Colors.YELLOW
        else:
            status_color = ft.Colors.RED

        # Resources
        containers = statefulset.spec.template.spec.containers
        cpu_req, cpu_lim, mem_req, mem_lim = self._calculate_resources(containers)

        # Fetch Pods for this statefulset
        selector = statefulset.spec.selector.match_labels
        pods = kube_service.list_pods(selector)
        
        pod_cards = []
        for pod in pods:
            pod_name = pod.metadata.name
            pod_status = pod.status.phase
            pod_metrics = metrics_map.get(pod_name)
            
            usage_cpu = "N/A"
            usage_mem = "N/A"
            
            if pod_metrics:
                p_containers = pod_metrics.get('containers', [])
                if p_containers:
                    usage_cpu = p_containers[0]['usage']['cpu']
                    usage_mem = p_containers[0]['usage']['memory']

            pod_cards.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(pod_name, size=12, weight=ft.FontWeight.BOLD, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1),
                            ft.Row(
                                [
                                    ft.Column([
                                        ft.Text("CPU", size=8, color=ft.Colors.OUTLINE),
                                        ft.Text(usage_cpu, size=10, weight=ft.FontWeight.BOLD)
                                    ]),
                                    ft.Column([
                                        ft.Text("MEM", size=8, color=ft.Colors.OUTLINE),
                                        ft.Text(usage_mem, size=10, weight=ft.FontWeight.BOLD)
                                    ]),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    padding=8,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    border_radius=8,
                    border=ft.border.all(2, ft.Colors.GREEN if pod_status == "Running" else ft.Colors.RED),
                    width=140,
                    height=60
                )
            )

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.LAYERS, size=24, color=ft.Colors.PRIMARY), # Icon for StatefulSet
                                ft.Text(name, size=16, weight=ft.FontWeight.BOLD, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                                ft.Container(
                                    content=ft.Text(f"{available}/{replicas}", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=12),
                                    bgcolor=status_color,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=12
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Divider(height=10, thickness=1),
                        ft.Row(
                            [
                                self._build_resource_chip("CPU", f"{cpu_req or '-'}/{cpu_lim or '-'}", ft.Icons.SPEED),
                                self._build_resource_chip("Mem", f"{mem_req or '-'}/{mem_lim or '-'}", ft.Icons.MEMORY),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Container(height=10),
                        ft.Text("Pods", size=12, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            pod_cards,
                            wrap=True,
                            spacing=5,
                            run_spacing=5
                        )
                    ],
                ),
                padding=15,
                on_click=lambda e: self._on_card_click("statefulset", name),
                border_radius=10,
            ),
            elevation=3,
        )

    def _build_cronjob_card(self, cronjob):
        name = cronjob.metadata.name
        schedule = cronjob.spec.schedule
        suspend = cronjob.spec.suspend
        
        last_schedule = "Never"
        if cronjob.status.last_schedule_time:
             last_schedule = str(datetime.datetime.now(datetime.timezone.utc) - cronjob.status.last_schedule_time).split('.')[0] + " ago"

        # Resources (from Job Template)
        containers = cronjob.spec.job_template.spec.template.spec.containers
        cpu_req, cpu_lim, mem_req, mem_lim = self._calculate_resources(containers)

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.SCHEDULE, size=24, color=ft.Colors.PRIMARY),
                                ft.Text(name, size=16, weight=ft.FontWeight.BOLD, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                                ft.Icon(ft.Icons.PAUSE_CIRCLE if suspend else ft.Icons.PLAY_CIRCLE, 
                                        color=ft.Colors.GREY if suspend else ft.Colors.GREEN, size=20)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Divider(height=10, thickness=1),
                        ft.Text(f"Schedule: {schedule}", size=12),
                        ft.Text(f"Last Run: {last_schedule}", size=12),
                        ft.Container(height=5),
                        ft.Row(
                            [
                                self._build_resource_chip("CPU", f"{cpu_req or '-'}/{cpu_lim or '-'}", ft.Icons.SPEED),
                                self._build_resource_chip("Mem", f"{mem_req or '-'}/{mem_lim or '-'}", ft.Icons.MEMORY),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                    ],
                ),
                padding=15,
                on_click=lambda e: self._on_card_click("cronjob", name),
                border_radius=10,
            ),
            elevation=3,
        )

    def _build_resource_chip(self, label, value, icon):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=12, color=ft.Colors.OUTLINE),
                    ft.Text(f"{label}: {value}", size=10, weight=ft.FontWeight.BOLD),
                ],
                spacing=5,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=4
        )

    def _calculate_resources(self, containers):
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
        
        def join_vals(vals):
            return "+".join(set(vals)) if vals else None

        return join_vals(cpu_reqs), join_vals(cpu_lims), join_vals(mem_reqs), join_vals(mem_lims)

    def _on_card_click(self, resource_type, name):
        self.page.pubsub.send_all(("resource_selected", {
            "type": resource_type,
            "name": name,
            "namespace": kube_service.active_namespace
        }))
