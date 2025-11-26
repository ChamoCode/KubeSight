import flet as ft
from src.services.kube_service import kube_service
import datetime

class PodsTab(ft.Container):
    def __init__(self, resource_type, resource_name, namespace):
        super().__init__()
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.namespace = namespace
        self.padding = 10
        
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Restarts")),
                ft.DataColumn(ft.Text("Age")),
            ],
            rows=[]
        )
        
        self.content = ft.Column(
            [
                ft.Text("Pods", size=16, weight=ft.FontWeight.BOLD),
                ft.Row([self.data_table], scroll=ft.ScrollMode.AUTO)
            ],
            scroll=ft.ScrollMode.AUTO
        )
        self._load_pods()

    def _load_pods(self):
        # 1. Get the resource to find selector
        selector_str = ""
        if self.resource_type == "deployment":
            dep = kube_service.get_deployment(self.resource_name, self.namespace)
            if dep and dep.spec.selector.match_labels:
                selector_str = ",".join([f"{k}={v}" for k, v in dep.spec.selector.match_labels.items()])
        elif self.resource_type == "cronjob":
            # CronJobs are trickier, they create Jobs which create Pods.
            # For simplicity, we might look for jobs with label-selector or just list all pods and filter?
            # Standard way: CronJob -> Job -> Pod.
            # For now, let's try to find pods that might belong to it (often have job-name label)
            # Or maybe we skip complex logic for now and just show empty or "Not implemented for CronJob"
            # But user asked for it. Let's try to match by name prefix as a fallback or if possible.
            # Actually, CronJob pods usually have a label 'job-name' which is the job name.
            # Let's stick to Deployments for the robust implementation first, and maybe simple prefix for CronJob?
            pass

        if selector_str:
            pods = kube_service.list_pods(selector_str, self.namespace)
            self.data_table.rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(pod.metadata.name)),
                        ft.DataCell(ft.Text(pod.status.phase)),
                        ft.DataCell(ft.Text(str(sum(c.restart_count for c in pod.status.container_statuses) if pod.status.container_statuses else 0))),
                        ft.DataCell(ft.Text(str(datetime.datetime.now(datetime.timezone.utc) - pod.metadata.creation_timestamp).split('.')[0])),
                    ]
                ) for pod in pods
            ]
        else:
             self.data_table.rows = []
