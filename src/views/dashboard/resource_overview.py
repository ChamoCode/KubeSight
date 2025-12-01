import flet as ft

class ResourceOverview(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 20
import flet as ft

class ResourceOverview(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 20
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.border_radius = 10
        self.content = ft.Column(
            [
                ft.Text("Resource Overview", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                self._build_progress_row("CPU", 0.0, ft.Colors.BLUE),
                ft.Container(height=10),
                self._build_progress_row("Memory", 0.0, ft.Colors.GREEN),
                ft.Container(height=10),
                self._build_progress_row("Pods", 0.0, ft.Colors.ORANGE),
                ft.Container(height=10),
                self._build_progress_row("Storage", 0.0, ft.Colors.PURPLE),
            ]
        )

    def _build_progress_row(self, label, value, color):
        return ft.Row(
            [
                ft.Text(label, width=80),
                ft.ProgressBar(value=value, color=color, bgcolor=ft.Colors.with_opacity(0.1, color), expand=True),
                ft.Text(f"{int(value*100)}%", width=40, text_align=ft.TextAlign.RIGHT, color=color),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def update_data(self, nodes, node_metrics, all_pods):
        # Calculate Cluster Resource Usage using Node Metrics
        
        total_cpu_usage = 0
        total_mem_usage = 0
        total_storage_usage = 0
        
        total_cpu_capacity = 0
        total_mem_capacity = 0
        total_pods_capacity = 0
        total_storage_capacity = 0
        
        # Calculate Capacity from Nodes
        for node in nodes:
            # CPU
            cpu = node.status.capacity.get('cpu', '0')
            if cpu.endswith('m'): total_cpu_capacity += int(cpu[:-1])
            else: total_cpu_capacity += int(cpu) * 1000
                
            # Mem
            mem = node.status.capacity.get('memory', '0')
            if mem.endswith('Ki'): total_mem_capacity += int(mem[:-2]) * 1024
            elif mem.endswith('Mi'): total_mem_capacity += int(mem[:-2]) * 1024 * 1024
            elif mem.endswith('Gi'): total_mem_capacity += int(mem[:-2]) * 1024 * 1024 * 1024
            else:
                 try: total_mem_capacity += int(mem)
                 except: pass
            
            # Pods
            pods = node.status.capacity.get('pods', '0')
            try: total_pods_capacity += int(pods)
            except: pass

            # Ephemeral Storage
            storage = node.status.capacity.get('ephemeral-storage', '0')
            if storage.endswith('Ki'): total_storage_capacity += int(storage[:-2]) * 1024
            elif storage.endswith('Mi'): total_storage_capacity += int(storage[:-2]) * 1024 * 1024
            elif storage.endswith('Gi'): total_storage_capacity += int(storage[:-2]) * 1024 * 1024 * 1024
            else:
                 try: total_storage_capacity += int(storage)
                 except: pass

        # Calculate Usage from Node Metrics
        for node_name, metrics in node_metrics.items():
            usage = metrics.get('usage', {})
            
            # CPU
            cpu_str = usage.get('cpu', '0')
            val = 0
            if cpu_str.endswith('n'): val = int(cpu_str[:-1]) / 1000000
            elif cpu_str.endswith('u'): val = int(cpu_str[:-1]) / 1000
            elif cpu_str.endswith('m'): val = int(cpu_str[:-1])
            else: 
                try: val = int(cpu_str) * 1000
                except: pass
            total_cpu_usage += val
            
            # Mem
            mem_str = usage.get('memory', '0')
            val_mem = 0
            if mem_str.endswith('Ki'): val_mem = int(mem_str[:-2]) * 1024
            elif mem_str.endswith('Mi'): val_mem = int(mem_str[:-2]) * 1024 * 1024
            elif mem_str.endswith('Gi'): val_mem = int(mem_str[:-2]) * 1024 * 1024 * 1024
            else:
                try: val_mem = int(mem_str)
                except: pass
            total_mem_usage += val_mem

            # Storage (if available in metrics, usually not in standard kubectl top node, but let's check)
            # Standard metrics.k8s.io usually doesn't provide ephemeral-storage usage for nodes directly in the same way.
            # However, if it's there, it would be 'ephemeral-storage'. 
            # If not, we might default to 0 or try to sum pod usage if we had it.
            # Let's try to read it from node metrics if present.
            storage_str = usage.get('ephemeral-storage', '0')
            val_storage = 0
            if storage_str.endswith('Ki'): val_storage = int(storage_str[:-2]) * 1024
            elif storage_str.endswith('Mi'): val_storage = int(storage_str[:-2]) * 1024 * 1024
            elif storage_str.endswith('Gi'): val_storage = int(storage_str[:-2]) * 1024 * 1024 * 1024
            else:
                try: val_storage = int(storage_str)
                except: pass
            total_storage_usage += val_storage

        # Pod Usage
        total_pods_usage = len(all_pods)

        cpu_percent = (total_cpu_usage / total_cpu_capacity) if total_cpu_capacity > 0 else 0
        mem_percent = (total_mem_usage / total_mem_capacity) if total_mem_capacity > 0 else 0
        pods_percent = (total_pods_usage / total_pods_capacity) if total_pods_capacity > 0 else 0
        storage_percent = (total_storage_usage / total_storage_capacity) if total_storage_capacity > 0 else 0
        
        # Update Bars
        # CPU
        self.content.controls[2].controls[1].value = min(cpu_percent, 1.0)
        self.content.controls[2].controls[2].value = f"{int(cpu_percent*100)}%"
        
        # Memory
        self.content.controls[4].controls[1].value = min(mem_percent, 1.0)
        self.content.controls[4].controls[2].value = f"{int(mem_percent*100)}%"
        
        # Pods
        self.content.controls[6].controls[1].value = min(pods_percent, 1.0)
        self.content.controls[6].controls[2].value = f"{int(pods_percent*100)}%"

        # Storage
        self.content.controls[8].controls[1].value = min(storage_percent, 1.0)
        self.content.controls[8].controls[2].value = f"{int(storage_percent*100)}%"
        
        # Network IO - Not available in standard metrics
        # self.content.controls[6].controls[1].value = 0
        # self.content.controls[6].controls[2].value = "N/A"
        
        self.update()
