# treadmill_app.py
import tkinter as tk
import time
import matplotlib.pyplot as plt
from tkinter import ttk, filedialog, messagebox
from core.heart_rate_collector import HeartRateCollector, HeartRateListener
from ui_elements.heart_rate_ui import HeartRateUI
from simulator.treadmill_simulator import TreadmillSimulator
from core.treadmill_controller import TreadmillController
from core.exercise_data_manager import get_history_record_previews, load_exercise_data
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from openai import OpenAI
import threading


class TreadmillApp(tk.Tk, HeartRateListener):
    DEFAULT_LAP_DISTANCE = 200  #  [修改 11.1]  定义类变量存储默认圈程距离

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

        #  [修改 12.1] 加载齿轮图标
        try:
            self.settings_icon = tk.PhotoImage(file="icon/gear_icon.png")  # 假设齿轮图标文件名为 gear_icon.gif，与脚本在同一目录
            self.settings_icon = self.settings_icon.subsample(10,10)
        except tk.TclError:
            self.settings_icon = None  # 如果图标加载失败，则设置为 None

        #  [修改 12.2] 创建 "设置" 按钮，使用图标，并放置在左上角
        settings_button = tk.Button(self,
                                     image=self.settings_icon if self.settings_icon else None, # 使用图标，如果加载失败则不显示图标
                                     text="" if self.settings_icon else "设置", #  如果使用图标，则不显示文字，否则显示 "设置" 文字
                                     compound="top", #  确保在没有文字时，图标能正确显示 (如果需要)
                                     command=self.open_settings_window)
        settings_button.grid(row=0, column=0, sticky="nw", padx=5, pady=5) #  放置在左上角 (row=0, column=0), sticky="nw" 对齐到西北角

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
        self.distance_entry.insert(0, str(TreadmillApp.DEFAULT_LAP_DISTANCE)) #  [修改 11.2]  初始值使用类变量

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

        open_ui_button = tk.Button(self, text="打开心率模拟器", command=self.open_heart_rate_ui)
        open_ui_button.grid(row=15, column=0, columnspan=2, pady=10)

        history_button = tk.Button(self, text="历史跑步记录", command=self.open_history_record)
        history_button.grid(row=16, column=0, columnspan=2, pady=10)


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
        history_previews = get_history_record_previews()

        if not history_previews:
            tk.Label(history_window, text="没有历史跑步记录").pack(padx=20, pady=20)
            return

        listbox = tk.Listbox(history_window, width=80)
        listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        for preview in history_previews:
            display_text = f"{preview['datetime']} - Level: {preview['level']}, 距离: {preview['lap_distance']}m, 年龄: {preview['age']}"
            listbox.insert(tk.END, display_text)
            listbox.itemconfig(tk.END, fg="blue")

        listbox.bind("<Double-Button-1>", lambda event: self.show_history_detail(history_previews, listbox.curselection()))

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
                tk.Label(detail_window, text=f"日期时间: {selected_record_preview['datetime']}").pack(anchor="w")
                tk.Label(detail_window, text=f"等级: {selected_record_preview['level']}").pack(anchor="w")
                tk.Label(detail_window, text=f"圈程距离: {selected_record_preview['lap_distance']} 米").pack(anchor="w")
                tk.Label(detail_window, text=f"年龄: {selected_record_preview['age']}").pack(anchor="w")

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

                tk.Label(detail_window, text=f"运动时长: {formatted_duration}").pack(anchor="w")
                tk.Label(detail_window, text=f"运动距离: {exercise_distance:.2f} 米").pack(anchor="w")
                tk.Label(detail_window, text=f"平均心率: {average_heart_rate:.1f} bpm").pack(anchor="w")


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
                canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
                canvas.draw()

                feedback_frame = tk.Frame(detail_window)
                feedback_frame.pack(pady=10)

                feedback_labels = ["过于轻松", "舒适", "一般", "难受", "难以承受"]
                self.recommendation_label = tk.Label(detail_window, text="", pady=10)

                def record_feedback(feedback_value, current_filename=filename, current_preview=selected_record_preview):
                    self.record_feedbacks[current_filename] = feedback_value
                    current_preview['feedback'] = feedback_value
                    update_recommendation_text(feedback_value)

                for i, label_text in enumerate(feedback_labels):
                    btn = tk.Button(feedback_frame, text=label_text, command=lambda text=label_text: record_feedback(text))
                    btn.pack(side=tk.LEFT, padx=5)
                    if i == 2:
                        self.recommendation_label.pack(padx=10)


                def update_recommendation_text(feedback_value):
                    if feedback_value in self.feedback_static_text:
                        self.recommendation_label.config(text=self.feedback_static_text[feedback_value])
                    else:
                        self.recommendation_label.config(text="")

                if 'feedback' in selected_record_preview and selected_record_preview['feedback']:
                    record_feedback(selected_record_preview['feedback'])

                if not self.openai_client:
                    try:
                        self.openai_client = OpenAI(api_key="sk-qydfmsqjvccqxrcijqenzwugckjrrtdttyfgvfmewdslvpmr", base_url="https://api.siliconflow.cn/v1")
                    except Exception as e:
                        messagebox.showerror("API 初始化错误", f"OpenAI API 初始化失败: {e}")
                        self.ai_analysis_text = tk.Text(detail_window, height=5, width=60, wrap=tk.WORD)
                        self.ai_analysis_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
                        self.ai_analysis_text.insert(tk.END, "OpenAI API 初始化失败，无法进行AI分析。请检查 API Key 和网络连接。\n")
                        self.ai_analysis_text.config(state=tk.DISABLED)
                        return

                self.ai_analysis_text = tk.Text(detail_window, height=10, width=60, wrap=tk.WORD)
                self.ai_analysis_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True,after=self.recommendation_label)
                self.ai_analysis_text.insert(tk.END, "正在分析中，请稍候...\n")
                self.ai_analysis_text.config(state=tk.DISABLED)

                #  [修改 9.1]  将 CSV 数据转换为字符串
                csv_data_string = ""
                for row in exercise_data:
                    csv_data_string += ",".join(map(str, row)) + "\n" # 每行数据用逗号分隔，行之间用换行符分隔


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
输出的语气需要元气满满的
最后为用户给出一句加油的话语
请输出纯text文本
不要分段

请使用中文生成 150 字左右的详细分析报告。
                """

                def call_openai_api(prompt):
                    try:
                        response = self.openai_client.chat.completions.create(
                            model='Qwen/Qwen2.5-7B-Instruct',
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


    def open_settings_window(self): #  [修改 11.4]  打开设置窗口的函数
        SettingsWindow(self)


#  [修改 11.5]  创建 SettingsWindow 类
class SettingsWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("设置")
        self.master_app = master #  保存主应用实例，方便访问主应用的数据

        tk.Label(self, text="默认圈程距离 (米):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.default_distance_entry = tk.Entry(self)
        self.default_distance_entry.grid(row=0, column=1, padx=10, pady=5)
        self.default_distance_entry.insert(0, str(TreadmillApp.DEFAULT_LAP_DISTANCE)) #  设置默认值

        save_button = tk.Button(self, text="保存设置", command=self.save_settings)
        save_button.grid(row=1, column=0, columnspan=2, pady=10)

    def save_settings(self): #  [修改 11.6]  保存设置的函数
        try:
            new_default_distance = int(self.default_distance_entry.get())
            if new_default_distance > 0:
                TreadmillApp.DEFAULT_LAP_DISTANCE = new_default_distance #  更新类变量
                self.master_app.distance_entry.delete(0, tk.END) #  更新主界面 distance_entry 的值
                self.master_app.distance_entry.insert(0, str(TreadmillApp.DEFAULT_LAP_DISTANCE))
                messagebox.showinfo("设置已保存", "默认圈程距离已保存。")
            else:
                messagebox.showerror("输入错误", "圈程距离必须是正整数。")
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的整数作为圈程距离。")



if __name__ == "__main__":
    collector = HeartRateCollector()
    app = TreadmillApp(collector)
    app.mainloop()
