from inkos import __version__
from inkos.app.base import App
from inkos.events import ACTION_BACK, ACTION_DOWN, ACTION_SELECT, ACTION_UP
from inkos.ui.pager import draw_page_arrows, list_window


class SettingsApp(App):
    app_id = "system.settings"
    name = "设置"

    def __init__(self, context):
        App.__init__(self, context)
        self.page = "root"
        self.root_index = 0
        self.item_index = 0
        self.categories = self._categories()

    def on_event(self, event):
        items = self._current_items()
        if event.action == ACTION_UP:
            self._set_index((self._index() - 1) % len(items))
            self.context.request_render()
        elif event.action == ACTION_DOWN:
            self._set_index((self._index() + 1) % len(items))
            self.context.request_render()
        elif event.action == ACTION_SELECT:
            self._select(items[self._index()])
        elif event.action == ACTION_BACK:
            if self.page == "root":
                self.context.exit_app()
            else:
                self.page = "root"
                self.item_index = 0
                self.context.kernel.request_full_refresh()

    def render(self, display):
        display.line(self._title())
        items = self._current_items()
        index = self._index()
        start, end, has_prev, has_next = list_window(display, len(items), index)
        for offset, item in enumerate(items[start:end]):
            row = start + offset
            marker = ">" if row == index else " "
            display.line(marker + " " + self._label(item))
        draw_page_arrows(display, has_prev, has_next)

    def _categories(self):
        return (
            ("display", "显示", (
                ("choice", "字体", "display.font_scale", (1, 2, 3)),
                ("choice", "行高", "display.line_height", (14, 16, 18, 20, 22)),
                ("toggle", "状态栏", "display.status_bar"),
            )),
            ("refresh", "刷新", (
                ("choice", "刷新方式", "refresh.mode", ("auto", "partial", "full")),
                ("choice", "局刷次数", "refresh.partial_limit", (5, 10, 20, 30, 50)),
                ("choice", "全刷间隔", "refresh.full_interval_ms", (30000, 60000, 120000, 300000)),
                ("command", "立即全刷", "full_refresh"),
            )),
            ("power", "电源", (
                ("choice", "电池ADC", "power.battery_adc_pin", (None, 0, 1, 2, 3, 4)),
                ("choice", "分压倍率", "power.divider_ratio", (1.0, 1.5, 2.0, 2.5, 3.0)),
            )),
            ("system", "系统", (
                ("toggle", "安全模式", "system.safe_mode"),
                ("command", "保存并应用", "apply"),
            )),
            ("about", "关于", (
                ("about", "InkOS " + __version__),
                ("about", "ESP32-C3"),
                ("about", "MicroPython"),
                ("about", "IO1/20/21/9"),
            )),
        )

    def _current_items(self):
        if self.page == "root":
            return self.categories
        for key, title, items in self.categories:
            if key == self.page:
                return items
        return self.categories

    def _title(self):
        if self.page == "root":
            return "系统设置"
        for key, title, items in self.categories:
            if key == self.page:
                return "设置/" + title
        return "系统设置"

    def _index(self):
        return self.root_index if self.page == "root" else self.item_index

    def _set_index(self, value):
        if self.page == "root":
            self.root_index = value
        else:
            self.item_index = value

    def _select(self, item):
        if self.page == "root":
            self.page = item[0]
            self.item_index = 0
            self.context.kernel.request_full_refresh()
            return

        kind = item[0]
        if kind == "toggle":
            self.context.settings.toggle(item[2])
            self.context.kernel.apply_settings()
            self.context.request_render()
        elif kind == "choice":
            self._next_choice(item)
            self.context.kernel.apply_settings()
            self.context.request_render()
        elif kind == "command":
            if item[2] == "full_refresh":
                self.context.kernel.request_full_refresh()
            elif item[2] == "apply":
                self.context.kernel.apply_settings()
            self.context.request_render()

    def _next_choice(self, item):
        key = item[2]
        values = item[3]
        current = self.context.settings.get(key)
        try:
            index = values.index(current)
        except ValueError:
            index = -1
        self.context.settings.set(key, values[(index + 1) % len(values)])

    def _label(self, item):
        if self.page == "root":
            return item[1]

        kind = item[0]
        if kind == "about":
            return item[1]
        if kind == "command":
            return item[1]

        value = self.context.settings.get(item[2])
        if kind == "toggle":
            return "%s: %s" % (item[1], "开" if value else "关")
        return "%s: %s" % (item[1], self._value_text(item[2], value))

    def _value_text(self, key, value):
        if key == "refresh.mode":
            if value == "auto":
                return "自动"
            if value == "partial":
                return "局刷"
            if value == "full":
                return "全刷"
        if key == "refresh.full_interval_ms":
            return "%ds" % (value // 1000)
        if key == "power.battery_adc_pin":
            return "关闭" if value is None else "GPIO%d" % value
        return str(value)


def create_app(context):
    return SettingsApp(context)
