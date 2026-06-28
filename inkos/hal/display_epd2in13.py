import time

from inkos import config
from inkos.ui.hzk16 import HZK16Font


WHITE = 1
BLACK = 0


LUT_FULL_UPDATE = bytes((
    0x80, 0x60, 0x40, 0x00, 0x00, 0x00, 0x00,
    0x10, 0x60, 0x20, 0x00, 0x00, 0x00, 0x00,
    0x80, 0x60, 0x40, 0x00, 0x00, 0x00, 0x00,
    0x10, 0x60, 0x20, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x03, 0x03, 0x00, 0x00, 0x02,
    0x09, 0x09, 0x00, 0x00, 0x02,
    0x03, 0x03, 0x00, 0x00, 0x02,
    0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00,
    0x15, 0x41, 0xA8, 0x32, 0x30, 0x0A,
))

LUT_PARTIAL_UPDATE = bytes((
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x0A, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00,
    0x15, 0x41, 0xA8, 0x32, 0x30, 0x0A,
))


FONT_5X7 = {
    " ": (0x00, 0x00, 0x00, 0x00, 0x00),
    "!": (0x00, 0x00, 0x5F, 0x00, 0x00),
    ".": (0x00, 0x60, 0x60, 0x00, 0x00),
    "/": (0x20, 0x10, 0x08, 0x04, 0x02),
    ":": (0x00, 0x36, 0x36, 0x00, 0x00),
    ">": (0x41, 0x22, 0x14, 0x08, 0x00),
    "[": (0x00, 0x7F, 0x41, 0x41, 0x00),
    "]": (0x00, 0x41, 0x41, 0x7F, 0x00),
    "-": (0x08, 0x08, 0x08, 0x08, 0x08),
    "_": (0x40, 0x40, 0x40, 0x40, 0x40),
    "0": (0x3E, 0x51, 0x49, 0x45, 0x3E),
    "1": (0x00, 0x42, 0x7F, 0x40, 0x00),
    "2": (0x42, 0x61, 0x51, 0x49, 0x46),
    "3": (0x21, 0x41, 0x45, 0x4B, 0x31),
    "4": (0x18, 0x14, 0x12, 0x7F, 0x10),
    "5": (0x27, 0x45, 0x45, 0x45, 0x39),
    "6": (0x3C, 0x4A, 0x49, 0x49, 0x30),
    "7": (0x01, 0x71, 0x09, 0x05, 0x03),
    "8": (0x36, 0x49, 0x49, 0x49, 0x36),
    "9": (0x06, 0x49, 0x49, 0x29, 0x1E),
}

_letters = {
    "A": (0x7E, 0x11, 0x11, 0x11, 0x7E),
    "B": (0x7F, 0x49, 0x49, 0x49, 0x36),
    "C": (0x3E, 0x41, 0x41, 0x41, 0x22),
    "D": (0x7F, 0x41, 0x41, 0x22, 0x1C),
    "E": (0x7F, 0x49, 0x49, 0x49, 0x41),
    "F": (0x7F, 0x09, 0x09, 0x09, 0x01),
    "G": (0x3E, 0x41, 0x49, 0x49, 0x7A),
    "H": (0x7F, 0x08, 0x08, 0x08, 0x7F),
    "I": (0x00, 0x41, 0x7F, 0x41, 0x00),
    "J": (0x20, 0x40, 0x41, 0x3F, 0x01),
    "K": (0x7F, 0x08, 0x14, 0x22, 0x41),
    "L": (0x7F, 0x40, 0x40, 0x40, 0x40),
    "M": (0x7F, 0x02, 0x0C, 0x02, 0x7F),
    "N": (0x7F, 0x04, 0x08, 0x10, 0x7F),
    "O": (0x3E, 0x41, 0x41, 0x41, 0x3E),
    "P": (0x7F, 0x09, 0x09, 0x09, 0x06),
    "Q": (0x3E, 0x41, 0x51, 0x21, 0x5E),
    "R": (0x7F, 0x09, 0x19, 0x29, 0x46),
    "S": (0x46, 0x49, 0x49, 0x49, 0x31),
    "T": (0x01, 0x01, 0x7F, 0x01, 0x01),
    "U": (0x3F, 0x40, 0x40, 0x40, 0x3F),
    "V": (0x1F, 0x20, 0x40, 0x20, 0x1F),
    "W": (0x3F, 0x40, 0x38, 0x40, 0x3F),
    "X": (0x63, 0x14, 0x08, 0x14, 0x63),
    "Y": (0x07, 0x08, 0x70, 0x08, 0x07),
    "Z": (0x61, 0x51, 0x49, 0x45, 0x43),
}
FONT_5X7.update(_letters)
for _key, _value in _letters.items():
    FONT_5X7[_key.lower()] = _value


class EPD2in13Display:
    width = 212
    height = 104
    epd_width = 104
    epd_height = 212
    bytes_per_row = 13
    ascii_scale = 2
    ascii_width = 12
    ascii_height = 14

    def __init__(self, cs=3, dc=4, rst=5, sck=6, mosi=7, busy=8):
        from machine import Pin, SPI

        self.cs = Pin(cs, Pin.OUT, value=1)
        self.dc = Pin(dc, Pin.OUT, value=0)
        self.rst = Pin(rst, Pin.OUT, value=1)
        self.busy = Pin(busy, Pin.IN)
        sck_pin = Pin(sck)
        mosi_pin = Pin(mosi)
        try:
            self.spi = SPI(1, baudrate=2000000, polarity=0, phase=0, sck=sck_pin, mosi=mosi_pin)
        except Exception:
            from machine import SoftSPI

            self.spi = SoftSPI(baudrate=2000000, polarity=0, phase=0, sck=sck_pin, mosi=mosi_pin, miso=Pin(busy))
        self.buffer = bytearray([0xFF] * (self.bytes_per_row * self.epd_height))
        self.hzk16 = HZK16Font()
        print("HZK16=%s" % (self.hzk16.path or "not found"))
        self._line_y = 0
        self._initialized = False
        self._partial_mode = False
        self._partial_count = 0
        self._last_full_ms = 0
        self._force_full = True
        self._partial_limit = getattr(config, "EPD_PARTIAL_REFRESH_LIMIT", 30)
        self._full_interval_ms = getattr(config, "EPD_FULL_REFRESH_INTERVAL_MS", 60000)
        self._refresh_mode = "auto"

    def init(self):
        self._init_full()
        self._initialized = True
        self.clear()
        self.show(force_full=True)

    def _init_full(self):
        self._partial_mode = False
        self._reset()
        self._wait_idle()
        self._command(0x12)
        self._wait_idle()
        self._command(0x74)
        self._data(0x54)
        self._command(0x7E)
        self._data(0x3B)
        self._command(0x01)
        self._data(0xD3)
        self._data(0x00)
        self._data(0x00)
        self._command(0x11)
        self._data(0x01)
        self._command(0x44)
        self._data(0x00)
        self._data(0x0C)
        self._command(0x45)
        self._data(0xD3)
        self._data(0x00)
        self._data(0x00)
        self._data(0x00)
        self._command(0x3C)
        self._data(0x03)
        self._command(0x2C)
        self._data(0x55)
        self._command(0x03)
        self._data(LUT_FULL_UPDATE[70])
        self._command(0x04)
        self._data(LUT_FULL_UPDATE[71])
        self._data(LUT_FULL_UPDATE[72])
        self._data(LUT_FULL_UPDATE[73])
        self._command(0x3A)
        self._data(LUT_FULL_UPDATE[74])
        self._command(0x3B)
        self._data(LUT_FULL_UPDATE[75])
        self._command(0x32)
        self._data_bytes(LUT_FULL_UPDATE[:70])
        self._set_cursor(0, 0xD3)
        self._wait_idle()

    def _init_partial(self):
        if self._partial_mode:
            return
        self._command(0x2C)
        self._data(0x26)
        self._wait_idle()
        self._command(0x32)
        self._data_bytes(LUT_PARTIAL_UPDATE[:70])
        self._command(0x37)
        self._data_bytes(bytes((0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00)))
        self._command(0x22)
        self._data(0xC0)
        self._command(0x20)
        self._wait_idle()
        self._command(0x3C)
        self._data(0x01)
        self._partial_mode = True

    def clear(self, color=WHITE):
        fill = 0xFF if color else 0x00
        for index in range(len(self.buffer)):
            self.buffer[index] = fill
        self._line_y = 0

    def set_line_y(self, y):
        self._line_y = y

    def text_width(self, value):
        width = 0
        for char in str(value):
            width += self.ascii_width if ord(char) < 128 else 16
        return width

    def apply_settings(self, settings):
        scale = settings.get("display.font_scale", self.ascii_scale)
        if scale < 1:
            scale = 1
        if scale > 3:
            scale = 3
        self.ascii_scale = scale
        self.ascii_width = 6 * scale
        self.ascii_height = 7 * scale
        self._line_height = settings.get("display.line_height", 18)
        self._refresh_mode = settings.get("refresh.mode", "auto")
        self._partial_limit = settings.get("refresh.partial_limit", self._partial_limit)
        self._full_interval_ms = settings.get("refresh.full_interval_ms", self._full_interval_ms)

    def text(self, x, y, value, color=BLACK):
        cursor_x = x
        for char in str(value):
            code = ord(char)
            if code < 128:
                self._char(cursor_x, y, char, color)
                cursor_x += self.ascii_width
            else:
                self._hzk16_char(cursor_x, y, char, color)
                cursor_x += 16

    def line(self, value=""):
        self.text(0, self._line_y, value)
        self._line_y += getattr(self, "_line_height", 18)

    def hline(self, x, y, width, color=BLACK):
        for offset in range(width):
            self.pixel(x + offset, y, color)

    def vline(self, x, y, height, color=BLACK):
        for offset in range(height):
            self.pixel(x, y + offset, color)

    def rect(self, x, y, width, height, color=BLACK, fill=WHITE):
        for yy in range(y, y + height):
            for xx in range(x, x + width):
                self.pixel(xx, yy, fill)
        self.hline(x, y, width, color)
        self.hline(x, y + height - 1, width, color)
        self.vline(x, y, height, color)
        self.vline(x + width - 1, y, height, color)

    def icon(self, x, y, bitmap, color=BLACK):
        if not bitmap:
            return
        for row in range(16):
            bits = (bitmap[row * 2] << 8) | bitmap[row * 2 + 1]
            for col in range(16):
                if bits & (0x8000 >> col):
                    self.pixel(x + col, y + row, color)

    def bitmap_1bit(self, x, y, width, height, bitmap, color=BLACK):
        if not bitmap:
            return
        row_bytes = (width + 7) // 8
        for row in range(height):
            for col in range(width):
                index = row * row_bytes + (col >> 3)
                if index >= len(bitmap):
                    return
                if bitmap[index] & (0x80 >> (col & 7)):
                    self.pixel(x + col, y + row, color)

    def show(self, force_full=False):
        if not self._initialized:
            return
        if self._refresh_mode == "full":
            force_full = True
        if force_full or self._force_full or self._should_full_refresh():
            self._display_full()
        elif self._refresh_mode == "partial" or self._refresh_mode == "auto":
            self._display_partial()

    def request_full_refresh(self):
        self._force_full = True

    def show_partial_once(self):
        if not self._initialized:
            return
        self._display_partial()

    def _should_full_refresh(self):
        if self._partial_count >= self._partial_limit:
            return True
        elapsed = self._ticks_diff(self._ticks_ms(), self._last_full_ms)
        return elapsed >= self._full_interval_ms

    def _display_full(self):
        if self._partial_mode:
            self._init_full()
        self._set_cursor(0, 0xD3)
        self._command(0x24)
        self._data_bytes(self.buffer)
        self._turn_on_display()
        self._command(0x26)
        self._data_bytes(self.buffer)
        self._last_full_ms = self._ticks_ms()
        self._partial_count = 0
        self._force_full = False

    def _display_partial(self):
        self._init_partial()
        self._set_cursor(0, 0xD3)
        self._command(0x24)
        self._data_bytes(self.buffer)
        self._turn_on_display_part()
        self._partial_count += 1

    def sleep(self):
        self._command(0x22)
        self._data(0xC3)
        self._command(0x20)
        self._command(0x10)
        self._data(0x01)
        self._sleep_ms(100)

    def wake(self):
        self.init()

    def _char(self, x, y, char, color):
        glyph = FONT_5X7.get(char, FONT_5X7.get(" "))
        for col, bits in enumerate(glyph):
            for row in range(7):
                if bits & (1 << row):
                    self._scaled_pixel(x + col * self.ascii_scale, y + row * self.ascii_scale, self.ascii_scale, color)

    def _scaled_pixel(self, x, y, scale, color):
        for dy in range(scale):
            for dx in range(scale):
                self.pixel(x + dx, y + dy, color)

    def _hzk16_char(self, x, y, char, color):
        bitmap = self.hzk16.bitmap(char)
        self._hzk16_bitmap(x, y, bitmap, color)

    def _hzk16_bytes(self, x, y, left, right, color):
        bitmap = self.hzk16.bitmap_from_gb2312(left, right)
        self._hzk16_bitmap(x, y, bitmap, color)

    def _hzk16_bitmap(self, x, y, bitmap, color):
        if bitmap is None:
            self._missing_char(x, y, color)
            return
        for row in range(16):
            left = bitmap[row * 2]
            right = bitmap[row * 2 + 1]
            bits = (left << 8) | right
            for col in range(16):
                if bits & (0x8000 >> col):
                    self.pixel(x + col, y + row, color)

    def _missing_char(self, x, y, color):
        for col in range(16):
            self.pixel(x + col, y, color)
            self.pixel(x + col, y + 15, color)
        for row in range(16):
            self.pixel(x, y + row, color)
            self.pixel(x + 15, y + row, color)
        self.pixel(x + 4, y + 4, color)
        self.pixel(x + 8, y + 8, color)
        self.pixel(x + 11, y + 11, color)

    def pixel(self, x, y, color):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return
        # Match the documented logical canvas: 212x104, rotate 270 and mirror vertical.
        physical_x = y
        physical_y = x
        if physical_x < 0 or physical_y < 0 or physical_x >= self.epd_width or physical_y >= self.epd_height:
            return
        index = physical_y * self.bytes_per_row + (physical_x >> 3)
        mask = 0x80 >> (physical_x & 0x07)
        if color == BLACK:
            self.buffer[index] &= ~mask
        else:
            self.buffer[index] |= mask

    def _reset(self):
        self.rst.value(1)
        self._sleep_ms(200)
        self.rst.value(0)
        self._sleep_ms(10)
        self.rst.value(1)
        self._sleep_ms(200)

    def _command(self, command):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytes((command,)))
        self.cs.value(1)

    def _data(self, data):
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(bytes((data,)))
        self.cs.value(1)

    def _data_bytes(self, data):
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(data)
        self.cs.value(1)

    def _wait_idle(self):
        while self.busy.value() == 1:
            self._sleep_ms(100)

    def _turn_on_display(self):
        self._command(0x22)
        self._data(0xC7)
        self._command(0x20)
        self._wait_idle()

    def _turn_on_display_part(self):
        self._command(0x22)
        self._data(0x0C)
        self._command(0x20)
        self._wait_idle()

    def _set_cursor(self, x, y):
        self._command(0x4E)
        self._data(x)
        self._command(0x4F)
        self._data(y)
        self._data(0x00)

    def _sleep_ms(self, ms):
        if hasattr(time, "sleep_ms"):
            time.sleep_ms(ms)
        else:
            time.sleep(ms / 1000)

    def _ticks_ms(self):
        if hasattr(time, "ticks_ms"):
            return time.ticks_ms()
        return int(time.time() * 1000)

    def _ticks_diff(self, end, start):
        if hasattr(time, "ticks_diff"):
            return time.ticks_diff(end, start)
        return end - start
