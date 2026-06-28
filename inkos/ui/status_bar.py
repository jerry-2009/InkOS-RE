class StatusBar:
    height = 18

    def __init__(self, clock, power):
        self.clock = clock
        self.power = power

    def render(self, display):
        display.text(0, 1, self.clock.time_text())
        voltage = self.power.voltage_text()
        display.text(display.width - display.text_width(voltage), 1, voltage)
        display.hline(0, self.height - 1, display.width)
