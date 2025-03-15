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
        """
        初始化跑步机控制器。

        Args:
            treadmill_simulator: TreadmillSimulator 实例。
            level_var: tkinter.StringVar 实例，用于获取选择的等级。
            distance_entry: tkinter.Entry 实例，用于获取圈程距离。
            current_speed_label: tkinter.Label 实例，用于显示当前速度。
            distance_label: tkinter.Label 实例，用于显示运动距离。
            lap_label: tkinter.Label 实例，用于显示当前圈程。
        """
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
        self.speed_update_interval = 1 # 秒，速度更新间隔
        self.is_running = False
        self.last_distance = 0 # 上一次更新速度时的距离
        self.update_speed_after_lap_thread = None # 用于速度更新的线程
        self.lock = threading.Lock() # 用于线程同步

    def start_exercise(self):
        """启动跑步机运动。"""
        if self.is_running:
            return False # 避免重复启动

        level = self._get_selected_level()
        if level is None:
            return False # 如果等级无效，则不启动

        distance_per_lap = self._get_lap_distance()
        if distance_per_lap is None:
            return False # 如果圈程距离无效，则不启动

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
        self._update_ui_labels() # 立即更新UI
        self._start_speed_update_thread() # 启动速度更新线程
        return True

    def stop_exercise(self):
        """停止跑步机运动。"""
        if self.is_running:
            self.is_running = False
            self.simulator.stop()
            if self.update_speed_after_lap_thread and self.update_speed_after_lap_thread.is_alive():
                self.update_speed_after_lap_thread.join(timeout=1) # 等待线程结束，设置超时时间防止阻塞
            self._update_ui_labels() # 最后一次更新UI

    def _start_speed_update_thread(self):
        """启动一个线程来定期检查距离并更新速度。"""
        self.update_speed_after_lap_thread = threading.Thread(target=self._update_speed_after_lap, daemon=True) # 设置为守护线程
        self.update_speed_after_lap_thread.start()

    def _update_speed_after_lap(self):
        """在后台线程中运行，定期检查距离并根据圈程更新速度。"""
        while self.is_running:
            time.sleep(self.speed_update_interval)
            current_distance = self.simulator.get_distance_covered()
            distance_since_last_update = current_distance - self.last_distance

            if distance_since_last_update >= self.lap_distance:
                with self.lock: # 确保线程安全
                    self.laps_completed += 1
                    self.last_distance = current_distance # 更新last_distance为当前距离，而不是 last_distance + lap_distance
                    self.current_speed_index += 1
                    if self.current_speed_index < len(self.speed_levels):
                        new_speed = self.speed_levels[self.current_speed_index]
                        self.simulator.set_speed(new_speed)
                        print(f"完成圈程 {self.laps_completed}, 速度调整为 {new_speed} km/h") # 调试信息
                    else:
                        print("速度列表已结束，保持当前速度。") # 调试信息
                        self.is_running = False # 速度列表结束，停止运动或者保持最后速度，这里选择停止更新速度

            self._update_ui_labels() # 每次循环都更新UI，保证数据实时性

    def _update_ui_labels(self):
        """更新UI上的速度、距离和圈程标签 (需要从主线程调用)。"""
        if not self.is_running:
            current_speed_text = "0.0 km/h"
        else:
            current_speed = self.simulator.get_current_speed()
            current_speed_text = f"{current_speed:.1f} km/h"

        distance_covered = self.simulator.get_distance_covered()
        distance_text = f"{distance_covered:.2f} 米"
        lap_text = f"{self.laps_completed} 圈"

        # 使用 tkinter.Tk.after 将UI更新操作放入主线程队列
        self.current_speed_label.after(0, self.current_speed_label.config, {"text": current_speed_text})
        self.distance_label.after(0, self.distance_label.config, {"text": distance_text})
        self.lap_label.after(0, self.lap_label.config, {"text": lap_text})

        if self.is_running:
            self.current_speed_label.after(100, self._update_ui_labels) # 定期更新，例如每 100 毫秒


    def _get_selected_level(self):
        """获取用户选择的运动等级，并进行校验。"""
        level_str = self.level_var.get()
        if not level_str:
            messagebox.showerror("错误", "请选择运动等级。")
            return None
        if level_str not in [str(l) for l in SPEED_LEVELS.keys()]:
            messagebox.showerror("错误", "选择的运动等级无效。")
            return None
        return level_str

    def _get_lap_distance(self):
        """获取用户输入的圈程距离，并进行校验。"""
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
