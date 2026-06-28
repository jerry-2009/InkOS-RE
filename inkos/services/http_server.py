from inkos.services.http_request import Request


class HttpServer:
    def __init__(self, logger, ssid="InkOS-File", password="12345678"):
        self.logger = logger
        self.ssid = ssid
        self.password = password
        self.enabled = False
        self.status = "off"
        self.ip = ""
        self._socket = None
        self._routes = {}
        self._route_titles = {}

    def route(self, path, handler, methods=("GET", "POST"), title=None):
        self._routes[path] = (handler, methods)
        if title:
            self._route_titles[path] = title

    def route_title(self, path):
        return self._route_titles.get(path, path)

    def set_enabled(self, enabled):
        if enabled:
            return self.start_ap()
        self.stop()
        return True

    def start_ap(self):
        try:
            import network
            import socket

            ap = network.WLAN(network.AP_IF)
            ap.active(True)
            ap.config(essid=self.ssid, password=self.password, authmode=network.AUTH_WPA_WPA2_PSK)
            self.ip = ap.ifconfig()[0]
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("0.0.0.0", 80))
            sock.listen(1)
            sock.setblocking(False)
            self._socket = sock
            self.enabled = True
            self.status = "on"
            self.logger.info("http server http://%s/ ssid=%s" % (self.ip, self.ssid))
            return True
        except Exception as exc:
            self.enabled = False
            self.status = "failed"
            self.logger.exception("http server start failed", exc)
            return False

    def stop(self):
        try:
            if self._socket:
                self._socket.close()
        except Exception:
            pass
        self._socket = None
        self.enabled = False
        self.status = "off"
        try:
            import network

            network.WLAN(network.AP_IF).active(False)
        except Exception:
            pass

    def poll(self):
        if not self.enabled or not self._socket:
            return
        try:
            conn, _addr = self._socket.accept()
        except Exception:
            return
        try:
            conn.settimeout(8)
            self._handle(conn)
        except Exception as exc:
            self.logger.exception("http request failed", exc)
        try:
            conn.close()
        except Exception:
            pass

    def status_text(self):
        if self.status == "on":
            return self.ip or "已开启"
        if self.status == "failed":
            return "失败"
        return "关闭"

    def _handle(self, conn):
        head, rest = self._read_headers(conn)
        if not head:
            return
        lines = head.decode("utf-8").split("\r\n")
        parts = lines[0].split(" ")
        method = parts[0]
        target = parts[1] if len(parts) > 1 else "/"
        headers = self._headers(lines[1:])
        path, query = self._split_query(target)
        rest = self._read_form_body(conn, headers, rest)
        handler_info = self._routes.get(path)
        if not handler_info:
            self.send(conn, "404 Not Found", "text/plain", "not found")
            return
        handler, methods = handler_info
        if method not in methods:
            self.send(conn, "405 Method Not Allowed", "text/plain", "method not allowed")
            return
        request = Request(method, path, query, headers, rest, self)
        response = handler(request, conn)
        if response:
            self.respond(conn, response)

    def _read_headers(self, conn):
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = conn.recv(512)
            if not chunk:
                break
            data += chunk
            if len(data) > 4096:
                break
        parts = data.split(b"\r\n\r\n", 1)
        if len(parts) == 1:
            return data, b""
        return parts[0], parts[1]

    def _headers(self, lines):
        headers = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.lower()] = value.strip()
        return headers

    def _read_form_body(self, conn, headers, body):
        content_type = headers.get("content-type", "")
        if not content_type.startswith("application/x-www-form-urlencoded"):
            return body
        try:
            length = int(headers.get("content-length", "0") or "0")
        except Exception:
            return body
        if length <= len(body) or length > 16384:
            return body
        while len(body) < length:
            chunk = conn.recv(min(512, length - len(body)))
            if not chunk:
                break
            body += chunk
        return body

    def respond(self, conn, response):
        status, content_type, body = response
        if content_type == "redirect":
            self.redirect(conn, body)
        else:
            self.send(conn, status, content_type, body)

    def send(self, conn, status, content_type, body):
        if isinstance(body, str):
            body = body.encode("utf-8")
        header = "HTTP/1.0 %s\r\nContent-Type: %s\r\nContent-Length: %d\r\n\r\n" % (status, content_type, len(body))
        conn.send(header.encode())
        conn.send(body)

    def redirect(self, conn, location):
        conn.send(("HTTP/1.0 302 Found\r\nLocation: %s\r\n\r\n" % location).encode())

    def html_head(self):
        return """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<style>
body{font-family:system-ui;margin:0;background:#f4f4f4;color:#111}main{max-width:720px;margin:auto;padding:14px}
h2{margin:8px 0 12px}nav{display:flex;gap:8px;margin-bottom:10px}a{color:#111;text-decoration:none}
nav a,.btn,button{background:#111;color:white;border:0;border-radius:8px;padding:10px 14px;display:inline-block}
.card,.row{background:white;border:1px solid #ddd;border-radius:10px;margin:8px 0;padding:12px}
.path{font-family:monospace;word-break:break-all;margin-bottom:10px}.row{display:flex;gap:10px;align-items:center}
.row span{flex:1;word-break:break-all}.row b{font-size:12px;color:#555;min-width:34px}
.danger{color:#b00020}input,button{font-size:16px;max-width:100%;box-sizing:border-box}label{display:block;margin:10px 0 4px}input{width:100%;padding:10px;border:1px solid #ccc;border-radius:8px}.hint{color:#555;font-size:14px;line-height:1.5}
</style></head><body>"""

    def page(self, body):
        return self.html_head() + body + "</body></html>"

    def param(self, query, key):
        prefix = key + "="
        for part in query.split("&"):
            if part.startswith(prefix):
                return self.url_decode(part[len(prefix):])
        return None

    def url_decode(self, value):
        data = bytearray()
        index = 0
        while index < len(value):
            char = value[index]
            if char == "+":
                data.append(32)
                index += 1
                continue
            if char == "%" and index + 2 < len(value):
                try:
                    data.append(int(value[index + 1:index + 3], 16))
                    index += 3
                    continue
                except Exception:
                    pass
            try:
                encoded = char.encode("utf-8")
            except Exception:
                encoded = bytes((ord(char) & 0xFF,))
            data.extend(encoded)
            index += 1
        try:
            return data.decode("utf-8")
        except Exception:
            return data.decode()

    def split_query(self, target):
        return self._split_query(target)

    def _split_query(self, target):
        if "?" in target:
            return target.split("?", 1)
        return target, ""
