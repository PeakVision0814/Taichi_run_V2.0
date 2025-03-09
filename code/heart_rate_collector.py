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
        self.heart_rate_monitor = HeartRateMonitor(age)  # 创建 HeartRateMonitor 实例
        self.heart_rate_samples = []  # 初始化心率样本列表

    def get_heart_rate(self):
        heart_rate = self.heart_rate_monitor.get_current_heart_rate()
        self.heart_rate_samples.append(heart_rate) # 添加到样本列表
        return heart_rate

    def get_average_heart_rate(self):
        """
        计算运动期间的平均心率。

        返回值:
            float: 平均心率值 (bpm)，如果无心率样本则返回 0。
        """
        if not self.heart_rate_samples:
            return 0  #  无心率样本时返回 0
        return sum(self.heart_rate_samples) / len(self.heart_rate_samples)

    def reset_heart_rate_samples(self):
        """
        重置心率样本列表，开始新的心率统计。
        """
        self.heart_rate_samples = []  # 重置心率样本列表