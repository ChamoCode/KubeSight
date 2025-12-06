import flet as ft
from src.services.kube_service import kube_service

class ContextManager(ft.AlertDialog):
    def __init__(self, page: ft.Page, on_update=None):
        self.page_ref = page
        self.on_update = on_update
        
        self.name_field = ft.TextField(label="Context Name", width=300)
        self.server_field = ft.TextField(label="Server URL (e.g. https://1.2.3.4:6443)", width=300)
        self.token_field = ft.TextField(label="Token", width=300, password=True, can_reveal_password=True)
        self.insecure_checkbox = ft.Checkbox(label="Skip TLS Verify (Insecure)")
        
        self.context_list = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            height=200,
            spacing=5
        )
        
        super().__init__(
            title=ft.Text("Manage Contexts"),
            content=ft.Container(
                width=450,
                content=ft.Column(
                    [
                        ft.Text("Add New Context", weight=ft.FontWeight.BOLD),
                        self.name_field,
                        self.server_field,
                        self.token_field,
                        self.insecure_checkbox,
                        ft.ElevatedButton("Add Context", on_click=self.add_context),
                        ft.Divider(),
                        ft.Text("Custom Contexts", weight=ft.FontWeight.BOLD),
                        self.context_list
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO
                )
            ),
            actions=[
                ft.TextButton("Close", on_click=self.close_dialog)
            ],
        )
        self.refresh_list(update=False)

    def refresh_list(self, update=True):
        self.context_list.controls = []
        
        # Filter for custom contexts only
        custom_contexts = [ctx for ctx in kube_service.contexts if ctx.get('is_custom')]
        
        if not custom_contexts:
            self.context_list.controls.append(ft.Text("No custom contexts found", italic=True))
        
        for ctx in custom_contexts:
            name = ctx['name']
            self.context_list.controls.append(
                ft.Row(
                    [
                        ft.Text(name),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.ERROR,
                            tooltip="Delete Context",
                            on_click=lambda e, n=name: self.delete_context(n)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
        if update:
            self.page_ref.update()

    def add_context(self, e):
        name = self.name_field.value
        server = self.server_field.value
        token = self.token_field.value
        
        if not all([name, server, token]):
            self.page_ref.show_snack_bar(ft.SnackBar(content=ft.Text("Please fill all fields")))
            return
            
        success, message = kube_service.add_custom_context(
            name, server, token, self.insecure_checkbox.value
        )
        
        if success:
            self.name_field.value = ""
            self.server_field.value = ""
            self.token_field.value = ""
            self.insecure_checkbox.value = False
            self.refresh_list(update=True)
            if self.on_update:
                self.on_update()
            self.page_ref.show_snack_bar(ft.SnackBar(content=ft.Text(message)))
        else:
            self.page_ref.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error: {message}")))

    def delete_context(self, name):
        success, message = kube_service.delete_custom_context(name)
        if success:
            self.refresh_list(update=True)
            if self.on_update:
                self.on_update()
            self.page_ref.show_snack_bar(ft.SnackBar(content=ft.Text(message)))
        else:
            self.page_ref.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error: {message}")))

    def close_dialog(self, e):
        self.open = False
        self.page_ref.update()
