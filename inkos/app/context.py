class AppContext:
    def __init__(self, kernel, app_id, app_dir=None, source="flash"):
        self.kernel = kernel
        self.app_id = app_id
        self.app_dir = app_dir
        self.source = source
        self.display = kernel.display
        self.logger = kernel.logger
        self.settings = kernel.settings
        self.http = kernel.file_transfer

    def request_render(self):
        self.kernel.render()

    def exit_app(self):
        self.kernel.back_to_launcher()
