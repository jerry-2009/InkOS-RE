class ClockService:
    def __init__(self, settings=None):
        self.settings = settings

    def time_text(self):
        try:
            import time

            offset = 0
            if self.settings:
                offset = int(self.settings.get("time.timezone_offset", 0) or 0)
            now = time.localtime(time.time() + offset * 3600)
            return "%02d:%02d" % (now[3], now[4])
        except Exception:
            return "--:--"
