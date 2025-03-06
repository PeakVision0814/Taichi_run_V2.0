import threading
import time
from treadmill_simulator import TreadmillSimulator
from heart_rate_monitor import HeartRateMonitor
from speed_levels import SPEED_LEVELS  # 导入 SPEED_LEVELS

class TreadmillController:
    def __init__(
            self,
            age,
            level,
            target_distance=None,
            max_time=None,
            target_heart_rate=None, 
            update_callback=None, 
            goal_reached_callback=None
            ):
        self.treadmill = TreadmillSimulator()
        self.heart_rate_monitor = HeartRateMonitor(
            age
            )
        self.level = level
        self.speed_index = 0
        self.decrease_speed_count = 0
        self.lock = threading.Lock()
        self.control_thread = threading.Thread(
            target=self._control
            )
        self.control_thread.daemon = True
        self.target_distance = target_distance
        self.max_time = max_time
        self.target_heart_rate = target_heart_rate
        self.update_callback = update_callback
        self.goal_reached_callback = goal_reached_callback
        self.running = False
        self.paused = False
        self.start_time = None
        self.elapsed_time_before_pause = 0
        self.decreasing = False
        self.start_decrease = False

    def start(self):
        self.running = True
        self.treadmill.start()
        self.start_time = time.time()
        self.control_thread.start()
        if self.update_callback:
            self.update_callback("跑步机已启动。")

    def stop(self):
        self.running = False
        self.treadmill.stop()
        if self.update_callback:
            self.update_callback("跑步机已停止。")
        if self.goal_reached_callback:
            self.goal_reached_callback()

    def pause(self):
        self.running = False
        self.paused = True
        self.treadmill.stop()
        self.elapsed_time_before_pause += time.time() - self.start_time
        if self.update_callback:
            self.update_callback("跑步机已暂停。")

    def resume(
            self
            ):
        self.running = True
        self.paused = False
        self.treadmill.start()
        self.start_time = time.time()
        self.control_thread = threading.Thread(
            target=self._control
            )
        self.control_thread.daemon = True
        self.control_thread.start()

    def set_speed(
            self,
            speed
            ):
        self.treadmill.set_speed(
            speed
            )

    def _control(
            self
            ):
        circle_distance = 200
        initial_distance = self.treadmill.get_distance_covered()
        while self.running:
            with self.lock:
                if self.start_decrease:
                    if self.treadmill.get_current_speed() > 3.5:
                        if self.decrease_speed_count < 3:
                            speed_decrease = 0.3
                        else:
                            speed_decrease = 0.5
                        new_speed = max(self.treadmill.get_current_speed() - speed_decrease, 3.5)
                        self.set_speed(new_speed)
                        self.decrease_speed_count += 1
                    else:
                        self.stop()
                        return
                elif self.speed_index < len(
                    SPEED_LEVELS
                    [
                        self.level
                        ]
                        ):
                    speed = SPEED_LEVELS[self.level][self.speed_index]
                    self.set_speed(speed)
                else:
                    self.stop()
                    return

            start_distance = self.treadmill.get_distance_covered()
            while self.treadmill.get_distance_covered() - start_distance < circle_distance and self.running:
                heart_rate = self.heart_rate_monitor.get_current_heart_rate()
                current_speed = self.treadmill.get_current_speed()

                if self.update_callback:
                    self.update_callback(
                        f"当前心率: {heart_rate} bpm"
                        )

                elapsed_time = self.elapsed_time_before_pause + (
                    time.time() - self.start_time
                    )
                distance_covered = self.treadmill.get_distance_covered()

                if (
                    (
                        self.target_distance is not None and 
                    self.treadmill.get_distance_covered() - initial_distance >= self.target_distance) or
                        (self.max_time is not None and 
                        elapsed_time >= self.max_time)
                        ):
                    self.pause()
                    if self.goal_reached_callback:
                        self.goal_reached_callback()
                    return

                if self.target_heart_rate is not None and heart_rate >= self.target_heart_rate:
                    self.decreasing = True

                if self.update_callback:
                    self.update_callback(
                        f"当前速度: {current_speed:.1f} km/h, 已跑距离: {distance_covered:.2f} 米, 运行时间: {elapsed_time:.2f} 秒"
                        )

                if heart_rate >= self.heart_rate_monitor.max_heart_rate * 0.8:
                    self.decreasing = True

                time.sleep(1)

            if self.decreasing:
                self.start_decrease = True
                self.decreasing = False

            with self.lock:
                if not self.start_decrease:
                    self.speed_index += 1


if __name__ == "__main__":
    def update_status(message):
        print(message)

    age = int(input("请输入您的年龄: "))
    level = int(input("请输入初始运动等级（2-10）: "))

    target_type = input("请选择目标类型（1: 距离, 2: 时间, 3: 无目标, 4: 心率）: ")
    if target_type == '1':
        target_distance = int
        (input("请输入目标跑步距离（米）: "))
        max_time = None
        target_heart_rate = None
    elif target_type == '2':
        max_time = int(input("请输入目标跑步时间（秒）: "))
        target_distance = None
        target_heart_rate = None
    elif target_type == '3':
        target_distance = None
        max_time = None
        target_heart_rate = None
    elif target_type == '4':
        target_heart_rate = int(input("请输入目标心率（bpm）: "))
        target_distance = None
        max_time = None
    else:
        print("无效的选择")
        exit(1)

    controller = TreadmillController(age, level, target_distance, max_time, target_heart_rate, update_status)
    controller.start()

    try:
        while controller.running:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()
        update_status("跑步机被手动停止。")