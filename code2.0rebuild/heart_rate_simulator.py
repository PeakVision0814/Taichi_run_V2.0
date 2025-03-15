import random
import time
import threading

class HeartRateSimulator:
    def __init__(self, collector):
        self.running = False
        self.rate_range = None
        self.rate = 0
        self.collector = collector

    def set_rate_range(self, rate_range):
        self.rate_range = rate_range

    def start(self):
        self.running = True
        threading.Thread(target=self._simulate).start()

    def stop(self):
        self.running = False
        self.rate = 0
        self.collector._notify_listeners(0)  # 在停止时显式发送心率 0

    def _simulate(self):
        while self.running and self.rate_range:
            self.rate = random.randint(self.rate_range[0], self.rate_range[1])
            # print(f"心率: {self.rate} bpm")
            self.collector._notify_listeners(self.rate)
            time.sleep(1)

    def get_rate(self):
        return self.rate