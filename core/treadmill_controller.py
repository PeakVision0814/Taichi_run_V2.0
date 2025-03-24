"""
treadmill_controller.py
Treadmill Exercise Controller Module
====================================
This module implements the control logic for a treadmill exercise simulation.
It manages the exercise flow, speed adjustments based on pre-defined levels and
real-time heart rate monitoring, distance tracking, lap counting, and data persistence.
The module integrates with:
- `TreadmillSimulator`: To control the simulated treadmill speed and distance.
- UI elements (via tkinter): To receive user inputs like exercise level, lap distance, and age,
  and to update UI labels displaying current speed, distance, laps, and post-exercise heart rate.
- `HeartRateCollector`: To receive real-time heart rate data for monitoring and speed adjustments.
- `exercise_data_manager`: To save exercise session data to CSV files for historical records.
Key functionalities include:
- Starting and stopping exercise sessions.
- Setting exercise level and lap distance.
- Dynamically adjusting treadmill speed based on the selected level and heart rate thresholds.
- Tracking distance covered and laps completed.
- Monitoring heart rate and triggering speed reductions if heart rate exceeds a threshold.
- Saving exercise data upon completion, including heart rate data, exercise parameters, and duration.
- Providing feedback to the user through message boxes and UI updates.
Author: Gaopeng Huang; Hui Guo
Email: perished_hgp@163.com; gh1848026781@163.com
Date Created: 2025-03-06
Last Modified: 2025-03-17
Copyright (c) 2025 PeakVision
All rights reserved.
This software is released under the GNU GENERAL PUBLIC LICENSE, see LICENSE for more information.
"""
import time
import tkinter as tk
import threading
from tkinter import messagebox
import datetime
from core.exercise_data_manager import save_exercise_data, update_exercise_data_feedback
from core.speed_config import SPEED_LEVELS, get_speed_levels

class TreadmillController:
    def __init__(self,
                 treadmill_simulator,
                 level_var,
                 distance_entry,
                current_speed_label,
                distance_label,
                lap_label,
                exercise_completion_callback,
                heart_rate_collector,
                age_entry,
                post_exercise_average_rate_label):
        self.simulator = treadmill_simulator
        self.level_var = level_var
        self.distance_entry = distance_entry
        self.current_speed_label = current_speed_label
        self.distance_label = distance_label
        self.lap_label = lap_label
        self.age_entry = age_entry
        self.post_exercise_average_rate_label = post_exercise_average_rate_label

        self.speed_levels = []
        self.current_speed_index = 0
        self.lap_distance = 0
        self.laps_completed = 0
        self.speed_update_interval = 1
        self.is_running = False
        self.last_distance = 0
        self.update_speed_after_lap_thread = None
        self.lock = threading.Lock()
        self.exercise_completion_callback = exercise_completion_callback
        self.heart_rate_collector = heart_rate_collector

        self.max_heart_rate = 0
        self.heart_rate_threshold = 0
        self.is_heart_rate_exceeded = False
        self.reduction_counter = 0
        self.reduction_stage = "small"
        self.post_exercise_heart_rates = []
        self.post_exercise_collection_active = False
        self.exercise_start_time = None
        self.total_distance_meters = 0.0
        self.current_filename = None # 初始化 current_filename


    def start_exercise(self):
        if self.is_running:
            return False

        level = self._get_selected_level()
        if level is None:
            return False

        distance_per_lap = self._get_lap_distance()
        if distance_per_lap is None:
            return False

        age_str = self.age_entry.get()
        if not age_str:
            messagebox.showerror("错误", "请输入年龄。")
            return False
        try:
            age = int(age_str)
            if age <= 0:
                messagebox.showerror("错误", "年龄必须是正整数。")
                return False
            self.max_heart_rate = 220 - age
            self.heart_rate_threshold = self.max_heart_rate * 0.8
        except ValueError:
            messagebox.showerror("错误", "年龄必须是整数。")
            return False


        try:
            self.speed_levels = get_speed_levels(int(level))
        except ValueError as e:
            messagebox.showerror("错误", str(e))
            return False

        if not self.speed_levels:
            messagebox.showerror("错误", "该等级没有预设速度。")
            return False

        self.lap_distance = distance_per_lap
        self.current_speed_index = 0
        self.laps_completed = 0
        self.last_distance = 0
        self.is_running = True
        self.is_heart_rate_exceeded = False
        self.reduction_counter = 0
        self.reduction_stage = "small"
        self.post_exercise_collection_active = False
        self.exercise_start_time = datetime.datetime.now()
        self.total_distance_meters = 0.0 

        timestamp_str = self.exercise_start_time.strftime("%Y%m%d-%H%M%S")
        self.current_filename = f"heart_rate_log_{timestamp_str}.csv" # 生成并保存文件名

        self.simulator.distance_covered = 0.0
        initial_speed = self.speed_levels[0]
        self.simulator.set_speed(initial_speed)
        self.simulator.start()
        self._update_ui_labels()
        self._start_speed_update_thread()
        return True

    def stop_exercise(self):
        if self.is_running:
            self.is_running = False
            self.simulator.stop()
            self._update_ui_labels()
            self._start_post_exercise_heart_rate_collection()

            session_data = self.heart_rate_collector.get_session_data()
            level = self._get_selected_level()
            lap_distance = self._get_lap_distance()
            age_str = self.age_entry.get()
            age = int(age_str) if age_str else 0
            exercise_duration_seconds = 0
            if self.exercise_start_time:
                exercise_end_time = datetime.datetime.now()
                exercise_duration_seconds = int((exercise_end_time - self.exercise_start_time).total_seconds())

            if session_data:
                timestamp_str = self.exercise_start_time.strftime("%Y%m%d-%H%M%S")
                filename = f"heart_rate_log_{timestamp_str}.csv"
                save_exercise_data(filename, session_data, level, lap_distance, age, exercise_duration_seconds, self.laps_completed, self.total_distance_meters) 
                print(f"运动数据已保存到: {filename}")
            else:
                print("没有心率数据需要保存。")


    def _start_post_exercise_heart_rate_collection(self):
        self.post_exercise_heart_rates = []
        self.post_exercise_collection_active = True
        self._collect_post_exercise_heart_rate(60)

    def _collect_post_exercise_heart_rate(self, seconds_left):
        if not self.post_exercise_collection_active:
            return

        current_heart_rate = self.heart_rate_collector.get_current_heart_rate()
        if current_heart_rate is not None:
            self.post_exercise_heart_rates.append(current_heart_rate)

        if self.post_exercise_heart_rates:
            average_post_exercise_heart_rate = sum(self.post_exercise_heart_rates) / len(self.post_exercise_heart_rates)
            self.post_exercise_average_rate_label.config(text=f"{average_post_exercise_heart_rate:.1f} bpm")
        else:
            self.post_exercise_average_rate_label.config(text="等待心率数据...")


        if seconds_left > 0:
            self.post_exercise_average_rate_label.after(1000, self._collect_post_exercise_heart_rate, seconds_left - 1)
        else:
            self.post_exercise_collection_active = False
            if self.post_exercise_heart_rates:
                average_post_exercise_heart_rate = sum(self.post_exercise_heart_rates) / len(self.post_exercise_heart_rates)
                self.post_exercise_average_rate_label.config(text=f"{average_post_exercise_heart_rate:.1f} bpm")
            else:
                self.post_exercise_average_rate_label.config(text="无法获取心率数据")


    def _start_speed_update_thread(self):
        self.update_speed_after_lap_thread = threading.Thread(target=self._update_speed_after_lap, daemon=True)
        self.update_speed_after_lap_thread.start()

    def _update_speed_after_lap(self):
        while self.is_running:
            time.sleep(self.speed_update_interval)
            current_distance = self.simulator.get_distance_covered()
            distance_since_last_update = current_distance - self.last_distance
            if distance_since_last_update >= self.lap_distance:
                lap_average_heart_rate = self.heart_rate_collector.get_lap_average_heart_rate()

                with self.lock:
                    self.laps_completed += 1
                    self.last_distance = current_distance
                    self.heart_rate_collector.start_new_lap()
                    if lap_average_heart_rate > self.heart_rate_threshold and not self.is_heart_rate_exceeded:
                        self.is_heart_rate_exceeded = True
                        print(f"本圈平均心率 {lap_average_heart_rate:.1f} bpm 超出阈值 {self.heart_rate_threshold:.1f} bpm，下一圈程开始降速")
                    if self.is_heart_rate_exceeded:
                        current_speed = self.simulator.get_current_speed()
                        if self.reduction_counter < 3:
                            new_speed = current_speed - 0.3
                            self.reduction_counter += 1
                            reduction_type = "小降速"
                        else:
                            new_speed = current_speed - 0.5
                            reduction_type = "大降速"
                        if new_speed < 3.5:
                            new_speed = 0.0
                            self._exercise_completed(reason="heart_rate_stop")
                            print(f"{reduction_type}, 速度降至低于3.5km/h，运动停止。")
                        else:
                            self.simulator.set_speed(new_speed)
                            print(f"完成圈程 {self.laps_completed}, {reduction_type} 速度调整为 {new_speed} km/h，本圈平均心率{lap_average_heart_rate:.1f}bpm，阈值{self.heart_rate_threshold:.1f}bpm")
                    else:
                        self.current_speed_index += 1
                        if self.current_speed_index < len(self.speed_levels):
                            new_speed = self.speed_levels[self.current_speed_index]
                            self.simulator.set_speed(new_speed)
                            print(f"完成圈程 {self.laps_completed}, 速度调整为 {new_speed} km/h, 本圈平均心率{lap_average_heart_rate:.1f}bpm，阈值{self.heart_rate_threshold:.1f}bpm")
                        else:
                            print("速度列表已结束，停止运动。")
                            self._exercise_completed()
            self._update_distance_label()
            self._schedule_ui_update()


    def _update_distance_label(self): 
        if self.is_running:
            distance_covered = self.simulator.get_distance_covered()
            self.total_distance_meters = distance_covered 
            distance_text = f"{distance_covered:.2f} 米"
            self.distance_label.after(0, self.distance_label.config, {"text": distance_text})


    def _exercise_completed(self, reason = None):
        level = self._get_selected_level()
        if reason == "heart_rate_stop":
            message = f"本次等级{level}运动结束，运动距离{self.total_distance_meters:.2f}米，因心率超过阈值停止，共完成{self.laps_completed}圈，平均心率{self.heart_rate_collector.get_average_heart_rate():.1f}bpm，最高心率{max(self.heart_rate_collector.get_all_heart_rates())}bpm。\n\n心率过高，建议适当减少运动强度喔。"
        elif level:
            message = f"等级{level}运动已完成，运动距离{self.total_distance_meters:.2f}米，共完成{self.laps_completed}圈，平均心率{self.heart_rate_collector.get_average_heart_rate():.1f}bpm，最高心率{max(self.heart_rate_collector.get_all_heart_rates())}bpm。\n\n运动强度达标，状态良好，继续保持！！"
        else:
            message = "运动结束！"

        completion_window = tk.Toplevel()
        completion_window.title("完成运动")

        message_label = tk.Label(completion_window, text=message, padx=20, pady=10)
        message_label.pack()

        feedback_frame = tk.Frame(completion_window)
        feedback_frame.pack(pady=10)

        feedback_labels = ["过于轻松", "舒适", "一般", "难受", "难以承受"]

        def record_feedback(feedback_value):
            if self.current_filename:
                update_exercise_data_feedback(self.current_filename, feedback_value) 
                print(f"反馈 '{feedback_value}' 已保存到文件: {self.current_filename}")
            else:
                print("错误: 无法获取当前文件名，反馈未保存。")
            completion_window.destroy()

        for i, label_text in enumerate(feedback_labels):
            btn = tk.Button(feedback_frame, text=label_text, command=lambda text=label_text: record_feedback(text)) 
            btn.pack(side=tk.LEFT, padx=5)


        self.stop_exercise()
        if self.exercise_completion_callback:
            self.exercise_completion_callback()



    def _close_completion_window(self, window):
        """关闭运动完成窗口并执行停止运动后的操作"""
        window.destroy()
        self.stop_exercise()
        if self.exercise_completion_callback:
            self.exercise_completion_callback()



    def _schedule_ui_update(self):
        if self.is_running:
            self.current_speed_label.after(0, self._update_ui_labels)


    def _update_ui_labels(self):
        if not self.is_running:
            current_speed_text = "0.0 km/h"
            if not self.post_exercise_collection_active:
                self.post_exercise_average_rate_label.config(text="等待运动停止...")
        else:
            current_speed = self.simulator.get_current_speed()
            current_speed_text = f"{current_speed:.1f} km/h"

        distance_covered = self.simulator.get_distance_covered()
        distance_text = f"{distance_covered:.2f} 米"

        if self.lap_distance > 0:
            current_lap_float = distance_covered / self.lap_distance
            lap_text = f"{int(current_lap_float)} 圈"
        else:
            lap_text = "0 圈"

        self.current_speed_label.after(0, self.current_speed_label.config, {"text": current_speed_text})
        self.distance_label.after(0, self.distance_label.config, {"text": distance_text})
        self.lap_label.after(0, self.lap_label.config, {"text": lap_text})


    def _get_selected_level(self):
        level_str = self.level_var.get()
        if not level_str:
            messagebox.showerror("错误", "请选择运动等级。")
            return None
        if level_str not in [str(l) for l in SPEED_LEVELS.keys()]:
            messagebox.showerror("错误", "选择的运动等级无效。")
            return None
        return level_str

    def _get_lap_distance(self):
        distance_str = self.distance_entry.get()
        if not distance_str:
            messagebox.showerror("错误", "请输入圈程距离。")
            return None
        try:
            distance = float(distance_str)
            if distance <= 0:
                messagebox.showerror("错误", "圈程距离必须是正数。")
                return None
            return distance
        except ValueError:
            messagebox.showerror("错误", "圈程距离必须是数字。")
            return None
