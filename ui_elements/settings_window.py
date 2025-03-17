# settings_window.py
import tkinter as tk
from tkinter import messagebox
class SettingsWindow(tk.Toplevel):
    def __init__(self, master, default_lap_distance, master_app): # [修改 15.1] 添加 default_lap_distance 和 master_app 参数
        super().__init__(master)
        self.title("设置")
        self.master_app = master_app # [修改 15.2]  保存 master_app 实例
        self.default_lap_distance = default_lap_distance # [修改 15.3] 保存 default_lap_distance
        tk.Label(self, text="默认圈程距离 (米):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.default_distance_entry = tk.Entry(self)
        self.default_distance_entry.grid(row=0, column=1, padx=10, pady=5)
        self.default_distance_entry.insert(0, str(self.default_lap_distance)) # [修改 15.4] 使用 self.default_lap_distance
        save_button = tk.Button(self, text="保存设置", command=self.save_settings)
        save_button.grid(row=1, column=0, columnspan=2, pady=10)
    def save_settings(self):
        try:
            new_default_distance = int(self.default_distance_entry.get())
            if new_default_distance > 0:
                #  这里仍然需要修改，不能直接修改 TreadmillApp.DEFAULT_LAP_DISTANCE
                #  需要通过 master_app 实例来更新
                self.master_app.DEFAULT_LAP_DISTANCE = new_default_distance # [修改 15.5]  通过 master_app 更新类变量
                self.master_app.distance_entry.delete(0, tk.END)
                self.master_app.distance_entry.insert(0, str(self.master_app.DEFAULT_LAP_DISTANCE)) # [修改 15.6] 通过 master_app 获取类变量
                messagebox.showinfo("设置已保存", "默认圈程距离已保存。")
            else:
                messagebox.showerror("输入错误", "圈程距离必须是正整数。")

        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的整数作为圈程距离。")
