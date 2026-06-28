class PowerDriver:
    def __init__(self, adc_pin=None, divider_ratio=2.0):
        self.adc_pin = adc_pin
        self.divider_ratio = divider_ratio
        self._adc = None

    def init(self):
        if self.adc_pin is None:
            return
        try:
            from machine import ADC, Pin

            self._adc = ADC(Pin(self.adc_pin))
            try:
                self._adc.atten(ADC.ATTN_11DB)
            except Exception:
                pass
        except Exception:
            self._adc = None

    def voltage(self):
        if self._adc is None:
            return None
        try:
            raw = self._adc.read()
        except Exception:
            return None
        return (raw / 4095.0) * 3.3 * self.divider_ratio

    def voltage_text(self):
        value = self.voltage()
        if value is None:
            return "--.--V"
        return "%.2fV" % value
