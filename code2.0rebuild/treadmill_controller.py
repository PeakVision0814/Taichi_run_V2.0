# treadmill_controller.py
import time
import threading
from tkinter import messagebox
import datetime 
from exercise_data_manager import save_exercise_data 
from speed_config import SPEED_LEVELS, get_speed_levels

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
        self.exercise_start_time = None #  <--- [修改 1.3] 添加 exercise_start_time 属性


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
            # if self.update_speed_after_lap_thread and self.update_speed_after_lap_thread.is_alive():
                # self.update_speed_after_lap_thread.join(timeout=1)
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
                save_exercise_data(filename, session_data, level, lap_distance, age, exercise_duration_seconds, self.laps_completed) 
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
                            # self.is_running = False
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
                            # self.is_running = False
                            self._exercise_completed()
            self._schedule_ui_update()

    def _exercise_completed(self, reason = None):
        level = self._get_selected_level()
        if reason == "heart_rate_stop":
            message = f"本次等级{level}运动结束，第{self.laps_completed}圈时心率略高，请注意下次调整等级"
        elif level:
            message = f"等级{level}运动已完成！"
        else:
            message = "运动结束！"

        messagebox.showinfo("完成运动", message)
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
            # if distance < 50:
                # messagebox.showerror("错误", "圈程距离必须大于等于50米。")
                # return None
            return distance
        except ValueError:
            messagebox.showerror("错误", "圈程距离必须是数字。")
            return None
