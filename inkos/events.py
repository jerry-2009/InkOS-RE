ACTION_UP = "UP"
ACTION_SELECT = "SELECT"
ACTION_DOWN = "DOWN"
ACTION_BACK = "BACK"
ACTION_BACK_LONG = "BACK_LONG"


class InputEvent:
    def __init__(self, action, long_press=False):
        self.action = action
        self.long_press = long_press

    def __repr__(self):
        return "InputEvent(%r)" % self.action
