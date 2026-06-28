class ConsoleDisplay:
    width = 212
    height = 104

    def __init__(self):
        self.lines = []

    def init(self):
        self.clear()

    def clear(self, color=1):
        self.lines = []

    def set_line_y(self, y):
        pass

    def text_width(self, value):
        return len(str(value)) * 6

    def text(self, x, y, value):
        self.lines.append(str(value))

    def hline(self, x, y, width, color=0):
        self.lines.append("-" * min(width, 24))

    def rect(self, x, y, width, height, color=0, fill=1):
        self.lines.append("[dialog]")

    def icon(self, x, y, bitmap, color=0):
        pass

    def bitmap_1bit(self, x, y, width, height, bitmap, color=0):
        pass

    def apply_settings(self, settings):
        pass

    def request_full_refresh(self):
        pass

    def line(self, value=""):
        self.lines.append(str(value))

    def show(self):
        print("\n" + "=" * 24)
        for line in self.lines:
            print(line)
        print("=" * 24)

    def show_partial_once(self):
        self.show()

    def sleep(self):
        pass

    def wake(self):
        pass
