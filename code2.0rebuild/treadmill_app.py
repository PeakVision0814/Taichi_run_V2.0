import tkinter as tk
import time
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
        self.protocol("WM_DELETE_WINDOW", self.stop_app)
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
        self.distance_entry.insert(0, "200")

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
        self.time_label = tk.Label(self, text="00:00")
        self.time_label.grid(row=9, column=1, padx=10, pady=5)

        tk.Label(self, text="运动距离:").grid(row=10, column=0, sticky="w", padx=10, pady=5)
        self.distance_label = tk.Label(self, text="0 米")
        self.distance_label.grid(row=10, column=1, padx=10, pady=5)

        tk.Label(self, text="完成圈程:").grid(row=11, column=0, sticky="w", padx=10, pady=5)
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
            self.lap_label,
            self.on_exercise_completion
        )

        self.start_time = None 
        self.elapsed_time = 0 
        self.timer_running = False 
        self.timer_id = None     
    
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
        start_success = self.treadmill_controller.start_exercise()
        if start_success:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.distance_label.config(text="0 米")
            self.start_time = time.time()  
            self.elapsed_time = 0    
            self.timer_running = True   
            self.update_timer()          


    def stop_treadmill(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.treadmill_controller.stop_exercise()
        self.stop_timer() # 停止定时器

    def stop_timer(self):
        """停止计时器"""
        if self.timer_running:
            self.timer_running = False
            if self.timer_id is not None:
                self.after_cancel(self.timer_id) 
                self.timer_id = None
    def update_timer(self):
        """更新时间标签"""
        if self.timer_running:
            current_time = time.time()
            self.elapsed_time = int(current_time - self.start_time) 
            time_str = self.format_time(self.elapsed_time)
            self.time_label.config(text=time_str)
            self.timer_id = self.after(1000, self.update_timer)
    def format_time(self, seconds):
        """将秒数格式化为 分:秒 形式"""
        minutes = seconds // 60
        secs = seconds % 60
        return "{:02d}:{:02d}".format(minutes, secs) 

    def stop_app(self):
        if hasattr(self, 'heart_rate_simulator'):
            self.heart_rate_simulator.stop()
        self.stop_treadmill()
        self.destroy()

    def on_exercise_completion(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    collector = HeartRateCollector()
    app = TreadmillApp(collector)
    app.mainloop()