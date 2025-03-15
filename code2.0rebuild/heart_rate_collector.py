# heart_rate_collector.py
import threading
import time

class HeartRateCollector:
    def __init__(self):
        self.heart_rates = []
        self.listeners = []
        self.running = False
        self.thread = None

        self.current_lap_heart_rates = []
        self.last_lap_average_rate = 0
        self.latest_heart_rate = 0
        self.session_start_time = 0  # 初始化 session_start_time
        self.current_session_data = []  #  <--- [修改 1] 初始化 current_session_data 列表

    def start_collection(self):
        if not self.running:
            self.running = True
        self.current_session_data = [] #  <--- [修改 2]  在开始收集时清空会话数据
        self.session_start_time = time.time()  # 记录会话开始时间

    def stop_collection(self):
        if self.running:
            self.running = False

    def _notify_listeners(self, heart_rate):
        current_timestamp  = time.time()  #  <--- [修改 3] 获取当前时间戳
        relative_timestamp = current_timestamp - self.session_start_time  # 计算相对时间戳
        self.heart_rates.append(heart_rate)
        self.current_lap_heart_rates.append(heart_rate)
        self.latest_heart_rate = heart_rate
        self.current_session_data.append((relative_timestamp, heart_rate)) #  <--- [修改 4] 存储 (时间戳, 心率) 元组
        for listener in self.listeners:
            listener.on_heart_rate_received(heart_rate, self.get_average_heart_rate(), self.get_lap_average_heart_rate(), self.last_lap_average_rate)

    def add_listener(self, listener):
        self.listeners.append(listener)

    def remove_listener(self, listener):
        if listener in self.listeners:
            self.listeners.remove(listener)

    def get_all_heart_rates(self):
        return self.heart_rates[:]

    def get_average_heart_rate(self):
        if not self.heart_rates:
            return 0
        return sum(self.heart_rates) / len(self.heart_rates)

    def get_lap_average_heart_rate(self):
        if not self.current_lap_heart_rates:
            return 0
        return sum(self.current_lap_heart_rates) / len(self.current_lap_heart_rates)

    def start_new_lap(self):
        current_lap_avg = self.get_lap_average_heart_rate()
        if self.current_lap_heart_rates:
            self.last_lap_average_rate = current_lap_avg
        self.current_lap_heart_rates = []

    def get_current_heart_rate(self):
        return self.latest_heart_rate

    def get_session_data(self):
        """获取当前运动会话的心率和时间戳数据""" #  <--- [修改 5] 添加 get_session_data 方法
        return self.current_session_data[:]


class HeartRateListener:
    def on_heart_rate_received(self, heart_rate, average_heart_rate, lap_average_heart_rate, last_lap_average_rate):
        pass
