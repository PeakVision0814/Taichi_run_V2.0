import threading
import time

class HeartRateCollector:
    def __init__(self):
        self.heart_rates = [] # 存储所有心率数据
        self.listeners = []
        self.running = False
        self.thread = None

        self.current_lap_heart_rates = [] # 存储当前圈程的心率数据
        self.last_lap_average_rate = 0 # 上一圈程的平均心率

    def start_collection(self):
        """启动心率收集线程"""
        if not self.running:
            self.running = True

    def stop_collection(self):
        """停止心率收集线程"""
        if self.running:
            self.running = False

    def _notify_listeners(self, heart_rate):
        """通知所有监听器，并存储心率数据"""
        self.heart_rates.append(heart_rate) # 存储所有心率
        self.current_lap_heart_rates.append(heart_rate) # 存储当前圈程心率
        for listener in self.listeners:
            listener.on_heart_rate_received(heart_rate, self.get_average_heart_rate(), self.get_lap_average_heart_rate(), self.last_lap_average_rate) # 通知监听器并传递平均心率

    def add_listener(self, listener):
        """添加监听器"""
        self.listeners.append(listener)

    def remove_listener(self, listener):
        """移除监听器"""
        if listener in self.listeners:
            self.listeners.remove(listener)

    def get_all_heart_rates(self):
        """获取所有已收集的心率数据"""
        return self.heart_rates[:]

    def get_average_heart_rate(self):
        """计算所有心率的平均值"""
        if not self.heart_rates:
            return 0
        return sum(self.heart_rates) / len(self.heart_rates)

    def get_lap_average_heart_rate(self):
        """计算当前圈程的平均心率"""
        if not self.current_lap_heart_rates:
            return 0
        return sum(self.current_lap_heart_rates) / len(self.current_lap_heart_rates)

    def start_new_lap(self):
        """开始新的圈程，重置当前圈程心率数据，并将当前圈程平均心率保存为上一圈程平均心率"""
        current_lap_avg = self.get_lap_average_heart_rate()
        if self.current_lap_heart_rates: # 只有当本圈程有心率数据时才更新上一圈程平均心率，避免在开始运动时立即更新为0
            self.last_lap_average_rate = current_lap_avg
        self.current_lap_heart_rates = [] # 清空当前圈程心率列表


class HeartRateListener:
    """心率监听器接口"""
    def on_heart_rate_received(self, heart_rate, average_heart_rate, lap_average_heart_rate, last_lap_average_rate):
        """心率数据接收回调，同时传递平均心率"""
        pass
