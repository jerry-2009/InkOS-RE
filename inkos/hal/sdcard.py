class SDCardDriver:
    def __init__(self, mount_point="/sd"):
        self.mount_point = mount_point
        self.available = False

    def init(self):
        self.available = self._ensure_root()
        for path in (
            self.mount_point + "/plugins",
            self.mount_point + "/data",
            self.mount_point + "/data/logs",
        ):
            self._mkdir(path)
        return self.available

    def _ensure_root(self):
        try:
            import os

            os.listdir(self.mount_point)
            return True
        except Exception:
            pass

        # Board-specific SPI SD mounting belongs here when pins are known.
        # The fallback directory keeps the minimum validation system bootable.
        return self._mkdir(self.mount_point)

    def _mkdir(self, path):
        try:
            import os

            os.mkdir(path)
            return True
        except OSError:
            try:
                import os

                os.listdir(path)
                return True
            except Exception:
                return False
