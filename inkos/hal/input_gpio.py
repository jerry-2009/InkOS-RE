from inkos.events import ACTION_BACK, ACTION_BACK_LONG, ACTION_DOWN, ACTION_SELECT, ACTION_UP, InputEvent


BUTTON_MAP = {
    1: ACTION_UP,
    20: ACTION_SELECT,
    21: ACTION_DOWN,
    9: ACTION_BACK,
}


class InputGPIO:
    debounce_ms = 80
    long_press_ms = 1200

    def __init__(self, pins=None, pull_up=True):
        self.pins = pins or BUTTON_MAP
        self.pull_up = pull_up
        self._machine_pins = []
        self._last = {}
        self._ticks_ms = None
        self._ticks_diff = None
        self._queue = []
        self._machine = None
        self._pressed_at = {}
        self._long_sent = {}

    def init(self):
        try:
            import machine
            import time

            self._machine = machine
            self._ticks_ms = time.ticks_ms
            self._ticks_diff = time.ticks_diff
            mode = machine.Pin.IN
            pull = machine.Pin.PULL_UP if self.pull_up else machine.Pin.PULL_DOWN
            for gpio in self.pins:
                pin = machine.Pin(gpio, mode, pull)
                self._machine_pins.append((gpio, pin))
                self._last[gpio] = (pin.value(), self._ticks_ms())
                self._pressed_at[gpio] = None
                self._long_sent[gpio] = False
        except Exception:
            self._machine_pins = []

    def poll(self):
        if not self._machine_pins:
            if self._queue:
                return [InputEvent(self._queue.pop(0))]
            return []

        now = self._ticks_ms()
        events = []
        pressed_value = 0 if self.pull_up else 1
        for gpio, pin in self._machine_pins:
            value = pin.value()
            last_value, last_time = self._last[gpio]
            if value != last_value and self._ticks_diff(now, last_time) >= self.debounce_ms:
                self._last[gpio] = (value, now)
                if value == pressed_value:
                    self._pressed_at[gpio] = now
                    self._long_sent[gpio] = False
                else:
                    pressed_at = self._pressed_at.get(gpio)
                    action = self.pins[gpio]
                    if pressed_at is not None and not self._long_sent.get(gpio):
                        events.append(InputEvent(action))
                    self._pressed_at[gpio] = None
                    self._long_sent[gpio] = False
            elif value == pressed_value:
                pressed_at = self._pressed_at.get(gpio)
                if (
                    self.pins[gpio] == ACTION_BACK
                    and pressed_at is not None
                    and not self._long_sent.get(gpio)
                    and self._ticks_diff(now, pressed_at) >= self.long_press_ms
                ):
                    self._long_sent[gpio] = True
                    events.append(InputEvent(ACTION_BACK_LONG, True))
        return events

    def inject(self, action):
        self._queue.append(action)
