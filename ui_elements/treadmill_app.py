"""
treadmill_app.py
Treadmill Exercise Application Module
======================================
This module is the main application for controlling a treadmill exercise simulation.
It integrates various components including UI elements, treadmill simulator, heart
rate collector, exercise data manager, and historical record viewer to provide
a comprehensive exercise application.

The application allows users to:
- Select exercise levels and set lap distances.
- Start, stop, and monitor treadmill exercises.
- Track real-time heart rate, speed, distance, and exercise time.
- View exercise history records and detailed session analysis, including heart rate graphs and AI-powered feedback.
- Configure application settings such as default lap distance and API keys.
- Simulate heart rate data through a separate UI.

Key features include:
- User-friendly graphical interface built with Tkinter.
- Real-time exercise monitoring and display.
- Integration with a heart rate collector and treadmill simulator.
- Exercise data logging and historical record management.
- AI-driven exercise analysis and feedback (via OpenAI API).
- Customizable settings and user preferences.

Author: Gaopeng Huang; Hui Guo
Email: perished_hgp@163.com; gh1848026781@163.com
Date Created: 2025-03-06
Last Modified: 2025-03-17
Copyright (c) 2025 PeakVision
All rights reserved.
This software is released under the GNU GENERAL PUBLIC LICENSE, see LICENSE for more information.
"""

import tkinter as tk
import time
import json
import os
import threading
import matplotlib.pyplot as plt
from tkinter import ttk, messagebox
from core.heart_rate_collector import HeartRateCollector, HeartRateListener
from ui_elements.heart_rate_ui import HeartRateUI
from simulator.treadmill_simulator import TreadmillSimulator
from core.treadmill_controller import TreadmillController
from core.exercise_data_manager import get_history_record_previews, load_exercise_data, update_exercise_data_feedback
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from openai import OpenAI

from ui_elements.settings_window import SettingsWindow


DEFAULT_SETTINGS_FILE = "data/app_settings.json" 

class TreadmillApp(tk.Tk, HeartRateListener):

    def __init__(self, collector):
        super().__init__()
        self.title("太极式健身跑V2.0")

        try:
            self.iconbitmap("icon/app_icon.ico") 
        except tk.TclError as e:
            print(f"加载应用图标失败: {e}") 
        

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

        self.app_settings = self.load_settings()

        self.openai_client = self.initialize_openai_client()


        try:
            self.settings_icon = tk.PhotoImage(file="icon/gear_icon.png")  
            self.settings_icon = self.settings_icon.subsample(10,10)
        except tk.TclError:
            self.settings_icon = None  

 
        settings_button = tk.Button(self,
                                     image=self.settings_icon if self.settings_icon else None, 
                                     text="" if self.settings_icon else "设置", 
                                     compound="top", 
                                     command=self.open_settings_window)
        settings_button.grid(row=0, column=0, sticky="nw", padx=5, pady=5) 

        tk.Label(self, text="选择等级:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.level_var = tk.StringVar(self)
        self.level_combobox = ttk.Combobox(self, textvariable=self.level_var, values=list(self.level_targets.keys()))
        self.level_combobox.grid(row=1, column=1, padx=10, pady=5)
        self.level_combobox.bind("<<ComboboxSelected>>", self.update_target)

        tk.Label(self, text="年龄:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.age_entry = tk.Entry(self)
        self.age_entry.grid(row=2, column=1, padx=10, pady=5)


        tk.Label(self, text="圈程距离(米):").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.distance_entry = tk.Entry(self)
        self.distance_entry.grid(row=3, column=1, padx=10, pady=5)
        default_lap_distance = self.app_settings.get("default_lap_distance", 200)
        self.distance_entry.insert(0, str(default_lap_distance)) 

        tk.Label(self, text="目标:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.target_label = tk.Label(self, text="无")
        self.target_label.grid(row=4, column=1, padx=10, pady=5)

        self.start_button = tk.Button(self, text="开始运动", command=self.start_treadmill)
        self.start_button.grid(row=5, column=0, padx=10, pady=5)
        self.stop_button = tk.Button(self, text="停止运动", command=self.stop_treadmill, state=tk.DISABLED)
        self.stop_button.grid(row=5, column=1, padx=10, pady=5)

        tk.Label(self, text="当前心率:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        self.current_rate_label = tk.Label(self, text="0 bpm")
        self.current_rate_label.grid(row=6, column=1, padx=10, pady=5)

        tk.Label(self, text="平均心率:").grid(row=7, column=0, sticky="w", padx=10, pady=5)
        self.average_rate_label = tk.Label(self, text="0 bpm")
        self.average_rate_label.grid(row=7, column=1, padx=10, pady=5)

        tk.Label(self, text="本圈平均心率:").grid(row=8, column=0, sticky="w", padx=10, pady=5)
        self.lap_average_rate_label = tk.Label(self, text="0 bpm")
        self.lap_average_rate_label.grid(row=8, column=1, padx=10, pady=5)

        tk.Label(self, text="上圈平均心率:").grid(row=9, column=0, sticky="w", padx=10, pady=5)
        self.last_lap_average_rate_label = tk.Label(self, text="0 bpm")
        self.last_lap_average_rate_label.grid(row=9, column=1, padx=10, pady=5)

        tk.Label(self, text="当前速度:").grid(row=10, column=0, sticky="w", padx=10, pady=5)
        self.current_speed_label = tk.Label(self, text="0 m/s")
        self.current_speed_label.grid(row=10, column=1, padx=10, pady=5)

        tk.Label(self, text="运动时间:").grid(row=11, column=0, sticky="w", padx=10, pady=5)
        self.time_label = tk.Label(self, text="00:00")
        self.time_label.grid(row=11, column=1, padx=10, pady=5)

        tk.Label(self, text="运动距离:").grid(row=12, column=0, sticky="w", padx=10, pady=5)
        self.distance_label = tk.Label(self, text="0 米")
        self.distance_label.grid(row=12, column=1, padx=10, pady=5)

        tk.Label(self, text="完成圈程:").grid(row=13, column=0, sticky="w", padx=10, pady=5)
        self.lap_label = tk.Label(self, text="0 圈")
        self.lap_label.grid(row=13, column=1, padx=10, pady=5)

        tk.Label(self, text="停止运动后平均心率 (1分钟):").grid(row=14, column=0, sticky="w", padx=10, pady=5)
        self.post_exercise_average_rate_label = tk.Label(self, text="等待运动停止...")
        self.post_exercise_average_rate_label.grid(row=14, column=1, padx=10, pady=5)

        open_ui_button = tk.Button(self, text="开启心率测量", command=self.open_heart_rate_ui)
        open_ui_button.grid(row=15, column=0, columnspan=1, pady=10)

        history_button = tk.Button(self, text="历史跑步记录", command=self.open_history_record)
        history_button.grid(row=15, column=1, columnspan=2, pady=10)


        self.treadmill_controller = TreadmillController(
            self.treadmill_simulator,
            self.level_var,
            self.distance_entry,
            self.current_speed_label,
            self.distance_label,
            self.lap_label,
            self.on_exercise_completion,
            collector,
            self.age_entry,
            self.post_exercise_average_rate_label
        )

        self.start_time = None
        self.elapsed_time = 0
        self.timer_running = False
        self.timer_id = None
        self.is_exercising = False
        self.record_feedbacks = {}
        self.feedback_static_text = {
            "过于轻松": "这次运动感觉非常轻松，可以尝试提高跑步等级或增加运动强度！",
            "舒适": "运动强度适中，状态良好，继续保持！",
            "一般": "运动强度还可以，但可以尝试挑战更高目标！",
            "难受": "感觉有些吃力了，注意调整呼吸和节奏，必要时降低强度。",
            "难以承受": "运动强度过大，身体负荷过重，请立即停止并降低等级！"
        }
        self.openai_client = None

    def load_settings(self):
        """从 JSON 文件加载设置，文件路径从设置中读取，或使用默认路径"""
        default_settings = {
            "settings_file_path": DEFAULT_SETTINGS_FILE, 
            "default_lap_distance": 200,
            "api_key": "",
            "base_url": "",
            "model": "Qwen/Qwen2.5-7B-Instruct"
        }
        settings_file_path = DEFAULT_SETTINGS_FILE 
        if os.path.exists(DEFAULT_SETTINGS_FILE): 
            try:
                with open(DEFAULT_SETTINGS_FILE, 'r') as f: 
                    initial_settings = json.load(f)
                    settings_file_path = initial_settings.get("settings_file_path", DEFAULT_SETTINGS_FILE) 
            except (FileNotFoundError, json.JSONDecodeError):
                pass 
        if os.path.exists(settings_file_path): 
            try:
                with open(settings_file_path, 'r') as f: 
                    loaded_settings = json.load(f)
                    return {**default_settings, **loaded_settings}
            except (FileNotFoundError, json.JSONDecodeError):
                messagebox.showerror("加载设置失败", f"无法加载设置文件: {settings_file_path}，将使用默认设置。") 
                return default_settings
        else:
            return default_settings
 

    def initialize_openai_client(self):
        api_key = self.app_settings.get("api_key")
        base_url = self.app_settings.get("base_url")

        self.api_key = api_key
        self.base_url = base_url
        try:
            if api_key and base_url:
                client = OpenAI(api_key=api_key, base_url=base_url)
                return client
            elif api_key: 
                 client = OpenAI(api_key=api_key)

                 return client
            else: 

                return None 
        except Exception as e:
            messagebox.showerror("API 初始化错误", f"OpenAI API 初始化失败: {e}")
            return None 



    def update_target(self, event):
        level = self.level_var.get()
        if level in self.level_targets:
            self.target_label.config(text=str(self.level_targets[level]))
        else:
            self.target_label.config(text="无")

    def on_heart_rate_received(self, heart_rate, average_heart_rate, lap_average_heart_rate, last_lap_average_rate):
        self.after(0, self._update_heart_rate_label, heart_rate, average_heart_rate, lap_average_heart_rate, last_lap_average_rate)


    def _update_heart_rate_label(self, heart_rate, average_heart_rate, lap_average_heart_rate, last_lap_average_rate):
        self.current_rate_label.config(text=f"{heart_rate} bpm")

        if self.is_exercising:
            self.average_rate_label.config(text=f"{average_heart_rate:.1f} bpm")
            self.lap_average_rate_label.config(text=f"{lap_average_heart_rate:.1f} bpm")
            self.last_lap_average_rate_label.config(text=f"{last_lap_average_rate:.1f} bpm")


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
            self.is_exercising = True


    def stop_treadmill(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.treadmill_controller.stop_exercise()
        self.stop_timer()
        self.is_exercising = False
        self.average_rate_label.config(text="0 bpm")
        self.lap_average_rate_label.config(text="0 bpm")
        self.last_lap_average_rate_label.config(text="0 bpm")


    def stop_timer(self):
        if self.timer_running:
            self.timer_running = False
            if self.timer_id is not None:
                self.after_cancel(self.timer_id)
                self.timer_id = None
    def update_timer(self):
        if self.timer_running:
            current_time = time.time()
            self.elapsed_time = int(current_time - self.start_time)
            time_str = self.format_time(self.elapsed_time)
            self.time_label.config(text=time_str)
            self.timer_id = self.after(1000, self.update_timer)
    def format_time(self, seconds):
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

    def open_history_record(self):
        history_window = tk.Toplevel(self)
        history_window.title("历史跑步记录")

        try:
            history_window.iconbitmap("icon/history_record.ico")
        except tk.TclError as e:
            print(f"加载历史记录窗口图标失败: {e}")

        refresh_button = tk.Button(history_window, text="刷新", command=lambda: self.refresh_history_record_list(listbox))
        refresh_button.grid(row=0, column=1, sticky='ne', padx=10, pady=10)

        list_frame = tk.Frame(history_window) 
        list_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10, columnspan=2) 

        history_previews = get_history_record_previews()

        if not history_previews:
            tk.Label(list_frame, text="没有历史跑步记录").pack(padx=20, pady=20) 
            return

        listbox = tk.Listbox(list_frame, width=80, selectmode=tk.SINGLE) 
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) 

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview) 
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y) 
        listbox.config(yscrollcommand=scrollbar.set) 


        for index, preview in enumerate(history_previews):
            display_text = f"{preview['datetime']} - Level: {preview['level']}, 距离: {preview['lap_distance']}m, 年龄: {preview['age']}"
            listbox.insert(tk.END, display_text)
            listbox.itemconfig(tk.END, fg="blue")
            listbox.itemconfig(tk.END, foreground="blue")

        listbox.bind("<Double-Button-1>", lambda event: self.show_history_detail(history_previews, listbox.curselection()))

        delete_button = tk.Button(history_window, text="删除记录", command=lambda: self.delete_history_record(history_previews, listbox))
        delete_button.grid(row=2, column=0, columnspan=2, pady=10) 

        history_window.grid_columnconfigure(0, weight=1) 
        history_window.grid_rowconfigure(1, weight=1)  
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)       


    def delete_history_record(self, history_previews, listbox): #  定义 delete_history_record 方法
        selection_indices = listbox.curselection()
        if not selection_indices:
            messagebox.showinfo("提示", "请选择要删除的记录。")
            return
        selected_index = int(selection_indices[0])
        if 0 <= selected_index < len(history_previews):
            selected_record_preview = history_previews[selected_index]
            filename = selected_record_preview['filename']
            filepath = os.path.join("data", filename)
            confirm_delete = messagebox.askyesno("确认删除", f"确定要删除记录: {filename} 吗?")
            if confirm_delete:
                try:
                    os.remove(filepath)
                    history_previews.pop(selected_index) #  从列表中移除
                    self.refresh_history_record_list(listbox) # 刷新 listbox
                    messagebox.showinfo("成功", f"记录 {filename} 删除成功。")
                except FileNotFoundError:
                    messagebox.showerror("错误", f"文件 {filename} 未找到，删除失败。")
                except Exception as e:
                    messagebox.showerror("错误", f"删除文件 {filename} 失败: {e}")


    def refresh_history_record_list(self, listbox):
        history_previews = get_history_record_previews()

        listbox.delete(0, tk.END) 

        if not history_previews:
            listbox.insert(tk.END, "没有历史跑步记录") 
            listbox.itemconfig(tk.END, fg="grey") 
            return

        for index, preview in enumerate(history_previews): 
            display_text = f"{preview['datetime']} - Level: {preview['level']}, 距离: {preview['lap_distance']}m, 年龄: {preview['age']}"
            listbox.insert(tk.END, display_text)
            listbox.itemconfig(tk.END, fg="blue")
            listbox.itemconfig(tk.END, foreground="blue") 

    def show_history_detail(self, history_previews, selection_indices):
        if not selection_indices:
            return
        selected_index = int(selection_indices[0])
        if 0 <= selected_index < len(history_previews):
            selected_record_preview = history_previews[selected_index]
            filename = selected_record_preview['filename']
            filepath = "data/" + filename
            exercise_data = load_exercise_data(filename)
            if exercise_data:
                detail_window = tk.Toplevel(self)
                detail_window.title(f"历史记录详情 - {filename}")

                try:
                    detail_window.iconbitmap("icon/history_record.ico")
                except tk.TclError as e:
                    print(f"加载历史记录详情窗口图标失败: {e}")

                delete_detail_button = tk.Button(detail_window, text="删除此记录",
                                                 command=lambda current_filename=filename, current_preview=selected_record_preview, current_detail_window=detail_window, current_index=selected_index:
                                                 self.delete_single_history_record_from_detail(current_filename, current_preview, current_detail_window, current_index, history_previews))
                delete_detail_button.grid(row=0, column=1, sticky='ne', padx=10, pady=10)

                info_frame = tk.Frame(detail_window)
                info_frame.grid(row=0, column=0, sticky='nw')

                tk.Label(info_frame, text=f"日期时间: {selected_record_preview['datetime']}").pack(anchor="w")
                tk.Label(info_frame, text=f"等级: {selected_record_preview['level']}").pack(anchor="w")
                tk.Label(info_frame, text=f"圈程距离: {selected_record_preview['lap_distance']} 米").pack(anchor="w")
                tk.Label(info_frame, text=f"年龄: {selected_record_preview['age']}").pack(anchor="w")

                duration_seconds_str = selected_record_preview.get('duration_seconds', '0')
                exercise_distance_str = selected_record_preview.get('exercise_distance', '0')
                try:
                    duration_seconds = int(duration_seconds_str)
                    exercise_distance = float(exercise_distance_str)
                except ValueError:
                    duration_seconds = 0
                    exercise_distance = 0

                heart_rates = [int(row[1]) for row in exercise_data]
                average_heart_rate = sum(heart_rates) / len(heart_rates) if heart_rates else 0

                minutes = duration_seconds // 60
                seconds = duration_seconds % 60
                formatted_duration = f"{minutes:02d}:{seconds:02d}"

                tk.Label(info_frame, text=f"运动时长: {formatted_duration}").pack(anchor="w")
                tk.Label(info_frame, text=f"运动距离: {exercise_distance:.2f} 米").pack(anchor="w")
                tk.Label(info_frame, text=f"平均心率: {average_heart_rate:.1f} bpm").pack(anchor="w")


                plt.rcParams['font.sans-serif'] = ['SimHei']
                plt.rcParams['axes.unicode_minus'] = False

                timestamps = [float(row[0]) for row in exercise_data]


                fig, ax = plt.subplots(figsize=(8, 6))
                ax.plot(timestamps, heart_rates)

                try:
                    age = int(selected_record_preview['age'])
                    max_heart_rate = 220 - age
                    threshold_80_percent = max_heart_rate * 0.8
                except (ValueError, KeyError):
                    threshold_80_percent = None

                if threshold_80_percent is not None:
                    ax.axhline(y=threshold_80_percent, color='r', linestyle='--', label=f'最大心率80%阈值 ({threshold_80_percent:.0f} bpm)')
                    ax.legend()

                ax.set_xlabel("运动时间 (秒)")
                ax.set_ylabel("心率 (bpm)")
                ax.set_title("运动心率变化图")
                ax.grid(True)

                canvas = FigureCanvasTkAgg(fig, master=detail_window)
                canvas_widget = canvas.get_tk_widget()
                canvas_widget.grid(row=1, column=0, columnspan=2, sticky='ewns', padx=10, pady=10)

                feedback_frame = tk.Frame(detail_window)
                feedback_frame.grid(row=2, column=0, columnspan=2, pady=10)

                feedback_labels = ["过于轻松", "舒适", "一般", "难受", "难以承受"]
                self.recommendation_label = tk.Label(detail_window, text="", pady=10)
                self.recommendation_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew") 

                def record_feedback(feedback_value, current_filename=filename, current_preview=selected_record_preview):
                    self.record_feedbacks[current_filename] = feedback_value
                    current_preview['feedback'] = feedback_value
                    update_recommendation_text(feedback_value)
                    update_exercise_data_feedback(current_filename, feedback_value)

                for i, label_text in enumerate(feedback_labels):
                    btn = tk.Button(feedback_frame, text=label_text, command=lambda text=label_text: record_feedback(text))
                    btn.pack(side=tk.LEFT, padx=5)
                    if i == 2:
                        pass 


                def update_recommendation_text(feedback_value):
                    if feedback_value in self.feedback_static_text:
                        self.recommendation_label.config(text=self.feedback_static_text[feedback_value])
                    else:
                        self.recommendation_label.config(text="")

                if 'feedback' in selected_record_preview and selected_record_preview['feedback']:
                    record_feedback(selected_record_preview['feedback'])

                if not self.openai_client:
                    try:
                        self.openai_client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                    except Exception as e:
                        messagebox.showerror("API 初始化错误", f"OpenAI API 初始化失败: {e}")
                        self.ai_analysis_text = tk.Text(detail_window, height=5, width=60, wrap=tk.WORD)
                        self.ai_analysis_text.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky='ewns')
                        self.ai_analysis_text.insert(tk.END, "OpenAI API 初始化失败，无法进行AI分析。请检查 API Key 和网络连接。\n")
                        self.ai_analysis_text.config(state=tk.DISABLED)
                        return

                self.ai_analysis_text = tk.Text(detail_window, height=10, width=60, wrap=tk.WORD)
                self.ai_analysis_text.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky='ewns')
                self.ai_analysis_text.insert(tk.END, "正在分析中，请稍候...\n")
                self.ai_analysis_text.config(state=tk.DISABLED)


                csv_data_string = ""
                for row in exercise_data:
                    csv_data_string += ",".join(map(str, row)) + "\n"

                prompt_content = f"""
这是一份太极式健身跑的心率记录，请分析用户的运动心率数据，数据以 CSV 格式提供，包含时间戳 (秒) 和心率值 (bpm) 两列。

运动时长: {formatted_duration}
运动距离: {exercise_distance:.2f} 米
平均心率: {average_heart_rate:.1f} bpm

CSV 格式的心率数据:
{csv_data_string}

请根据以上数据，提供一份详细的运动分析报告。
分析报告应该包括以下几个方面:
- 总体运动强度评估 (例如: 偏低, 适中, 偏高)。
- 心率在运动过程中的详细变化趋势分析 (例如:  更精细地描述心率的波动情况，峰值和谷值出现的时间点，心率恢复速度等，基于 CSV 数据进行分析)。
- 基于详细的心率数据，更深入地评价本次运动效果，并给出更个性化的建议 (例如:  更具体地指出运动强度不足或过高的时间段，更精确地评估心率恢复情况，给出更贴合用户实际情况的运动建议)。
- 更具体的运动建议 (例如:  如果运动强度偏低，建议提高多少速度或坡度; 如果心率波动大，建议如何调整呼吸和节奏;  针对心率恢复情况给出建议，例如运动后拉伸或放松)。

注意事项：
输出的语气需要元气满满的。
最后为用户给出一句加油的话语。
请输出纯text文本。
有时候输出没有标点，这是错误的输出方式。
不要分段。

请使用中文生成 150 字左右的详细分析报告。
                """

                def call_openai_api(prompt):
                    try:
                        response = self.openai_client.chat.completions.create(
                            model=self.app_settings.get("model", "Qwen/Qwen2.5-7B-Instruct"),
                            messages=[{'role': 'user', 'content': prompt}],
                            stream=False
                        )
                        ai_response_text = response.choices[0].message.content
                        if ai_response_text:
                            display_ai_analysis_result(ai_response_text)
                        else:
                            display_ai_analysis_result("AI 分析未能生成有效结果。")
                    except Exception as api_error:
                        display_ai_analysis_result(f"调用 AI API 出错: {api_error}")

                def display_ai_analysis_result(analysis_text):
                    detail_window.after(0, lambda text=analysis_text: _update_text(text))

                def _update_text(text):
                    self.ai_analysis_text.config(state=tk.NORMAL)
                    self.ai_analysis_text.delete("1.0", tk.END)
                    self.ai_analysis_text.insert(tk.END, text)
                    self.ai_analysis_text.config(state=tk.DISABLED)


                threading.Thread(target=call_openai_api, args=(prompt_content,), daemon=True).start()

                def on_detail_window_close():
                    plt.close(fig)
                    detail_window.destroy()
                detail_window.protocol("WM_DELETE_WINDOW", on_detail_window_close)


    def delete_single_history_record_from_detail(self, filename, selected_record_preview, detail_window, selected_index, history_previews):
        filepath = os.path.join("data", filename)

        confirm_delete = messagebox.askyesno("确认删除", f"确定要删除记录: {filename} 吗?")
        if confirm_delete:
            try:
                os.remove(filepath)
                history_previews.pop(selected_index)
                messagebox.showinfo("成功", f"记录 {filename} 删除成功。")
                detail_window.destroy()

            except FileNotFoundError:
                messagebox.showerror("错误", f"文件 {filename} 未找到，删除失败。")
            except Exception as e:
                messagebox.showerror("错误", f"删除文件 {filename} 失败: {e}")


    def open_settings_window(self):
        default_lap_distance = self.app_settings.get("default_lap_distance", 200) 
        SettingsWindow(self, default_lap_distance, self, self.app_settings)





if __name__ == "__main__":
    collector = HeartRateCollector()
    app = TreadmillApp(collector)
    app.mainloop()
