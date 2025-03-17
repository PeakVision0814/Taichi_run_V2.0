# heart_rate_ui.py
import tkinter as tk
from simulator.heart_rate_simulator import HeartRateSimulator

class HeartRateUI:
    def __init__(self, root, collector):
        self.root = root
        self.root.title("心率模拟器")

        try:
            self.root.iconbitmap("icon/heart_rate.ico")  # 设置窗口图标 (ICO)
        except tk.TclError as e:
            print(f"加载心率模拟器窗口图标失败: {e}")  # 如果加载失败，打印错误信息


        self.collector = collector 
        self.simulator = HeartRateSimulator(collector)  

        self.rate_label = tk.Label(root, text="心率: 0 bpm", font=("Arial", 24))
        self.rate_label.pack(pady=20)

        button_frame = tk.Frame(root)
        button_frame.pack()

        ranges = [(60, 70), (70, 90), (90, 110), (130, 150), (150, 170), (170, 195), (195, 250)]
        for low, high in ranges:
            button = tk.Button(button_frame, text=f"{low}-{high}",
                            command=lambda l=low, h=high: self.set_rate_range((l, h)))
            button.pack(side=tk.LEFT, padx=5)

        stop_button = tk.Button(root, text="停止模拟", command=self.stop_simulation)
        stop_button.pack(pady=10)

        self.update_rate()

        self.root.protocol("WM_DELETE_WINDOW", self.stop_ui)  

    def set_rate_range(self, rate_range):
        self.simulator.set_rate_range(rate_range)
        if not self.simulator.running:
            self.simulator.start()

    def stop_simulation(self):
        self.simulator.stop()

    def update_rate(self):
        rate = self.simulator.get_rate()
        self.rate_label.config(text=f"心率: {rate} bpm")
        self.root.after(1000, self.update_rate) 

    def stop_ui(self):
        """停止心率模拟器并关闭UI"""
        self.stop_simulation() 
        self.root.destroy() 