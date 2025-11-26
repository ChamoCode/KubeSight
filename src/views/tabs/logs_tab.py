import flet as ft
from src.services.kube_service import kube_service

class LogsTab(ft.Container):
    def __init__(self, resource_type, resource_name, namespace):
        super().__init__()
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.namespace = namespace
        self.padding = 10
        
        self.pod_selector = ft.Dropdown(
            label="Select Pod",
            options=[],
            on_change=self.on_pod_change,
            width=300
        )
        
        self.logs_view = ft.Markdown(
            "",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme="atom-one-dark",
        )
        
        self.content = ft.Column(
            [
                self.pod_selector,
                ft.Container(
                    content=self.logs_view,
                    bgcolor=ft.Colors.BLACK,
                    padding=10,
                    border_radius=5,
                    expand=True,
                )
            ],
            expand=True
        )
        self._load_pods()

    def _load_pods(self):
        selector_str = ""
        if self.resource_type == "deployment":
            dep = kube_service.get_deployment(self.resource_name, self.namespace)
            if dep and dep.spec.selector.match_labels:
                selector_str = ",".join([f"{k}={v}" for k, v in dep.spec.selector.match_labels.items()])
        
        if selector_str:
            pods = kube_service.list_pods(selector_str, self.namespace)
            self.pod_selector.options = [ft.dropdown.Option(pod.metadata.name) for pod in pods]
            if pods:
                self.pod_selector.value = pods[0].metadata.name
                self._load_logs(pods[0].metadata.name)

    def on_pod_change(self, e):
        self._load_logs(self.pod_selector.value)
        self.update()

    def _load_logs(self, pod_name):
        logs = kube_service.get_pod_logs(pod_name, self.namespace)
        self.logs_view.value = f"```log\n{logs}\n```"
