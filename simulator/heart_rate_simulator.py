"""
heart_rate_simulator.py
Heart Rate Simulation Module
==============================
This module provides a simulator for heart rate data. It is designed to generate
realistic heart rate readings within a specified range and feed them to a
HeartRateCollector. This simulation is useful for testing and development
purposes when a real heart rate sensor is not available.
The module includes the HeartRateSimulator class, which allows setting a heart
rate range, starting and stopping the simulation, and generating random heart
rate values within that range at one-second intervals. The simulator notifies
a HeartRateCollector instance with each generated heart rate reading.
Author: Gaopeng Huang; Hui Guo
Email: perished_hgp@163.com; gh1848026781@163.com
Date Created: 2025-03-06
Last Modified: 2025-03-17
Copyright (c) 2025 PeakVision
All rights reserved.
This software is released under the GNU GENERAL PUBLIC LICENSE, see LICENSE for more information.
"""


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
        self.collector._notify_listeners(0)
        
    def _simulate(self):
        while self.running and self.rate_range:
            self.rate = random.randint(self.rate_range[0], self.rate_range[1])
            self.collector._notify_listeners(self.rate)
            time.sleep(1)

    def get_rate(self):
        return self.rate