import flet as ft
from src.services.kube_service import kube_service

class NamespaceManager(ft.AlertDialog):
    def __init__(self, page: ft.Page, on_update=None):
        self.page_ref = page
        self.on_update = on_update
        
        self.new_namespace_field = ft.TextField(
            label="New Namespace Name",
            width=300,
            height=40,
            text_size=12,
            content_padding=10
        )
        
        self.namespace_list = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            height=300,
            spacing=5
        )
        
        super().__init__(
            title=ft.Text("Manage Namespaces"),
            content=ft.Container(
                width=400,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                self.new_namespace_field,
                                ft.IconButton(
                                    icon=ft.Icons.ADD,
                                    on_click=self.add_namespace,
                                    tooltip="Add Namespace"
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Divider(),
                        self.namespace_list
                    ]
                )
            ),
            actions=[
                ft.TextButton("Close", on_click=self.close_dialog)
            ],
        )
        self.refresh_list(update=False)

    def refresh_list(self, update=True):
        namespaces = kube_service.get_namespaces()
        self.namespace_list.controls = []
        
        for ns in namespaces:
            self.namespace_list.controls.append(
                ft.Row(
                    [
                        ft.Text(ns),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.ERROR,
                            tooltip="Delete Namespace",
                            on_click=lambda e, name=ns: self.delete_namespace(name),
                            disabled=(ns == "default" or ns == "kube-system" or ns == "kube-public" or ns == "kube-node-lease") # Prevent deleting system namespaces
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
        if update:
            self.page_ref.update()

    def add_namespace(self, e):
        name = self.new_namespace_field.value
        if not name:
            return
            
        if kube_service.create_namespace(name):
            self.new_namespace_field.value = ""
            self.refresh_list(update=True)
            if self.on_update:
                self.on_update()
        else:
            self.page_ref.show_snack_bar(ft.SnackBar(content=ft.Text(f"Failed to create namespace {name}")))

    def delete_namespace(self, name):
        if kube_service.delete_namespace(name):
            self.refresh_list(update=True)
            if self.on_update:
                self.on_update()
        else:
             self.page_ref.show_snack_bar(ft.SnackBar(content=ft.Text(f"Failed to delete namespace {name}")))

    def close_dialog(self, e):
        self.open = False
        self.page_ref.update()
