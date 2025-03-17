from ui_elements.treadmill_app import TreadmillApp
from core.heart_rate_collector import HeartRateCollector

if __name__ == "__main__":
    collector = HeartRateCollector()
    app = TreadmillApp(collector)
    app.mainloop()