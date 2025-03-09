"""
treadmill_simulator.py
Treadmill Simulator Module
==========================
This module provides a treadmill simulation with speed control and distance tracking capabilities.
Author: Gaopeng Huang; Hui Guo
Email: perished_hgp@163.com; gh1848026781@163.com
Date Created: 2025-03-06
Last Modified: 2025-03-06
Copyright (c) 2025 PeakVision Technologies
All rights reserved.
This software is released under the GNU GENERAL PUBLIC LICENSE, see LICENSE for more information.
"""

import threading
import time

class TreadmillSimulator:
    def __init__(
            self, 
            initial_speed=0.0
            ):
        self.current_speed = self._validate_initial_speed(initial_speed)
        self.distance_covered = 0.0
        self.start_time = None
        self.running = False
        self.lock = threading.Lock()

    def _validate_initial_speed(self,speed):
        self._check_speed_type(speed)
        self._check_speed_value(speed)
        return speed

    def _check_speed_type(self,speed):
        if not isinstance(speed,(int,float)):
            raise TypeError("Speed must be an integer or a float.")

    def _check_speed_value(self,speed):
        if speed < 0:
            raise ValueError("Speed must be a non-negative number.")

    def start(self):
        self.running = True
        self.start_time = self._get_current_time()
        self._start_thread()

    def _start_thread(self):
        thread = threading.Thread(target=self._run)
        thread.start()

    def stop(self):
        self.running = False

    def set_speed(self,speed):
        self._validate_speed(speed)
        self._set_current_speed(speed)

    def _validate_speed(self,speed):
        self._check_speed_type(speed)
        self._check_speed_value(speed)

    def _set_current_speed(self,speed):
        with self.lock:
            self.current_speed = speed

    def _run(self):
        last_time = self._get_current_time()
        while self.running:
            self._update_distance_covered(last_time)
            last_time = self._get_current_time()
            self._sleep_one_second()

    def _update_distance_covered(self,last_time):
        with self.lock:
            current_time = self._get_current_time()
            elapsed_time = self._calculate_elapsed_time(last_time,current_time)
            self.distance_covered += self._calculate_distance(elapsed_time)

    def _calculate_elapsed_time(self,last_time,current_time):
        return current_time - last_time

    def _calculate_distance(self, elapsed_time):
        """
        根据速度和经过时间计算跑过的距离（米）。

        参数:
            elapsed_time (float): 经过的时间 (秒)。

        返回值:
            float: 跑过的距离 (米)。
        """
        return self.current_speed * elapsed_time * (1000.0 / 3600.0)

    # def _convert_hours_to_seconds(self, elapsed_time):
    #     return (self.current_speed * 1000) * (elapsed_time / 3600)

    def get_elapsed_time(self):
        return self._calculate_elapsed_time_since_start() if self.start_time else 0

    def _calculate_elapsed_time_since_start(self):
        return self._get_current_time() - self.start_time

    def get_current_speed(self):
        return self._get_value_with_lock(self.current_speed)

    def get_distance_covered(self):
        return self._get_value_with_lock(self.distance_covered)

    def _get_value_with_lock(self,value):
        with self.lock:
            return value

    def _get_current_time(self):
        return time.time()

    def _sleep_one_second(self):
        time.sleep(1)