"""
heart_rate_ui.py
Heart Rate Simulator User Interface Module
===========================================
This module provides a graphical user interface (GUI) for controlling and
visualizing a heart rate simulator. It uses Tkinter to create a window with
buttons to set different heart rate ranges and a label to display the current
simulated heart rate.

The HeartRateUI class integrates a HeartRateSimulator instance to generate
simulated heart rate data and displays it in real-time. Users can select
predefined heart rate ranges by clicking buttons, and the UI continuously
updates the displayed heart rate to reflect the simulator's output.

Key features:
- GUI control for starting and stopping heart rate simulation.
- Buttons for selecting predefined heart rate ranges for simulation.
- Real-time display of the simulated heart rate.
- Integration with HeartRateSimulator for data generation.
- Icon support for the application window.

Author: Gaopeng Huang; Hui Guo
Email: perished_hgp@163.com; gh1848026781@163.com
Date Created: 2025-03-06
Last Modified: 2025-03-17
Copyright (c) 2025 PeakVision
All rights reserved.
This software is released under the GNU GENERAL PUBLIC LICENSE, see LICENSE for more information.
"""


import tkinter as tk
from simulator.heart_rate_simulator import HeartRateSimulator

class HeartRateUI:
    def __init__(self, root, collector):
        self.root = root
        self.root.title("心率模拟器")

        try:
            self.root.iconbitmap("icon/heart_rate.ico") 
        except tk.TclError as e:
            print(f"加载心率模拟器窗口图标失败: {e}")  


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