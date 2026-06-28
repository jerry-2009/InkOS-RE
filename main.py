# main.py -- InkOS entry point.

try:
    from inkos.kernel import Kernel

    print("InkOS main.py start")
    kernel = Kernel()
    kernel.boot()
    kernel.run_forever()
except KeyboardInterrupt:
    print("InkOS stopped by KeyboardInterrupt")
except Exception as exc:
    print("InkOS fatal error:", repr(exc))
    try:
        import sys

        sys.print_exception(exc)
    except Exception:
        pass
