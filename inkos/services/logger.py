class Logger:
    def __init__(self, path="/sd/data/logs/inkos.log"):
        self.path = path

    def info(self, message):
        self._write("INFO", message)

    def error(self, message):
        self._write("ERROR", message)

    def exception(self, message, exc):
        self._write("ERROR", "%s: %r" % (message, exc))

    def _write(self, level, message):
        line = "[%s] %s" % (level, message)
        print(line)
        try:
            with open(self.path, "a") as fp:
                fp.write(line + "\n")
        except Exception:
            pass
