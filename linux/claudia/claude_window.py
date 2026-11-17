"""收 GNOME Shell 扩展（linux/gnome-extension/）报来的 Claude 窗口状态。

Wayland 下桌宠自己看不到 Claude 的窗口：扩展在会话总线上提供 io.github.kirito1207.ClaudiaPet，
GetState() 给当前状态，StateChanged(s) 在 Claude 窗口挪动、改大小、最小化、换工作区、被别的窗口盖住时广播。
状态是 JSON：{protocol, found, rect: [x, y, w, h], minimized, onWorkspace, visible, fullscreen, focused, scale, covers: [[x, y, w, h], …]}
扩展没装、没启用、GNOME 版本不认它时，available 是 False，桌宠就待在桌面上。
"""
import json

from gi.repository import Gio, GLib

from . import store

BUS_NAME = "io.github.kirito1207.ClaudiaPet"
OBJECT_PATH = "/io/github/kirito1207/ClaudiaPet"
INTERFACE = "io.github.kirito1207.ClaudiaPet"
EXTENSION_UUID = "claudia-pet@kirito1207.github.io"


def _parse(text):
    try:
        v = json.loads(text)
    except (TypeError, ValueError):
        return None
    return v if isinstance(v, dict) else None


class ClaudeWindowWatch:
    def __init__(self, on_change):
        """on_change(watch)：状态变了（含扩展出现 / 消失）时调，读 watch.available、watch.state"""
        self.on_change = on_change
        self.available = False
        self.state = None
        try:
            self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        except GLib.Error as e:
            store.log("连不上会话总线，跟不了 Claude 窗口: " + e.message)
            self.bus = None
            return
        self.fetch_sync()
        self.bus.signal_subscribe(BUS_NAME, INTERFACE, "StateChanged", OBJECT_PATH, None,
                                  Gio.DBusSignalFlags.NONE, self._on_signal)
        Gio.bus_watch_name_on_connection(self.bus, BUS_NAME, Gio.BusNameWatcherFlags.NONE,
                                         self._on_appeared, self._on_vanished)

    def fetch_sync(self):
        """启动时先同步问一次：一开始就知道该待在 Claude 窗口里还是桌面上，不先在别处出现再跳过去"""
        try:
            r = self.bus.call_sync(BUS_NAME, OBJECT_PATH, INTERFACE, "GetState", None, GLib.VariantType("(s)"),
                                   Gio.DBusCallFlags.NO_AUTO_START, 500, None)
            self.state = _parse(r.unpack()[0])
            self.available = self.state is not None
        except GLib.Error:
            self.available, self.state = False, None
        return self.available

    def _changed(self):
        try:
            self.on_change(self)
        except Exception as e:
            store.log("处理 Claude 窗口状态出错: " + repr(e))

    def _on_signal(self, _conn, _sender, _path, _iface, _signal, params):
        state = _parse(params.unpack()[0])
        if state is None:
            return
        self.available, self.state = True, state
        self._changed()

    def _on_appeared(self, *_):
        if self.available:
            return
        store.log("GNOME 扩展在了：可以跟着 Claude 窗口")
        self.fetch_sync()
        self._changed()

    def _on_vanished(self, *_):
        if not self.available and self.state is None:
            return
        store.log("GNOME 扩展不在了（没启用、没装或 GNOME 不认它）：待在桌面上")
        self.available, self.state = False, None
        self._changed()
