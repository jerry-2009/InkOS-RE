class Request:
    def __init__(self, method, path, query, headers, body, server):
        self.method = method
        self.path = path
        self.query = query
        self.headers = headers
        self.body = body
        self.server = server

    def param(self, key, default=None):
        value = self.server.param(self.query, key)
        return default if value is None else value

    def form(self, key, default=None):
        try:
            text = self.body.decode()
        except Exception:
            text = ""
        value = self.server.param(text, key)
        return default if value is None else value


class Response:
    @staticmethod
    def html(body):
        return ("200 OK", "text/html; charset=utf-8", body)

    @staticmethod
    def text(body, status="200 OK"):
        return (status, "text/plain; charset=utf-8", body)

    @staticmethod
    def redirect(location):
        return ("302 Found", "redirect", location)
