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

    def start_collection(self):
        if not self.running:
            self.running = True

    def stop_collection(self):
        if self.running:
            self.running = False

    def _notify_listeners(self, heart_rate):
        self.heart_rates.append(heart_rate) 
        self.current_lap_heart_rates.append(heart_rate) 
        self.latest_heart_rate = heart_rate
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


class HeartRateListener:
    def on_heart_rate_received(self, heart_rate, average_heart_rate, lap_average_heart_rate, last_lap_average_rate):
        pass
