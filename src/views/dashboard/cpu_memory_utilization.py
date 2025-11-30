import flet as ft
import datetime

class CpuMemoryUtilization(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 20
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.border_radius = 10
        
        # Data history
        self.history_len = 20
        self.cpu_history = [0] * self.history_len
        self.mem_history = [0] * self.history_len
        self.time_labels = [""] * self.history_len

        self.chart = ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=[],
                    stroke_width=2,
                    color=ft.Colors.CYAN,
                    curved=True,
                    stroke_cap_round=True,
                    below_line_bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.CYAN),
                ),
                ft.LineChartData(
                    data_points=[],
                    stroke_width=2,
                    color=ft.Colors.PURPLE,
                    curved=True,
                    stroke_cap_round=True,
                    below_line_bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.PURPLE),
                )
            ],
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE)),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=10, color=ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE), width=1
            ),
            left_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text("CPU (m)", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN),
            ),
            right_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text("Mem (Mi)", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE),
                show_labels=True,
            ),
            bottom_axis=ft.ChartAxis(
                labels_size=20,
            ),
            tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.SURFACE),
            expand=True,
        )

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Cluster Utilization (All Namespaces)", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            [
                                self._build_legend_item("Total CPU", ft.Colors.CYAN),
                                self._build_legend_item("Total Memory", ft.Colors.PURPLE),
                            ],
                            spacing=10
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Container(height=20),
                ft.Container(
                    content=self.chart,
                    height=200, 
                )
            ]
        )

    def _build_legend_item(self, label, color):
        return ft.Row(
            [
                ft.Container(width=10, height=10, bgcolor=color, border_radius=2),
                ft.Text(label, size=12, color=color, weight=ft.FontWeight.BOLD),
            ],
            spacing=5,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

    def update_data(self, metrics_map):
        # Calculate totals across ALL namespaces
        total_cpu = 0 # millicores
        total_mem = 0 # MiB
        
        # metrics_map contains pods from all namespaces now
        for pod_name, metrics in metrics_map.items():
            containers = metrics.get('containers', [])
            for c in containers:
                # CPU
                cpu_str = c['usage']['cpu']
                if cpu_str.endswith('n'): total_cpu += int(cpu_str[:-1]) / 1000000
                elif cpu_str.endswith('u'): total_cpu += int(cpu_str[:-1]) / 1000
                elif cpu_str.endswith('m'): total_cpu += int(cpu_str[:-1])
                else: 
                    try: total_cpu += int(cpu_str) * 1000
                    except: pass
                
                # Mem
                mem_str = c['usage']['memory']
                if mem_str.endswith('Ki'): total_mem += int(mem_str[:-2]) / 1024
                elif mem_str.endswith('Mi'): total_mem += int(mem_str[:-2])
                elif mem_str.endswith('Gi'): total_mem += int(mem_str[:-2]) * 1024
                else:
                    try: total_mem += int(mem_str) / (1024*1024)
                    except: pass

        # Update History
        self.cpu_history.pop(0)
        self.cpu_history.append(total_cpu)
        
        self.mem_history.pop(0)
        self.mem_history.append(total_mem)
        
        now = datetime.datetime.now()
        time_label = now.strftime("%H:%M:%S")
        self.time_labels.pop(0)
        self.time_labels.append(time_label)

        # Scaling for Dual Axis Simulation
        max_cpu = max(self.cpu_history) if max(self.cpu_history) > 0 else 1
        max_mem = max(self.mem_history) if max(self.mem_history) > 0 else 1
        
        # Add 10% headroom
        max_cpu = max_cpu * 1.1
        max_mem = max_mem * 1.1

        cpu_points = []
        mem_points = []
        
        for i in range(self.history_len):
            # Normalize to 0-100 for plotting
            cpu_val = (self.cpu_history[i] / max_cpu) * 100
            mem_val = (self.mem_history[i] / max_mem) * 100
            
            cpu_points.append(ft.LineChartDataPoint(i, cpu_val))
            mem_points.append(ft.LineChartDataPoint(i, mem_val))

        self.chart.data_series[0].data_points = cpu_points
        self.chart.data_series[1].data_points = mem_points
        
        self.chart.min_y = 0
        self.chart.max_y = 100
        self.chart.min_x = 0
        self.chart.max_x = self.history_len - 1

        # Update Axis Labels
        # Left Axis (CPU)
        self.chart.left_axis.labels = [
            ft.ChartAxisLabel(value=0, label=ft.Text("0", size=10)),
            ft.ChartAxisLabel(value=25, label=ft.Text(f"{int(max_cpu*0.25)}", size=10)),
            ft.ChartAxisLabel(value=50, label=ft.Text(f"{int(max_cpu*0.5)}", size=10)),
            ft.ChartAxisLabel(value=75, label=ft.Text(f"{int(max_cpu*0.75)}", size=10)),
            ft.ChartAxisLabel(value=100, label=ft.Text(f"{int(max_cpu)}", size=10)),
        ]
        
        # Right Axis (Mem)
        self.chart.right_axis.labels = [
            ft.ChartAxisLabel(value=0, label=ft.Text("0", size=10)),
            ft.ChartAxisLabel(value=25, label=ft.Text(f"{int(max_mem*0.25)}", size=10)),
            ft.ChartAxisLabel(value=50, label=ft.Text(f"{int(max_mem*0.5)}", size=10)),
            ft.ChartAxisLabel(value=75, label=ft.Text(f"{int(max_mem*0.75)}", size=10)),
            ft.ChartAxisLabel(value=100, label=ft.Text(f"{int(max_mem)}", size=10)),
        ]
        
        # Bottom Axis (Time)
        self.chart.bottom_axis.labels = [
            ft.ChartAxisLabel(value=0, label=ft.Text(self.time_labels[0], size=10)),
            ft.ChartAxisLabel(value=int(self.history_len/2), label=ft.Text(self.time_labels[int(self.history_len/2)], size=10)),
            ft.ChartAxisLabel(value=self.history_len-1, label=ft.Text(self.time_labels[-1], size=10)),
        ]

        self.update()
