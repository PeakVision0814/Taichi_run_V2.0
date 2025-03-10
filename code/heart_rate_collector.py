"""
heart_rate_collector.py
Heart Rate Collector Module
==================
This module reads and processes the user's heart rate data.
Author: Gaopeng Huang; Hui Guo
Email: perished_hgp@163.com; gh1848026781@163.com
Date Created: 2025-03-06
Last Modified: 2025-03-09
Copyright (c) 2025 PeakVision
All rights reserved.
This software is released under the GNU GENERAL PUBLIC LICENSE, see LICENSE for more information.
"""

from heart_rate_monitor import HeartRateMonitor

class HeartRateCollector:
    def __init__(self, age):
        self.heart_rate_monitor = HeartRateMonitor(age)  
        self.heart_rate_samples = []
        self.current_lap_heart_rate_samples = [] 
        self.previous_lap_average_heart_rate = 0.0  

    def get_heart_rate(self):
        heart_rate = self.heart_rate_monitor.get_current_heart_rate()
        self.heart_rate_samples.append(heart_rate)
        self.current_lap_heart_rate_samples.append(heart_rate)
        return heart_rate

    def get_average_heart_rate(self):
        if not self.heart_rate_samples:
            return 0 
        return sum(self.heart_rate_samples) / len(self.heart_rate_samples)

    def reset_heart_rate_samples(self):
        self.heart_rate_samples = []

    def start_new_lap(self):
        self.previous_lap_average_heart_rate = self.get_current_lap_average_heart_rate()
        self.current_lap_heart_rate_samples = []

    def get_current_lap_average_heart_rate(self): 
        if not self.current_lap_heart_rate_samples:
            return 0
        return sum(self.current_lap_heart_rate_samples) / len(self.current_lap_heart_rate_samples)
    
    def get_previous_lap_average_heart_rate(self):
        return self.previous_lap_average_heart_rate