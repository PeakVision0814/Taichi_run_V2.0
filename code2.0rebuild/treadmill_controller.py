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
    def __init__(self, treadmill_simulator, level_var, distance_entry,
                current_speed_label, distance_label, lap_label):
        self.simulator = treadmill_simulator
        self.level_var = level_var
        self.distance_entry = distance_entry
        self.current_speed_label = current_speed_label
        self.distance_label = distance_label
        self.lap_label = lap_label

        self.speed_levels = []
        self.current_speed_index = 0
        self.lap_distance = 0
        self.laps_completed = 0
        self.speed_update_interval = 1
        self.is_running = False
        self.last_distance = 0 
        self.update_speed_after_lap_thread = None
        self.lock = threading.Lock()

    def start_exercise(self):
        if self.is_running:
            return False

        level = self._get_selected_level()
        if level is None:
            return False 

        distance_per_lap = self._get_lap_distance()
        if distance_per_lap is None:
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
                with self.lock: 
                    self.laps_completed += 1
                    self.last_distance = current_distance 
                    self.current_speed_index += 1
                    if self.current_speed_index < len(self.speed_levels):
                        new_speed = self.speed_levels[self.current_speed_index]
                        self.simulator.set_speed(new_speed)
                        print(f"完成圈程 {self.laps_completed}, 速度调整为 {new_speed} km/h") 
                    else:
                        print("速度列表已结束，保持当前速度。")
                        self.is_running = False 
            self._schedule_ui_update()

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
