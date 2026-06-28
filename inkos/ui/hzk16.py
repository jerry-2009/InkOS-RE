GB2312_OVERRIDES = {
    0x4E0A: (0xC9, 0xCF),
    0x4E0B: (0xCF, 0xC2),
    0x4E0D: (0xB2, 0xBB),
    0x4E2A: (0xB8, 0xF6),
    0x4E2D: (0xD6, 0xD0),
    0x4E8E: (0xD3, 0xDA),
    0x4EF6: (0xBC, 0xFE),
    0x4F11: (0xD0, 0xDD),
    0x4F20: (0xB4, 0xAB),
    0x4F4E: (0xB5, 0xCD),
    0x4F53: (0xCC, 0xE5),
    0x4F5C: (0xD7, 0xF7),
    0x4F60: (0xC4, 0xE3),
    0x4FDD: (0xB1, 0xA3),
    0x500D: (0xB1, 0xB6),
    0x50A8: (0xB4, 0xA2),
    0x5168: (0xC8, 0xAB),
    0x5173: (0xB9, 0xD8),
    0x5206: (0xB7, 0xD6),
    0x5230: (0xB5, 0xBD),
    0x5237: (0xCB, 0xA2),
    0x526F: (0xB8, 0xB1),
    0x529F: (0xB9, 0xA6),
    0x52A1: (0xCE, 0xF1),
    0x52A8: (0xB6, 0xAF),
    0x5361: (0xBF, 0xA8),
    0x5373: (0xBC, 0xB4),
    0x538B: (0xD1, 0xB9),
    0x542F: (0xC6, 0xF4),
    0x548C: (0xBA, 0xCD),
    0x5524: (0xBB, 0xBD),
    0x5668: (0xC6, 0xF7),
    0x5931: (0xCA, 0xA7),
    0x56DE: (0xBB, 0xD8),
    0x5728: (0xD4, 0xDA),
    0x597D: (0xBA, 0xC3),
    0x5B57: (0xD7, 0xD6),
    0x5B58: (0xB4, 0xE6),
    0x5B89: (0xB0, 0xB2),
    0x5C40: (0xBE, 0xD6),
    0x5C4F: (0xC6, 0xC1),
    0x5DF2: (0xD2, 0xD1),
    0x5E76: (0xB2, 0xA2),
    0x5E94: (0xD3, 0xA6),
    0x5F00: (0xBF, 0xAA),
    0x5F0F: (0xCA, 0xBD),
    0x6001: (0xCC, 0xAC),
    0x6301: (0xB3, 0xD6),
    0x652F: (0xD6, 0xA7),
    0x627E: (0xD5, 0xD2),
    0x6309: (0xB0, 0xB4),
    0x64CD: (0xB2, 0xD9),
    0x6570: (0xCA, 0xFD),
    0x6587: (0xCE, 0xC4),
    0x65B0: (0xD0, 0xC2),
    0x65B9: (0xB7, 0xBD),
    0x65E0: (0xCE, 0xDE),
    0x663E: (0xCF, 0xD4),
    0x6709: (0xD3, 0xD0),
    0x670D: (0xB7, 0xFE),
    0x6807: (0xB1, 0xEA),
    0x680F: (0xC0, 0xB8),
    0x6A21: (0xC4, 0xA3),
    0x6B21: (0xB4, 0xCE),
    0x6C60: (0xB3, 0xD8),
    0x6CA1: (0xC3, 0xBB),
    0x6E90: (0xD4, 0xB4),
    0x72B6: (0xD7, 0xB4),
    0x7387: (0xC2, 0xCA),
    0x7528: (0xD3, 0xC3),
    0x7535: (0xB5, 0xE7),
    0x7720: (0xC3, 0xDF),
    0x793A: (0xCA, 0xBE),
    0x7ACB: (0xC1, 0xA2),
    0x7CFB: (0xCF, 0xB5),
    0x7EDF: (0xCD, 0xB3),
    0x7F6E: (0xD6, 0xC3),
    0x7F51: (0xCD, 0xF8),
    0x8017: (0xBA, 0xC4),
    0x81EA: (0xD7, 0xD4),
    0x8282: (0xBD, 0xDA),
    0x884C: (0xD0, 0xD0),
    0x8BBE: (0xC9, 0xE8),
    0x8BF7: (0xC7, 0xEB),
    0x8D25: (0xB0, 0xDC),
    0x8F93: (0xCA, 0xE4),
    0x8BFB: (0xB6, 0xC1),
    0x8C03: (0xB5, 0xF7),
    0x8FD4: (0xB7, 0xB5),
    0x8FD9: (0xD5, 0xE2),
    0x9192: (0xD0, 0xD1),
    0x957F: (0xB3, 0xA4),
    0x9009: (0xD1, 0xA1),
    0x914D: (0xC5, 0xE4),
    0x95EA: (0xC9, 0xC1),
    0x95ED: (0xB1, 0xD5),
    0x95F4: (0xBC, 0xE4),
    0x9694: (0xB8, 0xF4),
    0x9898: (0xCC, 0xE2),
    0x9875: (0xD2, 0xB3),
    0x9AD8: (0xB8, 0xDF),
}


class HZK16Font:
    width = 16
    height = 16
    bytes_per_char = 32

    def __init__(self, paths=None):
        self.paths = paths or (
            "/fonts/HZK16",
            "/font/HZK16",
            "/sd/fonts/HZK16",
            "/sd/font/HZK16",
            "fonts/HZK16",
            "font/HZK16",
            "sd/fonts/HZK16",
            "sd/font/HZK16",
        )
        self.map_paths = (
            "/fonts/GB2312.TBL",
            "/font/GB2312.TBL",
            "/sd/fonts/GB2312.TBL",
            "/sd/font/GB2312.TBL",
            "fonts/GB2312.TBL",
            "font/GB2312.TBL",
            "sd/fonts/GB2312.TBL",
            "sd/font/GB2312.TBL",
        )
        self.path = self._find_path()
        self.map_path = self._find_map_path()
        self._map_cache = {}

    def available(self):
        return self.path is not None

    def bitmap(self, char):
        if not self.path:
            return None
        encoded = self._gb2312(char)
        if encoded is None:
            return None

        return self.bitmap_from_gb2312(encoded[0], encoded[1])

    def bitmap_from_gb2312(self, left, right):
        if not self.path:
            return None

        area = left - 0xA0
        index = right - 0xA0
        if area < 1 or area > 94 or index < 1 or index > 94:
            return None

        offset = ((area - 1) * 94 + (index - 1)) * self.bytes_per_char
        try:
            with open(self.path, "rb") as fp:
                fp.seek(offset)
                data = fp.read(self.bytes_per_char)
            if len(data) == self.bytes_per_char:
                return data
        except Exception:
            return None
        return None

    def _gb2312(self, char):
        mapped = GB2312_OVERRIDES.get(ord(char))
        if mapped:
            return mapped
        try:
            encoded = char.encode("gb2312")
            if len(encoded) == 2:
                return encoded
        except Exception:
            pass
        return self._gb2312_from_table(char)

    def _gb2312_from_table(self, char):
        if not self.map_path:
            return None
        code = ord(char)
        if code > 0xFFFF:
            return None
        cached = self._map_cache.get(code)
        if cached:
            return cached
        try:
            import os

            size = os.stat(self.map_path)[6]
            low = 0
            high = size // 4 - 1
            with open(self.map_path, "rb") as fp:
                while low <= high:
                    mid = (low + high) // 2
                    fp.seek(mid * 4)
                    data = fp.read(4)
                    if len(data) != 4:
                        return None
                    current = (data[0] << 8) | data[1]
                    if current == code:
                        mapped = bytes((data[2], data[3]))
                        if len(self._map_cache) < 64:
                            self._map_cache[code] = mapped
                        return mapped
                    if current < code:
                        low = mid + 1
                    else:
                        high = mid - 1
        except Exception:
            return None
        return None

    def _find_path(self):
        for path in self.paths:
            try:
                with open(path, "rb") as fp:
                    fp.read(1)
                return path
            except Exception:
                pass
        return None

    def _find_map_path(self):
        for path in self.map_paths:
            try:
                with open(path, "rb") as fp:
                    fp.read(1)
                return path
            except Exception:
                pass
        return None
