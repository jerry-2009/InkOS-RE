import gc
import time

from inkos import config
from inkos.app.context import AppContext
from inkos.apps.launcher import LauncherApp
from inkos.events import ACTION_BACK_LONG
from inkos.hal.display_console import ConsoleDisplay
from inkos.hal.power import PowerDriver
from inkos.hal.sdcard import SDCardDriver
from inkos.hal.input_gpio import InputGPIO
from inkos.services.clock import ClockService
from inkos.services.logger import Logger
from inkos.services.plugin_manager import PluginManager
from inkos.services.settings import SettingsService
from inkos.services.file_transfer import FileTransferService
from inkos.services.file_manager import FileManagerWeb
from inkos.ui.dialog import Dialog
from inkos.ui.status_bar import StatusBar


class Kernel:
    def __init__(self):
        self.logger = Logger()
        self.display = self._create_display()
        self.input = InputGPIO()
        self.sdcard = SDCardDriver()
        self.settings = SettingsService()
        self.file_transfer = FileTransferService(self.logger)
        self.file_manager = FileManagerWeb()
        self.power = PowerDriver(
            getattr(config, "BATTERY_ADC_PIN", None),
            getattr(config, "BATTERY_DIVIDER_RATIO", 2.0),
        )
        self.clock = ClockService(self.settings)
        self.status_bar = StatusBar(self.clock, self.power)
        self.dialog = Dialog()
        self.plugin_manager = PluginManager(self.logger)
        self.launcher = None
        self.screensaver = None
        self.system_apps = {}
        self.current_app = None
        self.running = False
        self.sleeping = False

    def boot(self):
        self.logger.info("InkOS boot")
        self.logger.info("display=%s" % self.display.__class__.__name__)
        self.display.init()
        self.input.init()
        self.sdcard.init()
        self.settings.load()
        self.file_manager.register(self.file_transfer)
        self.apply_settings()
        self.power.init()
        self.plugin_manager.discover()
        self.launcher = LauncherApp(AppContext(self, "system.launcher", source="flash"))
        self._start_autostart_plugins()
        self.screensaver = self._create_screensaver()
        self.current_app = self.launcher
        self.current_app.on_start()
        self.current_app.on_resume()
        self.render()

    def run_forever(self):
        self.running = True
        while self.running:
            events = self.input.poll()
            for event in events:
                self.dispatch(event)
            self.file_transfer.poll()
            time.sleep_ms(20) if hasattr(time, "sleep_ms") else time.sleep(0.02)

    def dispatch(self, event):
        if event.action == ACTION_BACK_LONG:
            self.toggle_sleep()
            return
        if self.sleeping:
            return
        if self.dialog.active():
            self.dialog.clear()
            self.render()
            return
        try:
            self.current_app.on_event(event)
        except Exception as exc:
            self.logger.exception("app event failed", exc)
            self.back_to_launcher()

    def start_app(self, app_info):
        old_app = self.current_app
        try:
            old_app.on_pause()
            context = AppContext(self, app_info.app_id, app_info.path, app_info.source)
            app = self.system_apps.get(app_info.app_id)
            if not app:
                app = self.plugin_manager.load(app_info, context)
            self.current_app = app
            if app_info.app_id not in self.system_apps:
                app.on_start()
            app.on_resume()
            self._request_full_refresh()
            self.render()
        except Exception:
            self.current_app = old_app
            old_app.on_resume()
            self.render()

    def back_to_launcher(self):
        if self.current_app is not self.launcher:
            if self.current_app in self.system_apps.values():
                try:
                    self.current_app.on_pause()
                except Exception as exc:
                    self.logger.exception("app pause failed", exc)
            else:
                try:
                    self.current_app.on_pause()
                    self.current_app.on_stop()
                except Exception as exc:
                    self.logger.exception("app stop failed", exc)
            gc.collect()
        self.current_app = self.launcher
        self.launcher.on_resume()
        self._request_full_refresh()
        self.render()

    def render(self):
        try:
            self.display.clear()
            if not self.sleeping and self.settings.get("display.status_bar", True):
                self.status_bar.render(self.display)
                self.display.set_line_y(self.status_bar.height + 2)
            else:
                self.display.set_line_y(0)
            self.current_app.render(self.display)
            self.dialog.render(self.display)
            self.display.show()
        except Exception as exc:
            self.logger.exception("render failed", exc)

    def shutdown(self):
        self.running = False

    def _create_display(self):
        try:
            from inkos.hal.display_epd2in13 import EPD2in13Display

            return EPD2in13Display()
        except Exception as exc:
            print("EPD display unavailable, using console:", repr(exc))
            return ConsoleDisplay()

    def _request_full_refresh(self):
        request = getattr(self.display, "request_full_refresh", None)
        if request:
            request()

    def request_full_refresh(self):
        self._request_full_refresh()
        self.render()

    def apply_settings(self):
        apply_display = getattr(self.display, "apply_settings", None)
        if apply_display:
            apply_display(self.settings)
        self.power.adc_pin = self.settings.get("power.battery_adc_pin")
        self.power.divider_ratio = self.settings.get("power.divider_ratio", 2.0)
        self.power.init()
        self.file_transfer.set_enabled(False)

    def show_dialog(self, title, message, on_close=None):
        self.dialog.show(title, message, on_close)
        self._request_full_refresh()
        self.render()

    def toggle_sleep(self):
        if self.sleeping:
            self.sleeping = False
            self.current_app = self.launcher
            self._request_full_refresh()
            self.render()
        else:
            self._show_sleeping_dialog()
            self.sleeping = True
            self.current_app = self.screensaver
            self._request_full_refresh()
            self.render()

    def _show_sleeping_dialog(self):
        try:
            self.display.clear()
            if self.settings.get("display.status_bar", True):
                self.status_bar.render(self.display)
                self.display.set_line_y(self.status_bar.height + 2)
            else:
                self.display.set_line_y(0)
            self.current_app.render(self.display)
            dialog = Dialog()
            dialog.show("屏幕", "正在关闭")
            dialog.render(self.display)
            partial = getattr(self.display, "show_partial_once", None)
            if partial:
                partial()
            else:
                self.display.show()
        except Exception as exc:
            self.logger.exception("sleep dialog failed", exc)

    def _create_screensaver(self):
        app_info = self.plugin_manager.find("system.screensaver")
        if not app_info:
            return self.launcher
        if app_info.app_id in self.system_apps:
            return self.system_apps[app_info.app_id]
        app = self.plugin_manager.load(app_info, AppContext(self, app_info.app_id, app_info.path, app_info.source))
        app.on_start()
        return app

    def _start_autostart_plugins(self):
        for app_info in self.plugin_manager.apps:
            if not app_info.autostart:
                continue
            try:
                app = self.plugin_manager.load(app_info, AppContext(self, app_info.app_id, app_info.path, app_info.source))
                app.on_start()
                self.system_apps[app_info.app_id] = app
            except Exception as exc:
                self.logger.exception("autostart app %s failed" % app_info.app_id, exc)
