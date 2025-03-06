import tkinter as tk
from treamill_app import TreadmillApp

def create_main_window():
    root = tk.Tk()
    root.title(
        "智能太极跑系统"
        )
    return root

def start_application():
    root = create_main_window()
    app = TreadmillApp(
        root
        )
    root.mainloop()

if __name__ == "__main__":
    start_application()