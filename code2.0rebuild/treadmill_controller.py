# treadmill_controller.py
import time
import threading
from tkinter import messagebox

SPEED_LEVELS = {
    2: [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.3, 5.6, 5.9, 6.2, 6.5, 6.8, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0, 3.5],
    3: [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5],
    4: [4.0, 4.5, 5.0, 5.5, 6.0, 6.3, 7.0, 7.3, 7.6, 7.9, 8.2, 8.5, 8.8, 9.1, 9.4, 9.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.5],
    5: [5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.3, 8.6, 8.9, 9.2, 9.5, 9.8, 10.1, 10.4, 10.7, 10.5, 10.0, 9.5, 9.0, 8.5, 8.0, 7.5, 7.0, 6.5],
    6: [6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.3, 9.6, 9.9, 10.2, 10.5, 10.8, 11.1, 11.4, 11.7, 12.1, 11.5, 11.0, 10.5, 10.0, 9.5, 9.0, 8.5, 8.0, 7.5],
    7: [7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.3, 10.6, 10.9, 11.2, 11.5, 11.8, 12.1, 12.4, 12.7, 13.0, 12.5, 12.0, 11.5, 11.0, 10.5, 10.0, 9.5, 9.0, 8.5],
    8: [8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.3, 11.6, 11.9, 12.2, 12.5, 12.8, 13.1, 13.4, 13.7, 14.0, 13.5, 13.0, 12.5, 12.0, 11.5, 11.0, 10.5, 10.0, 9.5, 9.0],
    9: [9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.3, 12.6, 12.9, 13.2, 13.5, 13.8, 14.1, 14.4, 14.7, 15.0, 14.5, 14.0, 13.5, 13.0, 12.5, 12.0, 11.5, 11.0, 10.5, 10.0],
    10: [10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.3, 13.6, 13.9, 14.2, 14.5, 14.8, 15.1, 15.4, 15.7, 16.0, 15.5, 15.0, 14.5, 14.0, 13.5, 13.0, 12.5, 12.0, 11.5, 11.0]
}

def get_speed_levels(level):
    if level not in SPEED_LEVELS:
        raise ValueError(f"Invalid level {level}. Valid levels are {list(SPEED_LEVELS.keys())}.")
    return SPEED_LEVELS[level]

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
                age_entry):
        self.simulator = treadmill_simulator
        self.level_var = level_var
        self.distance_entry = distance_entry
        self.current_speed_label = current_speed_label
        self.distance_label = distance_label
        self.lap_label = lap_label
        self.age_entry = age_entry  #  <---  [修改 in treadmill_controller.py] Store age_entry

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

        self.max_heart_rate = 0 #  <---  [修改 in treadmill_controller.py] Initialize max_heart_rate
        self.heart_rate_threshold = 0 #  <---  [修改 in treadmill_controller.py] Initialize heart_rate_threshold
        self.is_heart_rate_exceeded = False #  <---  [修改 in treadmill_controller.py] Initialize is_heart_rate_exceeded
        self.reduction_counter = 0 #  <---  [修改 in treadmill_controller.py] Initialize reduction_counter
        self.reduction_stage = "small" #  <---  [修改 in treadmill_controller.py] Initialize reduction_stage


    def start_exercise(self):
        if self.is_running:
            return False

        level = self._get_selected_level()
        if level is None:
            return False 

        distance_per_lap = self._get_lap_distance()
        if distance_per_lap is None:
            return False
        
        age_str = self.age_entry.get() #  <---  [修改 in treadmill_controller.py] Get age from entry
        if not age_str:
            messagebox.showerror("错误", "请输入年龄。")
            return False
        try:
            age = int(age_str)
            if age <= 0:
                messagebox.showerror("错误", "年龄必须是正整数。")
                return False
            self.max_heart_rate = 220 - age #  <---  [修改 in treadmill_controller.py] Calculate max heart rate
            self.heart_rate_threshold = self.max_heart_rate * 0.8 #  <---  [修改 in treadmill_controller.py] Calculate heart rate threshold
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
        self.is_heart_rate_exceeded = False #  <---  [修改 in treadmill_controller.py] Reset heart rate exceeded flag
        self.reduction_counter = 0 #  <---  [修改 in treadmill_controller.py] Reset reduction counter
        self.reduction_stage = "small" #  <---  [修改 in treadmill_controller.py] Reset reduction stage



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
            if self.update_speed_after_lap_thread and self.update_speed_after_lap_thread.is_alive():
                self.update_speed_after_lap_thread.join(timeout=1) 
            self._update_ui_labels()

    def _start_speed_update_thread(self):
        self.update_speed_after_lap_thread = threading.Thread(target=self._update_speed_after_lap, daemon=True) 
        self.update_speed_after_lap_thread.start()

    def _update_speed_after_lap(self):
        while self.is_running:
            time.sleep(self.speed_update_interval)
            current_distance = self.simulator.get_distance_covered()
            distance_since_last_update = current_distance - self.last_distance
            if distance_since_last_update >= self.lap_distance:
                lap_average_heart_rate = self.heart_rate_collector.get_lap_average_heart_rate() #  <---  [修改 in treadmill_controller.py] Get lap average heart rate

                with self.lock:
                    self.laps_completed += 1
                    self.last_distance = current_distance
                    self.heart_rate_collector.start_new_lap() #  <---  在圈程完成后，通知 HeartRateCollector 开始新圈程
                    if lap_average_heart_rate > self.heart_rate_threshold and not self.is_heart_rate_exceeded:
                        self.is_heart_rate_exceeded = True
                        print(f"本圈平均心率 {lap_average_heart_rate:.1f} bpm 超出阈值 {self.heart_rate_threshold:.1f} bpm，下一圈程开始降速")
                    if self.is_heart_rate_exceeded: # Speed reduction logic if heart rate exceeded
                        current_speed = self.simulator.get_current_speed()
                        if self.reduction_counter < 3: # "小降速" 3次
                            new_speed = max(current_speed - 0.3, 3.5) # 减速0.3，最低3.5km/h
                            self.reduction_counter += 1
                            reduction_type = "小降速"
                        else: # "大降速"
                            new_speed = max(current_speed - 0.5, 3.5) # 减速0.5，最低3.5km/h
                            reduction_type = "大降速"
                        if new_speed < 3.5: # 低于3.5km/h停止
                            new_speed = 0.0
                            self.is_running = False
                            self._exercise_completed()
                            print(f"{reduction_type}, 速度降至低于3.5km/h，运动停止。")
                        else:
                            self.simulator.set_speed(new_speed)
                            print(f"完成圈程 {self.laps_completed}, {reduction_type} 速度调整为 {new_speed} km/h，本圈平均心率{lap_average_heart_rate:.1f}bpm，阈值{self.heart_rate_threshold:.1f}bpm")
                    else: # Normal speed progression if heart rate not exceeded
                        self.current_speed_index += 1
                        if self.current_speed_index < len(self.speed_levels):
                            new_speed = self.speed_levels[self.current_speed_index]
                            self.simulator.set_speed(new_speed)
                            print(f"完成圈程 {self.laps_completed}, 速度调整为 {new_speed} km/h, 本圈平均心率{lap_average_heart_rate:.1f}bpm，阈值{self.heart_rate_threshold:.1f}bpm")
                        else:
                            print("速度列表已结束，停止运动。")
                            self.is_running = False
                            self._exercise_completed()
            self._schedule_ui_update()

            #         self.current_speed_index += 1
            #         if self.current_speed_index < len(self.speed_levels):
            #             new_speed = self.speed_levels[self.current_speed_index]
            #             self.simulator.set_speed(new_speed)
            #             print(f"完成圈程 {self.laps_completed}, 速度调整为 {new_speed} km/h")
            #         else:
            #             print("速度列表已结束，停止运动。")
            #             self.is_running = False
            #             self._exercise_completed()
            # self._schedule_ui_update()

    def _exercise_completed(self):
        level = self._get_selected_level()
        if level:
            message = f"等级{level}运动已完成！"
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
        else:
            current_speed = self.simulator.get_current_speed()
            current_speed_text = f"{current_speed:.1f} km/h"

        distance_covered = self.simulator.get_distance_covered()
        distance_text = f"{distance_covered:.2f} 米"
        lap_text = f"{self.laps_completed} 圈"

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
