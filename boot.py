# boot.py -- run on boot-up
#
# Keep early boot small: prepare storage directories and hand off to main.py.

try:
    import machine

    machine.freq(160000000)
except Exception:
    pass


def _mkdir(path):
    try:
        import os

        os.mkdir(path)
    except OSError:
        pass


for _path in ("/apps", "/plugins", "/sd", "/sd/plugins", "/sd/data", "/sd/data/logs"):
    _mkdir(_path)
