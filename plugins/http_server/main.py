from inkos.app.base import App
from inkos.events import ACTION_BACK, ACTION_SELECT


class HttpServerApp(App):
    app_id = "system.http"
    name = "文件服务"

    def on_event(self, event):
        if event.action == ACTION_SELECT:
            enabled = not self.context.http.enabled
            ok = self.context.http.set_enabled(enabled)
            if enabled and ok:
                self.context.kernel.show_dialog("文件服务", self.context.http.ip, self._stop)
            elif enabled:
                self.context.kernel.show_dialog("文件服务", "启动失败")
            self.context.request_render()
        elif event.action == ACTION_BACK:
            self.context.exit_app()

    def render(self, display):
        display.line("文件服务")
        display.line("状态: " + self.context.http.status_text())
        display.line("SSID: " + self.context.http.ssid)
        display.line("IO20 开关")

    def _stop(self):
        self.context.http.set_enabled(False)


def create_app(context):
    return HttpServerApp(context)
