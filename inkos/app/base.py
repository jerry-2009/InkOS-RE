class App:
    app_id = ""
    name = ""

    def __init__(self, context):
        self.context = context

    def on_start(self):
        pass

    def on_resume(self):
        pass

    def on_pause(self):
        pass

    def on_stop(self):
        pass

    def on_event(self, event):
        pass

    def render(self, display):
        display.clear()
        display.text(0, 0, self.name or self.app_id or "App")
