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

DEFAULT_SETTINGS_FILE = "data/app_settings.json"

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

        tk.Label(self, text="设置文件路径:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.settings_file_path_entry = tk.Entry(self)
        self.settings_file_path_entry.grid(row=0, column=1, padx=10, pady=5)
        settings_file_path = self.settings.get("settings_file_path", DEFAULT_SETTINGS_FILE)
        self.settings_file_path_entry.insert(0, settings_file_path)

        tk.Label(self, text="默认圈程距离 (米):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.default_distance_entry = tk.Entry(self)
        self.default_distance_entry.grid(row=1, column=1, padx=10, pady=5)
        self.default_distance_entry.insert(0, str(self.default_lap_distance))

        tk.Label(self, text="API Key:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.api_key_entry = tk.Entry(self, show="*")
        self.api_key_entry.grid(row=2, column=1, padx=10, pady=5)
        self.api_key_entry.insert(0, self.settings.get("api_key", ""))

        tk.Label(self, text="Base URL:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.base_url_entry = tk.Entry(self)
        self.base_url_entry.grid(row=3, column=1, padx=10, pady=5)
        self.base_url_entry.insert(0, self.settings.get("base_url", ""))

        tk.Label(self, text="Model:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.model_entry = tk.Entry(self)
        self.model_entry.grid(row=4, column=1, padx=10, pady=5)
        self.model_entry.insert(0, self.settings.get("model", ""))

        apply_button = tk.Button(self, text="应用", command=self.apply_settings)
        apply_button.grid(row=5, column=0, pady=10, sticky="ew")

        save_button = tk.Button(self, text="保存", command=self.save_settings)
        save_button.grid(row=5, column=1, pady=10, sticky="ew")

        # 让按钮在列中均匀分布
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)


    def apply_settings(self):
        self._save_settings_logic()
            # messagebox.showinfo("设置已应用", "设置已应用。")


    def save_settings(self):
        if self._save_settings_logic():
            self.destroy() # 关闭设置窗口


    def _save_settings_logic(self):
        try:
            new_settings_file_path = self.settings_file_path_entry.get()
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
                return False # 返回 False 表示保存失败

            self.settings["settings_file_path"] = new_settings_file_path
            self.settings["default_lap_distance"] = new_default_distance
            self.settings["api_key"] = new_api_key
            self.settings["base_url"] = new_base_url
            self.settings["model"] = new_model

            self.save_settings_to_file()
            return True # 返回 True 表示保存成功

        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的整数作为圈程距离。")
            return False # 返回 False 表示保存失败


    def save_settings_to_file(self):
        settings_file_path = self.settings.get("settings_file_path", DEFAULT_SETTINGS_FILE)
        with open(settings_file_path, 'w') as f:
            json.dump(self.settings, f, indent=4)


if __name__ == '__main__':
    # 示例主应用程序 (用于测试设置窗口)
    class MainApp(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("主程序窗口 (用于测试)")
            self.DEFAULT_LAP_DISTANCE = 400  # 默认圈程距离
            self.settings = self.load_settings() # 加载设置

            tk.Label(self, text="圈程距离:").pack(padx=10, pady=5)
            self.distance_entry = tk.Entry(self)
            self.distance_entry.pack(padx=10, pady=5)
            self.distance_entry.insert(0, str(self.DEFAULT_LAP_DISTANCE))


            settings_button = tk.Button(self, text="打开设置", command=self.open_settings)
            settings_button.pack(pady=20)

        def open_settings(self):
            settings_win = SettingsWindow(self, self.DEFAULT_LAP_DISTANCE, self, self.settings)
            settings_win.grab_set() # 模态窗口

        def load_settings(self):
            default_settings = {
                "settings_file_path": DEFAULT_SETTINGS_FILE,
                "default_lap_distance": 400,
                "api_key": "",
                "base_url": "",
                "model": ""
            }
            settings_file_path = default_settings["settings_file_path"]

            if os.path.exists(settings_file_path):
                try:
                    with open(settings_file_path, 'r') as f:
                        user_settings = json.load(f)
                        # 合并默认设置和用户设置，确保所有键都存在
                        merged_settings = {**default_settings, **user_settings}
                        return merged_settings
                except json.JSONDecodeError:
                    print("设置文件JSON格式错误，加载默认设置。")
                    return default_settings
            else:
                print("设置文件不存在，加载默认设置。")
                return default_settings


    root = MainApp()
    root.mainloop()
