from inkos.app.base import App
from inkos.events import ACTION_BACK, ACTION_SELECT
from inkos.services.http_request import Response


class TimeSyncApp(App):
    app_id = "system.time_sync"
    name = "联网对时"

    def on_start(self):
        self.context.http.route("/app/system.time_sync", self._http_config, title="WiFi/对时")

    def on_event(self, event):
        if event.action == ACTION_SELECT:
            self._set_status("连接中")
            self.context.request_render()
            self._sync()
            self.context.kernel.request_full_refresh()
        elif event.action == ACTION_BACK:
            self.context.exit_app()

    def render(self, display):
        display.line("联网对时")
        display.line("WiFi: " + (self.context.settings.get("wifi.ssid", "") or "未配置"))
        display.line("状态: " + self.context.settings.get("time.sync_status", "未同步"))
        display.line("IO20 立即对时")

    def _http_config(self, request, conn=None):
        if request.method == "POST":
            self._save_form(request)
            self._set_status("已保存")
            return Response.redirect("/app/system.time_sync")

        page = self._page()
        return Response.html(self.context.http.page(page))

    def _save_form(self, request):
        ssid = request.form("ssid", "")
        password = request.form("password", "")
        host = request.form("ntp_host", "ntp.aliyun.com")
        offset = request.form("timezone_offset", "8")
        self.context.settings.set("wifi.ssid", ssid)
        self.context.settings.set("wifi.password", password)
        self.context.settings.set("time.ntp_host", host or "ntp.aliyun.com")
        try:
            self.context.settings.set("time.timezone_offset", int(offset))
        except Exception:
            self.context.settings.set("time.timezone_offset", 8)

    def _sync(self):
        ssid = self.context.settings.get("wifi.ssid", "")
        password = self.context.settings.get("wifi.password", "")
        if not ssid:
            self._set_status("未配置WiFi")
            return False
        try:
            self._set_status("连接中")
            if not self._connect_wifi(ssid, password):
                self._set_status("连接失败")
                return False
            import ntptime

            ntptime.host = self.context.settings.get("time.ntp_host", "ntp.aliyun.com") or "ntp.aliyun.com"
            ntptime.settime()
            self._set_status("同步成功")
            self.context.settings.set("time.last_sync", self._now_text())
            return True
        except Exception as exc:
            self.context.logger.exception("time sync failed", exc)
            self._set_status("同步失败")
            return False
        finally:
            self._disconnect_wifi()

    def _connect_wifi(self, ssid, password):
        import network
        import time

        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        if not sta.isconnected():
            sta.connect(ssid, password)
        start = self._ticks_ms()
        while not sta.isconnected():
            if self._ticks_diff(self._ticks_ms(), start) > 15000:
                return False
            time.sleep_ms(200) if hasattr(time, "sleep_ms") else time.sleep(0.2)
        return True

    def _disconnect_wifi(self):
        try:
            import network

            sta = network.WLAN(network.STA_IF)
            sta.disconnect()
            sta.active(False)
        except Exception:
            pass

    def _set_status(self, value):
        self.context.settings.set("time.sync_status", value)

    def _now_text(self):
        try:
            import time

            offset = int(self.context.settings.get("time.timezone_offset", 8) or 0)
            now = time.localtime(time.time() + offset * 3600)
            return "%04d-%02d-%02d %02d:%02d" % (now[0], now[1], now[2], now[3], now[4])
        except Exception:
            return ""

    def _page(self):
        ssid = self._html_escape(self.context.settings.get("wifi.ssid", ""))
        password = self._html_escape(self.context.settings.get("wifi.password", ""))
        host = self._html_escape(self.context.settings.get("time.ntp_host", "ntp.aliyun.com"))
        offset = self.context.settings.get("time.timezone_offset", 8)
        status = self._html_escape(self.context.settings.get("time.sync_status", "未同步"))
        last = self._html_escape(self.context.settings.get("time.last_sync", ""))
        return """<main><h2>WiFi / 对时</h2>
<section class='card'><form method='post'>
<label>SSID</label><input name='ssid' value='%s' autocomplete='off'>
<label>密码</label><input name='password' type='password' value='%s'>
<label>NTP 服务器</label><input name='ntp_host' value='%s'>
<label>时区</label><input name='timezone_offset' type='number' min='-12' max='14' value='%s'>
<button name='action' value='save'>保存配置</button>
</form></section>
<section class='card'><p>状态: %s</p><p>上次同步: %s</p><p class='hint'>网页只保存 WiFi 配置。保存后请在设备的“联网对时”插件中按 IO20 执行对时，避免文件服务网页阻塞。</p></section>
</main>""" % (ssid, password, host, offset, status, last or "-")

    def _html_escape(self, value):
        return str(value).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

    def _ticks_ms(self):
        try:
            import time

            return time.ticks_ms()
        except Exception:
            import time

            return int(time.time() * 1000)

    def _ticks_diff(self, end, start):
        try:
            import time

            return time.ticks_diff(end, start)
        except Exception:
            return end - start


def create_app(context):
    return TimeSyncApp(context)
