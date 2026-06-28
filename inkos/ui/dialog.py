class Dialog:
    def __init__(self):
        self.title = None
        self.message = None
        self.on_close = None

    def show(self, title, message, on_close=None):
        self.title = title
        self.message = message
        self.on_close = on_close

    def clear(self):
        callback = self.on_close
        self.title = None
        self.message = None
        self.on_close = None
        if callback:
            callback()

    def active(self):
        return self.title is not None

    def render(self, display):
        if not self.active():
            return
        x = 16
        y = 28
        w = display.width - 32
        h = 50
        display.rect(x, y, w, h, 0)
        display.text(x + 8, y + 8, self.title)
        display.text(x + 8, y + 28, self.message)
