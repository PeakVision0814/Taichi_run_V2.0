# settings_window.py
import tkinter as tk
from tkinter import messagebox
import json
import os

SETTINGS_FILE = "data/app_settings.json"  # 定义设置文件路径

class SettingsWindow(tk.Toplevel):
    def __init__(self, master, default_lap_distance, master_app, initial_settings): # [修改 16.1] 添加 initial_settings 参数
        super().__init__(master)
        self.title("设置")
        
        try:
            self.iconbitmap("icon/gear_icon.ico") #  设置窗口图标 (ICO)
        except tk.TclError as e:
            print(f"加载设置窗口图标失败: {e}") #  如果加载失败，打印错误信息


        self.master_app = master_app
        self.default_lap_distance = default_lap_distance
        self.settings = initial_settings  # [修改 16.2]  保存初始设置

        # 默认圈程距离设置
        tk.Label(self, text="默认圈程距离 (米):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.default_distance_entry = tk.Entry(self)
        self.default_distance_entry.grid(row=0, column=1, padx=10, pady=5)
        self.default_distance_entry.insert(0, str(self.default_lap_distance))

        # OpenAI API Key 设置
        tk.Label(self, text="API Key:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.api_key_entry = tk.Entry(self, show="*") #  密码形式显示
        self.api_key_entry.grid(row=1, column=1, padx=10, pady=5)
        self.api_key_entry.insert(0, self.settings.get("api_key", "")) # [修改 16.3]  从设置中加载

        # OpenAI Base URL 设置
        tk.Label(self, text="Base URL:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.base_url_entry = tk.Entry(self)
        self.base_url_entry.grid(row=2, column=1, padx=10, pady=5)
        self.base_url_entry.insert(0, self.settings.get("base_url", "")) # [修改 16.4] 从设置中加载

        # OpenAI Model 设置
        tk.Label(self, text="Model:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.model_entry = tk.Entry(self)
        self.model_entry.grid(row=3, column=1, padx=10, pady=5)
        self.model_entry.insert(0, self.settings.get("model", "")) # [修改 16.5] 从设置中加载

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
                return #  如果圈程距离错误，直接返回，不保存其他设置

            # [修改 16.6]  更新设置字典
            self.settings["default_lap_distance"] = new_default_distance
            self.settings["api_key"] = new_api_key
            self.settings["base_url"] = new_base_url
            self.settings["model"] = new_model

            # [修改 16.7]  保存设置到 JSON 文件
            self.save_settings_to_file()

            messagebox.showinfo("设置已保存", "设置已保存。")
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的整数作为圈程距离。")

    def save_settings_to_file(self):
        """将设置保存到 JSON 文件"""
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f, indent=4) #  使用 indent=4 使 JSON 文件更易读

