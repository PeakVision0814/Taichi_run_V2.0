import tkinter as tk
from tkinter import ttk
from heart_rate_collector import HeartRateCollector, HeartRateListener
from heart_rate_ui import HeartRateUI
from treadmill_simulator import TreadmillSimulator
from treadmill_controller import TreadmillController

class TreadmillApp(tk.Tk, HeartRateListener):
    def __init__(self, collector):
        super().__init__()
        self.title("跑步机应用")

        self.collector = collector
        self.collector.add_listener(self)

        self.treadmill_simulator = TreadmillSimulator()

        self.level_targets = {"2": 4000,
                              "3": 4200,
                              "4": 4600,
                              "5": 5000,
                              "6": 5200,
                              "7": 5200,
                              "8": 5400,
                              "9": 5400,
                              "10": 5400
        }

        tk.Label(self, text="选择等级:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.level_var = tk.StringVar(self)
        self.level_combobox = ttk.Combobox(self, textvariable=self.level_var, values=list(self.level_targets.keys()))
        self.level_combobox.grid(row=0, column=1, padx=10, pady=5)
        self.level_combobox.bind("<<ComboboxSelected>>", self.update_target)

        tk.Label(self, text="年龄:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.age_entry = tk.Entry(self)
        self.age_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self, text="圈程距离(米):").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.distance_entry = tk.Entry(self)
        self.distance_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self, text="目标:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.target_label = tk.Label(self, text="无")
        self.target_label.grid(row=3, column=1, padx=10, pady=5)

        self.start_button = tk.Button(self, text="开始运动", command=self.start_treadmill) 
        self.start_button.grid(row=4, column=0, padx=10, pady=5)
        self.stop_button = tk.Button(self, text="停止运动", command=self.stop_treadmill, state=tk.DISABLED) 
        self.stop_button.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(self, text="当前心率:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        self.current_rate_label = tk.Label(self, text="0 bpm")
        self.current_rate_label.grid(row=5, column=1, padx=10, pady=5)

        tk.Label(self, text="平均心率:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        self.average_rate_label = tk.Label(self, text="0 bpm")
        self.average_rate_label.grid(row=6, column=1, padx=10, pady=5)

        tk.Label(self, text="本圈平均心率:").grid(row=7, column=0, sticky="w", padx=10, pady=5)
        self.lap_average_rate_label = tk.Label(self, text="0 bpm")
        self.lap_average_rate_label.grid(row=7, column=1, padx=10, pady=5)

        tk.Label(self, text="当前速度:").grid(row=8, column=0, sticky="w", padx=10, pady=5)
        self.current_speed_label = tk.Label(self, text="0 m/s")
        self.current_speed_label.grid(row=8, column=1, padx=10, pady=5)

        tk.Label(self, text="运动时间:").grid(row=9, column=0, sticky="w", padx=10, pady=5)
        self.time_label = tk.Label(self, text="0 秒")
        self.time_label.grid(row=9, column=1, padx=10, pady=5)

        tk.Label(self, text="运动距离:").grid(row=10, column=0, sticky="w", padx=10, pady=5)
        self.distance_label = tk.Label(self, text="0 米")
        self.distance_label.grid(row=10, column=1, padx=10, pady=5)

        tk.Label(self, text="当前圈程:").grid(row=11, column=0, sticky="w", padx=10, pady=5)
        self.lap_label = tk.Label(self, text="0 圈")
        self.lap_label.grid(row=11, column=1, padx=10, pady=5)

        open_ui_button = tk.Button(self, text="打开心率模拟器", command=self.open_heart_rate_ui)
        open_ui_button.grid(row=12, column=0, columnspan=2, pady=10)

        self.treadmill_controller = TreadmillController( 
            self.treadmill_simulator,
            self.level_var,
            self.distance_entry,
            self.current_speed_label, 
            self.distance_label, 
            self.lap_label           
        )
    
    def update_target(self, event):
        """根据选择的等级更新目标"""
        level = self.level_var.get()
        if level in self.level_targets:
            self.target_label.config(text=str(self.level_targets[level]))
        else:
            self.target_label.config(text="无")

    def on_heart_rate_received(self, heart_rate):
        self.after(0, self._update_heart_rate_label, heart_rate)

    def _update_heart_rate_label(self, heart_rate):
        self.current_rate_label.config(text=f"{heart_rate} bpm")

    def open_heart_rate_ui(self):
        heart_rate_ui_window = tk.Toplevel(self)
        HeartRateUI(heart_rate_ui_window, self.collector)

    def start_treadmill(self):
        # 调用 TreadmillController 的 start_exercise 方法，并获取返回值
        start_success = self.treadmill_controller.start_exercise()
        # 检查返回值，只有启动成功才改变按钮状态
        if start_success:
            # 禁用开始按钮，启用停止按钮
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            # 重置运动距离显示为 0 米 (保持不变)
            self.distance_label.config(text="0 米")
        # 如果启动失败 (start_success 为 False)，则按钮状态保持不变，让用户可以修改输入并重试

    def stop_treadmill(self):
        # 启用开始按钮，禁用停止按钮
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        # 调用 TreadmillController 的 stop_exercise 方法
        self.treadmill_controller.stop_exercise()


if __name__ == "__main__":
    collector = HeartRateCollector()
    app = TreadmillApp(collector)
    app.mainloop()