ARROW_GUTTER = 8


def glyph_height(display):
    return max(getattr(display, "ascii_height", 14), 16)


def line_height(display):
    return getattr(display, "_line_height", 18)


def list_window(display, total, index, top_y=None):
    if total <= 0:
        return 0, 0, False, False
    if top_y is None:
        top_y = getattr(display, "_line_y", 0)
    normal_capacity = _row_capacity(display, top_y, 0)
    reserve = ARROW_GUTTER if total > normal_capacity else 0
    capacity = _row_capacity(display, top_y, reserve)
    start = (index // capacity) * capacity
    end = min(total, start + capacity)
    return start, end, start > 0, end < total


def fixed_window(total, index, page_size):
    if total <= 0:
        return 0, 0, False, False
    page_size = max(1, page_size)
    start = (index // page_size) * page_size
    end = min(total, start + page_size)
    return start, end, start > 0, end < total


def draw_page_arrows(display, has_prev, has_next):
    if not has_prev and not has_next:
        return
    y = max(0, getattr(display, "height", 104) - 6)
    if has_prev:
        _up_arrow(display, max(4, getattr(display, "width", 212) - 18), y)
    if has_next:
        _down_arrow(display, max(4, getattr(display, "width", 212) - 8), y)


def _row_capacity(display, top_y, bottom_reserve):
    bottom = getattr(display, "height", 104) - bottom_reserve
    available = bottom - top_y - glyph_height(display)
    if available < 0:
        return 1
    return max(1, (available // line_height(display)) + 1)


def _up_arrow(display, x, y):
    for row in range(4):
        _hline(display, x - row, y + row, row * 2 + 1)


def _down_arrow(display, x, y):
    for row in range(4):
        width = (3 - row) * 2 + 1
        _hline(display, x - (width // 2), y + row, width)


def _hline(display, x, y, width):
    draw = getattr(display, "hline", None)
    if draw:
        draw(x, y, width)
        return
    pixel = getattr(display, "pixel", None)
    if not pixel:
        return
    for offset in range(width):
        pixel(x + offset, y, 0)
