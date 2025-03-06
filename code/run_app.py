"""
Run the application.
==================
This module is the entry point for the launch page.
Author: Gaopeng Huang; Hui Guo
Email: perished_hgp@163.com; 
Date Created: 2025-03-06
Last Modified: 2025-03-06
Version: 2.0.0
Copyright (c) 2025 PeakVision
All rights reserved.
This software is released under the GNU GENERAL PUBLIC LICENSE, see LICENSE for more information.
"""

import tkinter as tk
from treamill_app import TreadmillApp

def create_main_window():
    root = tk.Tk()
    root.title("智能太极跑系统V2.0")
    return root

def start_application():
    root = create_main_window()
    app = TreadmillApp(root)
    root.mainloop()

if __name__ == "__main__":
    start_application()