from inkos.app.base import App
from inkos.events import ACTION_BACK


class HelloApp(App):
    app_id = "system.hello"
    name = "你好"

    def on_event(self, event):
        if event.action == ACTION_BACK:
            self.context.exit_app()

    def render(self, display):
        display.line("你好应用")
        display.line("")
        display.line("这个应用存储在")
        display.line("闪存 /apps")
        display.line("")
        display.line("IO9 返回")


def create_app(context):
    return HelloApp(context)
