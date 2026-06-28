from inkos.services.http_request import Response


class FileManagerWeb:
    def __init__(self):
        self.http = None

    def register(self, http):
        self.http = http
        http.route("/", self.index, ("GET",))
        http.route("/upload", self.upload, ("POST",))
        http.route("/download", self.download, ("GET",))
        http.route("/delete", self.delete, ("GET",))

    def index(self, request, conn=None):
        import os

        root = request.param("root", "/sd")
        if root not in ("/sd", "/"):
            root = "/sd"
        path = self._safe_path(root, request.param("path", root))
        try:
            names = os.listdir(path)
        except Exception:
            names = []
        body = ["<main><h2>InkOS File</h2>"]
        body.append("<nav><a href='/?root=/sd'>SD</a><a href='/?root=/'>Flash</a></nav>")
        body.append("<section class='card'><div class='path'>%s</div>" % path)
        body.append("<a class='btn' href='/?root=%s&path=%s'>Parent</a></section>" % (root, self._parent(path, root)))
        body.append("<section class='card'><h3>Apps</h3>")
        for route in self.http._routes:
            if route.startswith("/app/"):
                body.append("<a class='btn' href='%s'>%s</a> " % (route, self.http.route_title(route)))
        body.append("</section><section class='card'><h3>Upload</h3>")
        body.append("<form action='/upload?path=%s' method='post' enctype='multipart/form-data'>" % path)
        body.append("<input type='file' name='file' multiple><button>Upload</button></form></section>")
        body.append("<section class='list'>")
        for name in names:
            full = self._join(path, name)
            if self._is_dir(full):
                body.append("<a class='row' href='/?root=%s&path=%s'><b>DIR</b><span>%s</span></a>" % (root, full, name))
            else:
                body.append("<div class='row'><b>FILE</b><span>%s</span><a href='/download?path=%s'>Down</a><a class='danger' href='/delete?path=%s'>Del</a></div>" % (name, full, full))
        body.append("</section></main>")
        return Response.html(self.http.page("\n".join(body)))

    def upload(self, request, conn):
        target_dir = self._safe_path("/", request.param("path", "/sd"))
        length = int(request.headers.get("content-length", "0") or "0")
        boundary = self._boundary(request.headers.get("content-type", ""))
        if not boundary:
            return Response.text("missing boundary", "400 Bad Request")
        self._save_multipart_stream(conn, request.body, length - len(request.body), boundary, target_dir)
        return Response.redirect("/?path=%s" % target_dir)

    def download(self, request, conn=None):
        path = self._safe_path("/", request.param("path", ""))
        try:
            with open(path, "rb") as fp:
                return ("200 OK", "application/octet-stream", fp.read())
        except Exception:
            return Response.text("not found", "404 Not Found")

    def delete(self, request, conn=None):
        try:
            import os

            os.remove(self._safe_path("/", request.param("path", "")))
        except Exception:
            pass
        return Response.redirect("/")

    def _save_multipart_stream(self, conn, data, remaining, boundary, target_dir):
        marker = b"--" + boundary
        saved = 0
        while True:
            start = data.find(marker)
            if start < 0:
                more = self._recv(conn, remaining)
                if not more:
                    return saved
                data += more
                remaining -= len(more)
                continue
            data = data[start + len(marker):]
            if data.startswith(b"--"):
                return saved
            if data.startswith(b"\r\n"):
                data = data[2:]
            while b"\r\n\r\n" not in data:
                more = self._recv(conn, remaining)
                if not more:
                    return saved
                data += more
                remaining -= len(more)
            header, data = data.split(b"\r\n\r\n", 1)
            name = self._filename(header)
            if not name:
                continue
            full = self._join(target_dir, self._clean_name(name))
            end_marker = b"\r\n" + marker
            tail_keep = len(end_marker) + 4
            with open(full, "wb") as fp:
                while True:
                    pos = data.find(end_marker)
                    if pos >= 0:
                        fp.write(data[:pos])
                        data = data[pos + 2:]
                        saved += 1
                        break
                    if len(data) > tail_keep:
                        fp.write(data[:-tail_keep])
                        data = data[-tail_keep:]
                    more = self._recv(conn, remaining)
                    if not more:
                        fp.write(data)
                        return saved + 1
                    data += more
                    remaining -= len(more)

    def _recv(self, conn, remaining):
        if remaining <= 0:
            return b""
        return conn.recv(min(1024, remaining))

    def _boundary(self, content_type):
        for part in content_type.split(";"):
            part = part.strip()
            if part.startswith("boundary="):
                return part.split("=", 1)[1].encode()
        return None

    def _filename(self, header):
        try:
            text = header.decode()
            key = "filename=\""
            start = text.find(key)
            if start < 0:
                return ""
            start += len(key)
            return text[start:text.find("\"", start)]
        except Exception:
            return ""

    def _safe_path(self, root, path):
        path = self.http.url_decode(path)
        if ".." in path:
            return root
        if not path.startswith("/"):
            path = "/" + path
        return path

    def _clean_name(self, name):
        return name.replace("/", "").replace("\\", "") or "upload.bin"

    def _join(self, left, right):
        return left.rstrip("/") + "/" + right

    def _parent(self, path, root):
        if path == root:
            return root
        return path.rsplit("/", 1)[0] or root

    def _is_dir(self, path):
        try:
            import os

            os.listdir(path)
            return True
        except Exception:
            return False
