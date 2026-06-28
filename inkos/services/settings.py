try:
    import ujson as json
except ImportError:
    import json


DEFAULT_SETTINGS = {
    "display.font_scale": 2,
    "display.line_height": 18,
    "display.status_bar": True,
    "refresh.mode": "auto",
    "refresh.partial_limit": 30,
    "refresh.full_interval_ms": 60000,
    "power.battery_adc_pin": 0,
    "power.divider_ratio": 2.0,
    "screensaver.title": "InkOS",
    "screensaver.subtitle": "休眠中",
    "screensaver.mode": "text",
    "screensaver.image_hex": "",
    "wifi.ssid": "",
    "wifi.password": "",
    "time.ntp_host": "ntp.aliyun.com",
    "time.timezone_offset": 8,
    "time.last_sync": "",
    "time.sync_status": "未同步",
    "system.safe_mode": False,
}


class SettingsService:
    def __init__(self, path="/sd/data/settings.json"):
        self.path = path
        self.values = dict(DEFAULT_SETTINGS)

    def load(self):
        try:
            with open(self.path, "r") as fp:
                loaded = json.load(fp)
            for key, value in loaded.items():
                if key in self.values:
                    self.values[key] = value
        except Exception:
            pass

    def save(self):
        try:
            tmp = self.path + ".tmp"
            with open(tmp, "w") as fp:
                json.dump(self.values, fp)
            try:
                import os

                os.remove(self.path)
            except Exception:
                pass
            import os

            os.rename(tmp, self.path)
        except Exception:
            pass

    def get(self, key, default=None):
        return self.values.get(key, default)

    def set(self, key, value):
        self.values[key] = value
        self.save()

    def toggle(self, key):
        self.set(key, not bool(self.get(key)))
