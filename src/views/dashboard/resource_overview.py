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
                self._build_progress_row("CPU", 0.35, ft.Colors.BLUE),
                ft.Container(height=10),
                self._build_progress_row("Memory", 0.48, ft.Colors.GREEN),
                ft.Container(height=10),
                self._build_progress_row("Network IO", 0.15, ft.Colors.BLUE),
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

    def update_data(self, nodes, metrics_map):
        # Calculate Cluster Resource Usage
        # This is tricky without metrics server for nodes. 
        # We will approximate using Pod Metrics vs Node Allocatable if available, 
        # or just aggregate Pod Metrics and show a "Cluster Load" relative to some arbitrary capacity if node stats missing.
        
        # For now, let's just use the aggregated pod metrics we calculated in CpuUtilization (re-calculate here or pass it)
        # And compare against Node Capacity if we can get it.
        
        total_cpu_usage = 0
        total_mem_usage = 0
        
        total_cpu_capacity = 0
        total_mem_capacity = 0
        
        # Calculate Capacity from Nodes
        for node in nodes:
            # CPU: "8" or "8000m"
            cpu = node.status.capacity.get('cpu', '0')
            if cpu.endswith('m'):
                total_cpu_capacity += int(cpu[:-1])
            else:
                total_cpu_capacity += int(cpu) * 1000
                
            # Mem: "32930660Ki"
            mem = node.status.capacity.get('memory', '0')
            if mem.endswith('Ki'):
                total_mem_capacity += int(mem[:-2]) * 1024
            elif mem.endswith('Mi'):
                total_mem_capacity += int(mem[:-2]) * 1024 * 1024
            elif mem.endswith('Gi'):
                 total_mem_capacity += int(mem[:-2]) * 1024 * 1024 * 1024
            else:
                 try: total_mem_capacity += int(mem)
                 except: pass

        # Calculate Usage from Pod Metrics
        for pod_name, metrics in metrics_map.items():
            containers = metrics.get('containers', [])
            for c in containers:
                # CPU
                cpu_str = c['usage']['cpu']
                val = 0
                if cpu_str.endswith('n'): val = int(cpu_str[:-1]) / 1000000
                elif cpu_str.endswith('u'): val = int(cpu_str[:-1]) / 1000
                elif cpu_str.endswith('m'): val = int(cpu_str[:-1])
                else: 
                    try: val = int(cpu_str) * 1000
                    except: pass
                total_cpu_usage += val
                
                # Mem
                mem_str = c['usage']['memory']
                val_mem = 0
                if mem_str.endswith('Ki'): val_mem = int(mem_str[:-2]) * 1024
                elif mem_str.endswith('Mi'): val_mem = int(mem_str[:-2]) * 1024 * 1024
                elif mem_str.endswith('Gi'): val_mem = int(mem_str[:-2]) * 1024 * 1024 * 1024
                else:
                    try: val_mem = int(mem_str)
                    except: pass
                total_mem_usage += val_mem

        cpu_percent = (total_cpu_usage / total_cpu_capacity) if total_cpu_capacity > 0 else 0
        mem_percent = (total_mem_usage / total_mem_capacity) if total_mem_capacity > 0 else 0
        
        # Update Bars
        # CPU
        self.content.controls[2].controls[1].value = min(cpu_percent, 1.0)
        self.content.controls[2].controls[2].value = f"{int(cpu_percent*100)}%"
        
        # Memory
        self.content.controls[4].controls[1].value = min(mem_percent, 1.0)
        self.content.controls[4].controls[2].value = f"{int(mem_percent*100)}%"
        
        self.update()
