"""
heart_rate_collector.py
Heart Rate Collector Module
==================
This module reads and processes the user's heart rate data.
Author: Gaopeng Huang; Hui Guo
Email: perished_hgp@163.com; gh1848026781@163.com
Date Created: 2025-03-06
Last Modified: 2025-03-06
Version: 1.0.0
Copyright (c) 2025 PeakVision
All rights reserved.
This software is released under the GNU GENERAL PUBLIC LICENSE, see LICENSE for more information.
"""

from heart_rate_monitor import HeartRateMonitor

class HeartRateCollector:
    def __init__(self, age):
        """
        初始化心率收集器。

        参数:
            age (int): 用户年龄，用于初始化心率监控器。
        """
        self.heart_rate_monitor = HeartRateMonitor(age)  # 创建 HeartRateMonitor 实例

    def get_heart_rate(self):
        """
        获取当前心率。

        返回值:
            int: 当前心率值 (bpm)。
        """
        return self.heart_rate_monitor.get_current_heart_rate()  # 调用 HeartRateMonitor 实例的 get_current_heart_rate 方法


