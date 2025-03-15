import threading
import time

class HeartRateCollector:
    def __init__(self):
        self.heart_rates = []
        self.listeners = []
        self.running = False
        self.thread = None

    def start_collection(self):
        """启动心率收集线程"""
        if not self.running:
            self.running = True

    def stop_collection(self):
        """停止心率收集线程"""
        if self.running:
            self.running = False

    def _notify_listeners(self, heart_rate):
        """通知所有监听器"""
        self.heart_rates.append(heart_rate)
        for listener in self.listeners:
            listener.on_heart_rate_received(heart_rate)

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

class HeartRateListener:
    """心率监听器接口"""
    def on_heart_rate_received(self, heart_rate):
        """心率数据接收回调"""
        pass