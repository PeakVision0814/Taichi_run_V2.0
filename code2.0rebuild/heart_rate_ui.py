import tkinter as tk
from heart_rate_simulator import HeartRateSimulator

class HeartRateUI:
    def __init__(self, root, collector): #添加collector参数
        self.root = root
        self.root.title("心率模拟器")

        self.collector = collector #添加collector参数
        self.simulator = HeartRateSimulator(collector) #传递collector参数给模拟器

        # 心率显示标签
        self.rate_label = tk.Label(root, text="心率: 0 bpm", font=("Arial", 24))
        self.rate_label.pack(pady=20)

        # 按钮框架
        button_frame = tk.Frame(root)
        button_frame.pack()

        # 心率范围按钮
        ranges = [(60, 70), (70, 90), (90, 110), (130, 150), (150, 170), (170, 195), (195, 250)]
        for low, high in ranges:
            button = tk.Button(button_frame, text=f"{low}-{high}", command=lambda l=low, h=high: self.set_rate_range((l, h)))
            button.pack(side=tk.LEFT, padx=5)

        # 停止按钮
        stop_button = tk.Button(root, text="停止模拟", command=self.stop_simulation)
        stop_button.pack(pady=10)

        # 更新心率显示
        self.update_rate()

    def set_rate_range(self, rate_range):
        self.simulator.set_rate_range(rate_range)
        if not self.simulator.running:
            self.simulator.start()

    def stop_simulation(self):
        self.simulator.stop()

    def update_rate(self):
        rate = self.simulator.get_rate()
        self.rate_label.config(text=f"心率: {rate} bpm")
        self.root.after(1000, self.update_rate)  # 每秒更新一次