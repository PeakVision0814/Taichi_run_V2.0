"""
settings_window.py
Application Settings Window Module
===================================
This module implements a settings window for the application, allowing users to
configure various application parameters such as default lap distance, API key,
base URL, and model settings.
The SettingsWindow class provides a graphical interface built with Tkinter to:
- Display and modify application settings.
- Persist settings to a JSON file (`data/app_settings.json`).
- Load settings from the JSON file upon initialization.
- Validate user inputs to ensure correct setting values.
- Communicate updated settings back to the main application.
Settings that can be configured through this window include:
- Default lap distance for treadmill exercises.
- API Key for external services.
- Base URL for API endpoints.
- Model selection for API interactions.
Author: Gaopeng Huang; Hui Guo
Email: perished_hgp@163.com; gh1848026781@163.com
Date Created: 2025-03-06
Last Modified: 2025-03-17
Copyright (c) 2025 PeakVision
All rights reserved.
This software is released under the GNU GENERAL PUBLIC LICENSE, see LICENSE for more information.
"""

import tkinter as tk
from tkinter import messagebox
import json
import os

SETTINGS_FILE = "data/app_settings.json"  

class SettingsWindow(tk.Toplevel):
    def __init__(self, master, default_lap_distance, master_app, initial_settings):
        super().__init__(master)
        self.title("设置")
        
        try:
            self.iconbitmap("icon/gear_icon.ico") 
        except tk.TclError as e:
            print(f"加载设置窗口图标失败: {e}") 


        self.master_app = master_app
        self.default_lap_distance = default_lap_distance
        self.settings = initial_settings  

        tk.Label(self, text="默认圈程距离 (米):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.default_distance_entry = tk.Entry(self)
        self.default_distance_entry.grid(row=0, column=1, padx=10, pady=5)
        self.default_distance_entry.insert(0, str(self.default_lap_distance))

        tk.Label(self, text="API Key:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.api_key_entry = tk.Entry(self, show="*") 
        self.api_key_entry.grid(row=1, column=1, padx=10, pady=5)
        self.api_key_entry.insert(0, self.settings.get("api_key", "")) 

        tk.Label(self, text="Base URL:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.base_url_entry = tk.Entry(self)
        self.base_url_entry.grid(row=2, column=1, padx=10, pady=5)
        self.base_url_entry.insert(0, self.settings.get("base_url", "")) 

        tk.Label(self, text="Model:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.model_entry = tk.Entry(self)
        self.model_entry.grid(row=3, column=1, padx=10, pady=5)
        self.model_entry.insert(0, self.settings.get("model", "")) 

        save_button = tk.Button(self, text="保存设置", command=self.save_settings)
        save_button.grid(row=4, column=0, columnspan=2, pady=10)

    def save_settings(self):
        try:
            new_default_distance = int(self.default_distance_entry.get())
            new_api_key = self.api_key_entry.get()
            new_base_url = self.base_url_entry.get()
            new_model = self.model_entry.get()

            if new_default_distance > 0:
                self.master_app.DEFAULT_LAP_DISTANCE = new_default_distance
                self.master_app.distance_entry.delete(0, tk.END)
                self.master_app.distance_entry.insert(0, str(self.master_app.DEFAULT_LAP_DISTANCE))
            else:
                messagebox.showerror("输入错误", "圈程距离必须是正整数。")
                return 

            self.settings["default_lap_distance"] = new_default_distance
            self.settings["api_key"] = new_api_key
            self.settings["base_url"] = new_base_url
            self.settings["model"] = new_model

            self.save_settings_to_file()

            messagebox.showinfo("设置已保存", "设置已保存。")
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的整数作为圈程距离。")

    def save_settings_to_file(self):
        """将设置保存到 JSON 文件"""
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f, indent=4) 

