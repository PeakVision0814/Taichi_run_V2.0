"""
heart_rate_collector.py
Heart Rate Data Collection Module
=================================
This module is responsible for collecting and managing heart rate data.
It provides classes to simulate a heart rate collector and a listener interface
to receive heart rate updates. The module supports starting and stopping data
collection, calculating average heart rates (overall and per lap), and notifying
registered listeners of new heart rate readings.
Author: Gaopeng Huang; Hui Guo
Email: perished_hgp@163.com; gh1848026781@163.com
Date Created: 2025-03-06
Last Modified: 2025-03-17
Copyright (c) 2025 PeakVision
All rights reserved.
This software is released under the GNU GENERAL PUBLIC LICENSE, see LICENSE for more information.
"""

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
        self.session_start_time = 0 
        self.current_session_data = []  

    def start_collection(self):
        if not self.running:
            self.running = True
        self.current_session_data = [] 
        self.session_start_time = time.time() 

    def stop_collection(self):
        if self.running:
            self.running = False

    def _notify_listeners(self, heart_rate):
        current_timestamp  = time.time() 
        relative_timestamp = current_timestamp - self.session_start_time  
        self.heart_rates.append(heart_rate)
        self.current_lap_heart_rates.append(heart_rate)
        self.latest_heart_rate = heart_rate
        self.current_session_data.append((relative_timestamp, heart_rate)) 
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
        return self.current_session_data[:]


class HeartRateListener:
    def on_heart_rate_received(self, heart_rate, average_heart_rate, lap_average_heart_rate, last_lap_average_rate):
        pass
