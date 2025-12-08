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
            title_size = 24 if self.filter_type == "deployments" else 18
            weight = ft.FontWeight.BOLD if self.filter_type == "deployments" else ft.FontWeight.W_600
            
            controls.append(
                ft.Row(
                    [
                        ft.Text("Deployments", size=title_size, weight=weight),
                        ft.ElevatedButton(
                            "Add", 
                            icon=ft.Icons.ADD,
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.PRIMARY,
                            ),
                            on_click=lambda _: self._open_deployment_dialog()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
            controls.append(ft.Divider())
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
            child_aspect_ratio=1.3,
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
            child_aspect_ratio=1.7,
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
        
        pod_icons = []
        for pod in pods:
            pod_name = pod.metadata.name
            pod_status = pod.status.phase
            
            icon_color = ft.Colors.RED
            if pod_status in ["Running", "Succeeded"]:
                icon_color = ft.Colors.GREEN
            elif pod_status == "Pending":
                icon_color = ft.Colors.YELLOW
            
            pod_icons.append(
                ft.Icon(
                    ft.Icons.CIRCLE, 
                    size=12, 
                    color=icon_color, 
                    tooltip=f"{pod_name}: {pod_status}"
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
                        ft.Container(height=5),
                        ft.Text("Pods Status", size=12, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            pod_icons,
                            wrap=True,
                            spacing=5,
                            run_spacing=5
                        ),
                        ft.Container(expand=True),
                        ft.Divider(height=10, thickness=1),
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.LINEAR_SCALE,
                                    tooltip="Scale",
                                    icon_color=ft.Colors.BLUE_200,
                                    on_click=lambda _: self._open_scale_dialog(name, replicas)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.RESTART_ALT,
                                    tooltip="Restart",
                                    icon_color=ft.Colors.ORANGE_300,
                                    on_click=lambda _: self._restart_deployment(name)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    tooltip="Edit",
                                    icon_color=ft.Colors.BLUE_GREY_300,
                                    on_click=lambda _: self._open_deployment_dialog(deployment)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    tooltip="Delete",
                                    icon_color=ft.Colors.RED_300,
                                    on_click=lambda _: self._confirm_delete_deployment(name)
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_EVENLY
                        )
                    ],
                ),
                padding=15,
                on_click=lambda e: self._on_card_click("deployment", name),
                border_radius=10,
            ),
            elevation=3,
        )

    def _open_scale_dialog(self, name, current_replicas):
        def close_dlg(e):
             if hasattr(self.page, "close"):
                 self.page.close(dlg)
             else:
                 self.page.dialog.open = False
                 self.page.update()

        def save_scale(e):
            if not scale_tf.value.isdigit():
                scale_tf.error_text = "Must be a number"
                scale_tf.update()
                return
            
            success, msg = kube_service.scale_deployment(name, int(scale_tf.value))
            success, msg = kube_service.scale_deployment(name, int(scale_tf.value))
            if hasattr(self.page, "close"):
                 self.page.close(dlg)
            else:
                 self.page.dialog.open = False
                 self.page.update()
            
            self.page.snack_bar = ft.SnackBar(ft.Text(msg))
            self.page.snack_bar.open = True
            self.page.update()

        scale_tf = ft.TextField(label="Replicas", value=str(current_replicas), keyboard_type=ft.KeyboardType.NUMBER)
        
        dlg = ft.AlertDialog(
            title=ft.Text(f"Scale {name}"),
            content=scale_tf,
            actions=[
                ft.TextButton("Cancel", on_click=close_dlg),
                ft.TextButton("Scale", on_click=save_scale),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        dlg = ft.AlertDialog(
            title=ft.Text(f"Scale {name}"),
            content=scale_tf,
            actions=[
                ft.TextButton("Cancel", on_click=close_dlg),
                ft.TextButton("Scale", on_click=save_scale),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        if hasattr(self.page, "open"):
             self.page.open(dlg)
        else:
             self.page.dialog = dlg
             dlg.open = True
             self.page.update()

    def _restart_deployment(self, name):
         success, msg = kube_service.restart_deployment(name)
         self.page.snack_bar = ft.SnackBar(ft.Text(msg))
         self.page.snack_bar.open = True
         self.page.update()

    def _confirm_delete_deployment(self, name):
        def close_dlg(e):
             if hasattr(self.page, "close"):
                 self.page.close(dlg)
             else:
                 self.page.dialog.open = False
                 self.page.update()

        def confirm_delete(e):
            success, msg = kube_service.delete_deployment(name)
        def confirm_delete(e):
            success, msg = kube_service.delete_deployment(name)
            if hasattr(self.page, "close"):
                 self.page.close(dlg)
            else:
                 self.page.dialog.open = False
                 self.page.update()
            
            self.page.snack_bar = ft.SnackBar(ft.Text(msg))
            self.page.snack_bar.open = True
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete deployment '{name}'?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dlg),
                ft.TextButton("Delete", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dlg
        if hasattr(self.page, "open"):
             self.page.open(dlg)
        else:
             dlg.open = True
             self.page.update()

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
        
        pod_icons = []
        for pod in pods:
            pod_name = pod.metadata.name
            pod_status = pod.status.phase
            
            icon_color = ft.Colors.RED
            if pod_status in ["Running", "Succeeded"]:
                icon_color = ft.Colors.GREEN
            elif pod_status == "Pending":
                icon_color = ft.Colors.YELLOW
            
            pod_icons.append(
                ft.Icon(
                    ft.Icons.CIRCLE, 
                    size=12, 
                    color=icon_color, 
                    tooltip=f"{pod_name}: {pod_status}"
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
                        ft.Container(height=5),
                        ft.Text("Pods Status", size=12, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            pod_icons,
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

    def _open_deployment_dialog(self, deployment=None):
        print(f"DEBUG: _open_deployment_dialog called. Deployment: {deployment}")
        try:
            if not self.page:
                print("ERROR: self.page is None!")
                return
            
            is_edit = deployment is not None
            title = f"Edit Deployment: {deployment.metadata.name}" if is_edit else "Create New Deployment"
            
            # Form Fields
            name_tf = ft.TextField(label="Name", value=deployment.metadata.name if is_edit else "", read_only=is_edit)
            image_tf = ft.TextField(label="Image", value=deployment.spec.template.spec.containers[0].image if is_edit else "")
            replicas_tf = ft.TextField(label="Replicas", value=str(deployment.spec.replicas) if is_edit else "1", keyboard_type=ft.KeyboardType.NUMBER)
            
            # Selector (Simple label for now, e.g., app=my-app)
            default_selector = ""
            if is_edit and deployment.spec.selector.match_labels:
                k, v = list(deployment.spec.selector.match_labels.items())[0]
                default_selector = f"{k}={v}"
            selector_tf = ft.TextField(label="Selector (key=value)", value=default_selector)

            # Env Vars Management
            env_vars_col = ft.Column()
            
            def add_env_var_row(key="", val=""):
                key_tf = ft.TextField(label="Key", value=key, expand=True, height=40, text_size=12)
                val_tf = ft.TextField(label="Value", value=val, expand=True, height=40, text_size=12)
                row = ft.Row([key_tf, val_tf, ft.IconButton(ft.Icons.DELETE, on_click=lambda e: remove_env_var_row(row))])
                env_vars_col.controls.append(row)
                env_vars_col.update()

            def remove_env_var_row(row):
                env_vars_col.controls.remove(row)
                env_vars_col.update()

            # Pre-fill env vars if editing
            if is_edit and deployment.spec.template.spec.containers[0].env:
                for env in deployment.spec.template.spec.containers[0].env:
                     # Only handle simple key-value env vars for now
                     if env.value is not None:
                        add_env_var_row(env.name, env.value)

            def save_deployment(e):
                 # Collect data
                 name = name_tf.value
                 image = image_tf.value
                 replicas = replicas_tf.value
                 selector = selector_tf.value
                 
                 # Collect Env Vars
                 env_vars = {}
                 for row in env_vars_col.controls:
                     k = row.controls[0].value
                     v = row.controls[1].value
                     if k: env_vars[k] = v

                 if not name or not image or not replicas or not selector:
                     self.page.snack_bar = ft.SnackBar(ft.Text("Please fill all required fields"))
                     self.page.snack_bar.open = True
                     self.page.update()
                     return

                 if is_edit:
                     success, msg = kube_service.update_deployment(name, image, env_vars)
                 else:
                     success, msg = kube_service.create_deployment(name, image, replicas, selector, env_vars)
                 
                 if is_edit:
                     success, msg = kube_service.update_deployment(name, image, env_vars)
                 else:
                     success, msg = kube_service.create_deployment(name, image, replicas, selector, env_vars)
                 
                 if hasattr(self.page, "close"):
                     self.page.close(dlg)
                 else:
                     self.page.dialog.open = False
                     self.page.update()
                 self.page.update()
                 self.page.snack_bar = ft.SnackBar(ft.Text(msg))
                 self.page.snack_bar.open = True
                 self.page.update()

            def close_dlg(e):
                 if hasattr(self.page, "close"):
                     self.page.close(dlg)
                 else:
                     self.page.dialog.open = False
                     self.page.update()

            dlg = ft.AlertDialog(
                title=ft.Text(title),
                content=ft.Container(
                    content=ft.Column(
                        [
                            name_tf,
                            image_tf,
                            ft.Row([replicas_tf, selector_tf]),
                            ft.Divider(),
                            ft.Text("Environment Variables", weight=ft.FontWeight.BOLD),
                            env_vars_col,
                            ft.ElevatedButton("Add Env Var", on_click=lambda _: add_env_var_row())
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        height=400,
                        width=600
                    ),
                    padding=10
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=close_dlg),
                    ft.TextButton("Save", on_click=save_deployment),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            print("DEBUG: Dialog object created.")
            
            if hasattr(self.page, "open"):
                print("DEBUG: Using page.open(dlg)")
                self.page.open(dlg)
            else:
                print("DEBUG: Using legacy page.dialog = dlg")
                self.page.dialog = dlg
                dlg.open = True
                self.page.update()
            
            print("DEBUG: Dialog open command sent.")
        except Exception as e:
            print(f"Error opening dialog: {e}")
            import traceback
            traceback.print_exc()
            if self.page:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {e}"))
                self.page.snack_bar.open = True
                self.page.update()

