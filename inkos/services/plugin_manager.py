import os
import sys

try:
    import ujson as json
except ImportError:
    import json


class AppInfo:
    def __init__(self, app_id, name, path, entry, source, factory=None, icon=None, permissions=None, category="app", autostart=False):
        self.app_id = app_id
        self.name = name
        self.path = path
        self.entry = entry
        self.source = source
        self.factory = factory
        self.icon = icon
        self.permissions = permissions or ()
        self.category = category or "app"
        self.autostart = bool(autostart)


class PluginManager:
    def __init__(self, logger):
        self.logger = logger
        self.apps = []

    def discover(self):
        self.apps = []
        self._scan_root("/apps", "flash")
        self._scan_root("/plugins", "system")
        self._scan_root("/sd/plugins", "sd")
        self.apps.sort(key=lambda item: (item.category, item.source, item.name.lower()))
        return self.apps

    def _scan_root(self, root, source):
        root = self._resolve_root(root)
        try:
            names = os.listdir(root)
        except OSError:
            return

        for name in names:
            path = self._join(root, name)
            manifest_path = self._join(path, "manifest.json")
            try:
                with open(manifest_path, "r") as fp:
                    manifest = json.load(fp)
            except Exception as exc:
                self.logger.exception("skip app manifest %s" % manifest_path, exc)
                continue

            app_id = manifest.get("id") or name
            display_name = manifest.get("name") or app_id
            entry = manifest.get("entry") or "main.py"
            permissions = tuple(manifest.get("permissions") or ())
            category = manifest.get("category") or "app"
            autostart = bool(manifest.get("autostart", False))
            icon = self._load_icon(path, manifest.get("icon"))
            if ".." in entry or entry.startswith("/"):
                self.logger.error("skip unsafe app entry %s" % app_id)
                continue

            self.apps.append(AppInfo(app_id, display_name, path, entry, source, icon=icon, permissions=permissions, category=category, autostart=autostart))

    def find(self, app_id):
        for app in self.apps:
            if app.app_id == app_id:
                return app
        return None

    def _load_icon(self, app_path, icon_path):
        from inkos.ui.icons import ICON_APP, load_icon

        if not icon_path:
            return ICON_APP
        if ".." in icon_path or icon_path.startswith("/"):
            return ICON_APP
        return load_icon(self._join(app_path, icon_path)) or ICON_APP

    def load(self, app_info, context):
        if app_info.factory:
            return app_info.factory(context)

        module_name = "_inkos_app_" + app_info.app_id.replace(".", "_").replace("-", "_")
        entry_path = self._join(app_info.path, app_info.entry)
        try:
            if app_info.path not in sys.path:
                sys.path.insert(0, app_info.path)
            namespace = self._load_module(module_name, entry_path)
            create_app = namespace["create_app"]
            app = create_app(context)
            app.app_id = getattr(app, "app_id", None) or app_info.app_id
            app.name = getattr(app, "name", None) or app_info.name
            return app
        except Exception as exc:
            self.logger.exception("load app %s failed" % app_info.app_id, exc)
            raise
        finally:
            try:
                sys.path.remove(app_info.path)
            except ValueError:
                pass

    def _load_module(self, module_name, entry_path):
        with open(entry_path, "rb") as fp:
            source = fp.read().decode("utf-8")
        namespace = {
            "__name__": module_name,
            "__file__": entry_path,
        }
        exec(compile(source, entry_path, "exec"), namespace)
        return namespace

    def _resolve_root(self, root):
        local_root = root[1:] if root.startswith("/") else root
        try:
            os.listdir(local_root)
            return local_root
        except OSError:
            pass

        try:
            os.listdir(root)
            return root
        except OSError:
            return root

    def _join(self, left, right):
        if left.endswith("/") or left.endswith("\\"):
            return left + right
        return left + "/" + right
