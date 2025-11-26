import flet as ft
from src.services.kube_service import kube_service

class YamlTab(ft.Container):
    def __init__(self, resource_type, resource_name, namespace):
        super().__init__()
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.namespace = namespace
        self.padding = 10
        
        self.yaml_view = ft.Markdown(
            "",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme="atom-one-dark",
        )
        
        self.content = ft.Column(
            [
                ft.Container(
                    content=self.yaml_view,
                    bgcolor=ft.Colors.BLACK,
                    padding=10,
                    border_radius=5,
                    expand=True, # Allow scrolling
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        self._load_yaml()

    def _load_yaml(self):
        obj = None
        if self.resource_type == "deployment":
            obj = kube_service.get_deployment(self.resource_name, self.namespace)
        elif self.resource_type == "cronjob":
            obj = kube_service.get_cronjob(self.resource_name, self.namespace)
            
        if obj:
            yaml_str = kube_service.get_resource_yaml(obj)
            self.yaml_view.value = f"```yaml\n{yaml_str}\n```"
        else:
            self.yaml_view.value = "**Error loading YAML**"
