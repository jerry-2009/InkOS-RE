from inkos.app.base import App
from inkos.events import ACTION_BACK, ACTION_DOWN, ACTION_SELECT, ACTION_UP
from inkos.services.plugin_manager import AppInfo
from inkos.ui.icons import ICON_SETTINGS
from inkos.ui.pager import ARROW_GUTTER, draw_page_arrows, fixed_window, glyph_height


class LauncherApp(App):
    app_id = "system.launcher"
    name = "启动器"

    def __init__(self, context):
        App.__init__(self, context)
        self.index = 0
        self.page = "main"
        self.system_entry = AppInfo("system.folder", "系统", None, None, "folder", icon=ICON_SETTINGS, category="folder")

    def on_event(self, event):
        apps = self._apps()
        if not apps:
            return

        if event.action == ACTION_UP:
            self.index = (self.index - 1) % len(apps)
            self.context.request_render()
        elif event.action == ACTION_DOWN:
            self.index = (self.index + 1) % len(apps)
            self.context.request_render()
        elif event.action == ACTION_SELECT:
            app = apps[self.index]
            if app.app_id == "system.folder":
                self.page = "system"
                self.index = 0
                self.context.kernel.request_full_refresh()
            else:
                self.context.kernel.start_app(app)
        elif event.action == ACTION_BACK:
            if self.page == "system":
                self.page = "main"
                self.index = 0
                self.context.kernel.request_full_refresh()
            else:
                self.context.logger.info("launcher back ignored")

    def render(self, display):
        apps = self._apps()
        if not apps:
            display.line("没有找到应用")
            display.line("/apps /plugins")
            display.line("/sd/plugins")
            return

        page_size = 6
        start, end, has_prev, has_next = fixed_window(len(apps), self.index, page_size)
        cell_w = display.width // 3
        base_y = getattr(display, "_line_y", 0)
        grid_bottom = display.height - (ARROW_GUTTER if has_prev or has_next else 0)
        cell_h = max(34, (grid_bottom - base_y) // 2)
        text_h = glyph_height(display)
        for offset, app in enumerate(apps[start:end]):
            absolute = start + offset
            col = offset % 3
            row = offset // 3
            x = col * cell_w
            y = base_y + row * cell_h
            if absolute == self.index:
                display.rect(x + 1, y + 1, cell_w - 2, cell_h - 2, 0)
            display.icon(x + (cell_w - 16) // 2, y + 3, app.icon)
            name = self._fit_name(display, app.name, cell_w - 4)
            name_x = x + max(2, (cell_w - display.text_width(name)) // 2)
            display.text(name_x, min(y + 23, y + cell_h - text_h - 2), name)
        draw_page_arrows(display, has_prev, has_next)

    def _apps(self):
        apps = self.context.kernel.plugin_manager.apps
        if self.page == "system":
            return [app for app in apps if app.category == "system"]
        main_apps = [app for app in apps if app.category != "system"]
        if any(app.category == "system" for app in apps):
            main_apps.append(self.system_entry)
        return main_apps

    def _fit_name(self, display, name, max_width):
        name = str(name)
        if display.text_width(name) <= max_width:
            return name
        suffix = "..."
        suffix_width = display.text_width(suffix)
        result = ""
        for char in name:
            if display.text_width(result + char) + suffix_width > max_width:
                break
            result += char
        return (result or name[:1]) + suffix
