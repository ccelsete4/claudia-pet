"""claudia-pet Linux 版入口（对应 Windows 版 app/src/Program.cs）。

  claudia-pet                       打开（已经开着就让她回到默认位置）
  claudia-pet --toggle              藏起来 / 再按一次出来（GNOME 自定义快捷键调的就是这个）
  claudia-pet --show | --quit       叫出来 / 退出
  claudia-pet --ensure              给 Claude 用：没开就打开（Claude Code 插件、桌面端 MCP 调）
  claudia-pet --mcp                 给 Claude 桌面端用的 MCP 服务（stdio）
  claudia-pet --connect [plugin|mcp|gnome|all] / --disconnect [...]   接入 / 撤销（gnome = 跟着 Claude 窗口的 GNOME 扩展）
  claudia-pet --pet 2 [--mode desktop|claude]                   多开的那几只，由第一只带起来
"""
import faulthandler
import os
import sys

# 进程被 C 层面的错误弄死时（段错误、glibc 报 corrupted double-linked list 后中止）把当时每个线程正在跑的
# Python 调用栈打到 stderr（~/.claudia/stderr.log）。2026-11-22 拖动后崩过好几次，没留下别的线索
faulthandler.enable()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from claudia import claude, store  # noqa: E402

MENU_CSS = b"""
window.claudia-pet, window.claudia-pet > * { background-color: transparent; }
menu.claudia-menu, .claudia-menu menu { border-radius: 10px; padding: 4px 0; }
menu.claudia-menu menuitem, .claudia-menu menu menuitem { padding: 6px 14px; border-radius: 6px; margin: 0 4px; }
menu.claudia-menu menuitem:hover, .claudia-menu menu menuitem:hover { background-color: #fde3cf; color: #3b2a20; }
"""


def arg_after(args, flag):
    i = args.index(flag)
    return args[i + 1] if i + 1 < len(args) else None


def choose_run_mode(fresh, by_claude):
    """还没选过运行方式时选一次：第一次用、自己打开、又没接入 Claude 的，才设成「独立运行」"""
    try:
        connected = claude.connected()
    except Exception:
        connected = False
    standalone = fresh and not by_claude and not connected
    store.set_standalone(standalone)
    if standalone and "mode" not in store.settings:
        store.settings["mode"] = "desktop"
        store.save_settings()
    store.log(f"运行方式：{'独立运行' if standalone else '跟着 Claude'}（第一次用 = {fresh}，Claude 叫出来的 = {by_claude}，已接入 Claude = {connected}）")


SESSION_VARS = ("DISPLAY", "XAUTHORITY", "WAYLAND_DISPLAY", "XDG_RUNTIME_DIR", "DBUS_SESSION_BUS_ADDRESS",
                "XDG_SESSION_TYPE", "XDG_CURRENT_DESKTOP")


def fill_session_env(override=False):
    """Claude 桌面端随登录自启时，交给 MCP 的环境里可能还没有 DISPLAY、XAUTHORITY：从 systemd 用户会话里补上"""
    import glob
    import subprocess
    run = f"/run/user/{os.getuid()}"
    if not os.environ.get("XDG_RUNTIME_DIR") and os.path.isdir(run):
        os.environ["XDG_RUNTIME_DIR"] = run
    if not os.environ.get("DBUS_SESSION_BUS_ADDRESS") and os.path.exists(run + "/bus"):
        os.environ["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={run}/bus"
    try:
        out = subprocess.run(["systemctl", "--user", "show-environment"], capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.SubprocessError):
        out = ""
    for line in out.splitlines():
        k, _, v = line.partition("=")
        if k in SESSION_VARS and v and (override or not os.environ.get(k)):
            os.environ[k] = v
    if not os.environ.get("DISPLAY") and os.path.exists("/tmp/.X11-unix/X0"):
        os.environ["DISPLAY"] = ":0"
    if not os.environ.get("XAUTHORITY"):
        auth = sorted(glob.glob(run + "/.mutter-Xwaylandauth.*"), key=os.path.getmtime)
        if auth:
            os.environ["XAUTHORITY"] = auth[-1]


def x_display_ok():
    import ctypes
    import ctypes.util
    try:
        x = ctypes.CDLL(ctypes.util.find_library("X11") or "libX11.so.6")
        x.XOpenDisplay.restype = ctypes.c_void_p
        x.XOpenDisplay.argtypes = [ctypes.c_char_p]
        x.XCloseDisplay.argtypes = [ctypes.c_void_p]
        d = x.XOpenDisplay(None)
        if d:
            x.XCloseDisplay(d)
            return True
    except OSError:
        pass
    return False


def wait_for_display(seconds=30):
    """连得上 XWayland 才开窗口；刚登录时可能还没好，等一会儿再试"""
    import time
    deadline = time.monotonic() + seconds
    attempt = 0
    while True:
        fill_session_env(override=attempt > 0)
        if x_display_ok():
            if attempt:
                store.log(f"等了 {attempt} 次才连上图形界面（DISPLAY={os.environ.get('DISPLAY')}）")
            return True
        attempt += 1
        if time.monotonic() > deadline:
            return False
        time.sleep(2)


def main(args):
    if "--ensure" in args:
        store.log("--ensure：" + claude.ensure())
        return 0
    if "--mcp" in args:
        claude.mcp_serve()
        return 0
    for flag, install in (("--connect", True), ("--disconnect", False)):
        if flag not in args:
            continue
        what = arg_after(args, flag) or "all"
        store.DATA.mkdir(parents=True, exist_ok=True)
        code = 0
        targets = ["plugin", "mcp"] + (["gnome"] if claude.gnome_session() else []) if what == "all" else [what]
        for t in targets:
            try:
                if t == "plugin":
                    msg = claude.set_plugin(install)
                elif t == "mcp":
                    msg = claude.set_mcp(install)
                elif t == "gnome":
                    msg = claude.set_gnome_extension(install)
                else:
                    raise ValueError("不认识：" + t)
            except Exception as e:
                code = 1
                msg = "没有完成：" + str(e)
            store.log(f"{flag} {t}：{msg}".replace("\n", " "))
            print(f"[{t}] {msg}")
        return code
    for flag in ("--toggle", "--show", "--quit"):
        if flag in args:
            if claude.send_command(flag[2:]):
                return 0
            if flag != "--show":
                print(store.APP_NAME + " 没在运行", file=sys.stderr)
                return 1
            break   # --show 而她没开：照常打开

    first_mode = None
    if "--pet" in args:
        pid = arg_after(args, "--pet")
        if not store.valid_pet_id(pid):
            return 2
        store.pet_id = pid
        if "--mode" in args and arg_after(args, "--mode") in ("desktop", "claude"):
            first_mode = arg_after(args, "--mode")

    main_pet = store.is_main()
    lock = claude.take_lock(store.pet_id)
    if lock is None:
        if main_pet:
            claude.send_command("show")
        return 0
    if not main_pet and not claude.pet_running("main"):
        store.log("第一只没在跑，不单独打开")
        return 0

    os.environ.setdefault("GDK_BACKEND", "x11")   # Wayland 下普通窗口摆不了位置、置不了顶：走 XWayland
    if not wait_for_display():
        store.log(f"打不开图形界面：DISPLAY={os.environ.get('DISPLAY')!r}，XAUTHORITY={os.environ.get('XAUTHORITY')!r}")
        print(store.APP_NAME + "：打不开图形界面", file=sys.stderr)
        return 1
    if not os.environ.get("CLAUDIA_DEBUG"):
        # WebKit、EGL、托盘库的警告（虚拟机里没有 3D 加速时一大串）不往终端刷：写进 ~/.claudia/stderr.log
        try:
            store.DATA.mkdir(parents=True, exist_ok=True)
            err = store.DATA / "stderr.log"
            if err.exists() and err.stat().st_size > 1_000_000:
                err.unlink()
            fd = os.open(err, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            os.dup2(fd, 2)
            os.close(fd)
        except OSError:
            pass
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, GLib, Gtk

    from claudia import system
    from claudia.pet import Pet

    store.pet_dir().mkdir(parents=True, exist_ok=True)
    if main_pet:
        try:
            claude.USER_QUIT_FLAG.unlink()   # 自己打开了：恢复跟着 Claude 出现
        except OSError:
            pass
        store.STATE.mkdir(parents=True, exist_ok=True)
        (store.STATE / "pet.pid").write_text(str(os.getpid()))
        Pet.clear_signal()
    store.log(f"启动 {store.version()}，{os.uname().sysname} {os.uname().release}，"
              f"会话 {os.environ.get('XDG_SESSION_TYPE', '?')}，GDK {os.environ.get('GDK_BACKEND')}")
    fresh = main_pet and not (store.DATA / "settings.json").exists()
    store.load_settings()
    if first_mode and "mode" not in store.settings:
        store.settings["mode"] = first_mode
        store.save_settings()
    if main_pet and not store.has_run_mode():
        choose_run_mode(fresh, claude.BY_CLAUDE_ARG in args)

    if not Gtk.init_check(sys.argv[:1])[0]:
        store.log(f"GTK 打不开图形界面：DISPLAY={os.environ.get('DISPLAY')!r}")
        print(store.APP_NAME + "：打不开图形界面", file=sys.stderr)
        return 1
    css = Gtk.CssProvider()
    css.load_from_data(MENU_CSS)
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    pet = Pet()
    pet.start()
    srv = system.serve(claude.socket_path(store.pet_id), pet.on_command)
    try:
        gi.require_version("GLibUnix", "2.0")
        from gi.repository import GLibUnix
        signal_add = GLibUnix.signal_add
    except (ValueError, ImportError):
        signal_add = GLib.unix_signal_add
    for sig in (2, 15):   # SIGINT、SIGTERM：好好退出
        signal_add(GLib.PRIORITY_DEFAULT, sig, lambda *_: (pet.quit(), False)[1])
    if main_pet:
        for pid in store.extra_pets():   # 把上次多开的几只也叫出来
            GLib.timeout_add(1500, lambda p=pid: (Pet.launch_pet(p), False)[1])
    Gtk.main()
    srv.close()
    for f in (claude.socket_path(store.pet_id), store.STATE / "pet.pid" if main_pet else None):
        if f:
            try:
                f.unlink()
            except OSError:
                pass
    store.log("退出")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
