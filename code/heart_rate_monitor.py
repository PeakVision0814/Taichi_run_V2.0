"""
Heart Rate Monitor
==================
This module provides a class to simulate and monitor heart rate based on elapsed time and age.
Author: Gaopeng Huang; Hui Guo
Email: perished_hgp@163.com; 
Date Created: 2025-03-06
Last Modified: 2025-03-06
Version: 1.0.0
Copyright (c) 2025 PeakVision
All rights reserved.
This software is released under the GNU GENERAL PUBLIC LICENSE, see LICENSE for more information.
"""

import random
import time

class HeartRateMonitor:
    def __init__(self, age):
        self.start_time = time.time()
        self.age = age
        self._validate_age()
        self.max_heart_rate = self.calculate_max_heart_rate()
        self.heart_rate = self.initialize_heart_rate()
        self.stabilized = False

    def _validate_age(self):
        if not isinstance(self.age, int) or self.age <= 0:
            raise ValueError("Age must be a positive integer.")

    def calculate_max_heart_rate(self):
        return 220 - self.age

    def initialize_heart_rate(self):
        return random.randint(60, 100)

    def get_current_heart_rate(self):
        self.heart_rate = self._get_heart_rate_from_device()
        return self.heart_rate

    def _get_heart_rate_from_device(self):
        elapsed_time = time.time() - self.start_time
        return self._simulate_heart_rate(elapsed_time)

    def _simulate_heart_rate(self, elapsed_time):
        if self.stabilized:
            return random.randint(int(self.max_heart_rate * 0.73), int(self.max_heart_rate * 0.77))
        return self._adjust_heart_rate_based_on_time(elapsed_time)

    def _adjust_heart_rate_based_on_time(self, elapsed_time):
        if elapsed_time > 300:
            return random.randint(145, 200)
        if elapsed_time > 200:
            return random.randint(130, 144)
        if elapsed_time > 100:
            return random.randint(100, 120)
        return random.randint(60, 100)

    def set_stabilized(self, stabilized):
        self.stabilized = stabilized