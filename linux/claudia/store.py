"""目录、设置、日志、内置素材同步、角色清单（对应 Windows 版 app/src/Store.cs）。

数据目录和 Windows 版一样是 ~/.claudia：Claude Code 插件往 ~/.claudia/state 写状态，两边的插件代码共用。
"""
import json
import os
import shutil
import sys
import time
import urllib.parse
from pathlib import Path

APP_NAME = "claudia-pet"
# 网页从两个「主机」读文件：claudia://app/（安装目录/web）和 claudia://data/characters/…（数据目录里的立绘），见 web.py
SCHEME = "claudia"
APP_HOST, DATA_HOST = "app", "data"
ANIM_DIR = "anim"


def _env(name):
    v = os.environ.get(name, "").strip()
    return v or None


# 安装目录：linux/claudia/store.py 往上两级（开发时就是仓库根目录，装好后是 ~/.local/share/claudia-pet）
INSTALL = Path(__file__).resolve().parent.parent.parent
DATA = Path(_env("CLAUDIA_DATA_DIR") or Path.home() / ".claudia")
STATE = Path(_env("CLAUDIA_STATE_DIR") or DATA / "state")
CHARACTERS = DATA / "characters"
RUN = DATA / "run"   # 单实例锁和控制用的 socket


def page_url(page):
    return f"{SCHEME}://{APP_HOST}/{page}"


def version():
    try:
        return (INSTALL / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return "0"


def launcher():
    """自己的启动命令（多开、--ensure、MCP 配置里都用它）。装好后是 ~/.local/bin/claudia-pet，开发时是仓库里的 linux/claudia-pet"""
    exe = _env("CLAUDIA_EXE")
    if exe:
        return exe
    return str(INSTALL / "linux" / "claudia-pet")


# ---------------- JSON / 日志 ----------------
def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def read_json(path):
    text = read_text(path)
    if text is None:
        return None
    try:
        v = json.loads(text.lstrip("﻿"))
    except ValueError:
        return None
    return v if isinstance(v, dict) else None


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def dumps(v):
    return json.dumps(v, ensure_ascii=False)


def changed_state(path, stamps, *, max_bytes, not_before=None):
    """Read a changed plugin file. A partial write is retried on the next poll."""
    try:
        stat = path.stat()
    except OSError:
        stamps.pop(path, None)
        return None
    if stat.st_size > max_bytes or not_before is not None and stat.st_mtime < not_before:
        stamps.pop(path, None)
        return None
    stamp = stat.st_mtime_ns, stat.st_size
    if stamps.get(path) == stamp:
        return None
    value = read_json(path)
    if value is None:
        return None
    stamps[path] = stamp
    return value, stat.st_mtime


pet_id = "main"


def is_main():
    return pet_id == "main"


def log(text):
    try:
        DATA.mkdir(parents=True, exist_ok=True)
        f = DATA / "linux.log"
        if f.exists() and f.stat().st_size > 1_000_000:
            f.unlink()
        with open(f, "a", encoding="utf-8") as out:
            out.write(time.strftime("%Y-%m-%d %H:%M:%S ") + ("" if is_main() else f"[{pet_id}] ") + str(text) + "\n")
    except OSError:
        pass
    if os.environ.get("CLAUDIA_DEBUG"):
        print(text, file=sys.stderr)


# ---------------- 多开 ----------------
# 每只是一个独立进程：第一只叫 main，多开的由它带起来（claudia-pet --pet 2）。各有各的设置文件和网页数据目录
MAX_EXTRA_PETS = 4


def pet_dir():
    return DATA if is_main() else DATA / "pets" / pet_id


def webview_dir():
    return pet_dir() / "webkit"


def valid_pet_id(i):
    return bool(i) and 1 <= len(i) <= 8 and i != "main" and all(c.isdigit() or "a" <= c <= "z" for c in i)


PETS_FILE = DATA / "pets.json"


def extra_pets():
    d = read_json(PETS_FILE)
    ids = d.get("ids") if d else None
    out = []
    for i in ids if isinstance(ids, list) else []:
        if isinstance(i, str) and valid_pet_id(i) and i not in out:
            out.append(i)
    return out[:MAX_EXTRA_PETS]


def save_extra_pets(ids):
    write_json(PETS_FILE, {"ids": list(ids)})


# ---------------- 设置 ----------------
settings = {}


def settings_file():
    return pet_dir() / "settings.json"


def load_settings():
    global settings
    own = read_json(settings_file())
    if own is None and not is_main():
        # 新来的一只：先照第一只的设置（大小、手感这些），位置、待在哪、名字用自己的
        own = read_json(DATA / "settings.json") or {}
        for k in ("follow", "desk", "mode", "names"):
            own.pop(k, None)
    settings = own or {}
    if not isinstance(settings.get("names"), dict):
        settings["names"] = {}


def save_settings():
    try:
        write_json(settings_file(), settings)
    except OSError as e:
        log("保存设置失败: " + str(e))


def flag(key):
    return settings.get(key) is True


def setting_on(key):
    """没存过算开"""
    v = settings.get(key)
    return not isinstance(v, bool) or v


def names():
    return settings["names"]


# ---------------- 运行方式：跟着 Claude / 独立运行（所有几只共用 run.json） ----------------
RUN_FILE = DATA / "run.json"
_standalone = False
_run_stamp = None
_run_checked = 0.0


def has_run_mode():
    return RUN_FILE.exists()


def standalone():
    """按 run.json 的修改时间缓存，最多一秒看一次：别的那只改了，这一只一秒内跟上"""
    global _standalone, _run_stamp, _run_checked
    now = time.monotonic()
    if now - _run_checked < 1:
        return _standalone
    _run_checked = now
    try:
        stamp = RUN_FILE.stat().st_mtime_ns if RUN_FILE.exists() else None
        if stamp != _run_stamp:
            _run_stamp = stamp
            d = read_json(RUN_FILE)
            _standalone = bool(d) and d.get("mode") == "standalone"
    except OSError:
        pass
    return _standalone


def set_standalone(on):
    global _standalone, _run_checked
    try:
        write_json(RUN_FILE, {"mode": "standalone" if on else "claude"})
    except OSError as e:
        log("保存运行方式失败: " + str(e))
    _standalone = on
    _run_checked = 0.0


# ---------------- 内置素材同步 ----------------
# 安装目录里的 characters 同步到数据目录（用户可以在那里改立绘）；只在有变化时复制
def _same_file(src, dst):
    try:
        a, b = src.stat(), dst.stat()
    except OSError:
        return False
    return a.st_size == b.st_size and int(a.st_mtime) == int(b.st_mtime)


def _resource_dirs(path):
    return [d for d in sorted(path.iterdir()) if d.is_dir() and d.name.lower() != "raw"]


def _same_resources(src, dst):
    if not dst.is_dir():
        return False
    files = [f for f in src.iterdir() if f.is_file()]
    if len(files) != len([f for f in dst.iterdir() if f.is_file()]):
        return False
    if any(not _same_file(f, dst / f.name) for f in files):
        return False
    dirs = _resource_dirs(src)
    if len(dirs) != len([d for d in dst.iterdir() if d.is_dir()]):
        return False
    return all(_same_resources(d, dst / d.name) for d in dirs)


def _copy_dir(src, dst):
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.iterdir():
        if f.is_file():
            shutil.copy2(f, dst / f.name)
    for d in _resource_dirs(src):
        _copy_dir(d, dst / d.name)


def sync_resources():
    CHARACTERS.mkdir(parents=True, exist_ok=True)
    STATE.mkdir(parents=True, exist_ok=True)
    src = INSTALL / "characters"
    if not src.is_dir() or src.resolve() == CHARACTERS.resolve():
        return
    for d in sorted(src.iterdir()):
        if not d.is_dir():
            continue
        dst = CHARACTERS / d.name
        try:
            work = DATA / "builtin-resource-sync" / d.name
            staged, previous = work / "next", work / "previous"
            if previous.exists():
                if dst.exists():
                    shutil.rmtree(previous)
                else:
                    os.replace(previous, dst)
            if staged.exists():
                shutil.rmtree(staged)
            if _same_resources(d, dst):
                continue
            _copy_dir(d, staged)
            if dst.exists():
                os.replace(dst, previous)
            try:
                os.replace(staged, dst)
            except OSError:
                if previous.exists():
                    os.replace(previous, dst)
                raise
            if previous.exists():
                shutil.rmtree(previous)
            log("同步角色素材：" + d.name)
        except OSError as e:
            log(f"同步角色失败 {d}: {e}")
    for md in src.glob("*.md"):
        try:
            if not _same_file(md, CHARACTERS / md.name):
                shutil.copy2(md, CHARACTERS / md.name)
        except OSError as e:
            log(f"同步说明文件失败 {md}: {e}")


# ---------------- 角色清单 ----------------
def is_sprite(stem):
    return stem not in ("portrait", "portrait-card", "avatar")


def _url(cid, *parts):
    return f"{SCHEME}://{DATA_HOST}/characters/" + "/".join(urllib.parse.quote(p, safe="") for p in (cid, *parts))


def _sprites(d):
    cid = d.name
    poses, blink, blink_base = {}, None, None
    files = sorted((f for f in d.iterdir() if f.is_file() and f.suffix.lower() in (".webp", ".png")), key=lambda f: f.name)
    for f in files:
        stem = f.stem
        if not is_sprite(stem):
            continue
        url = _url(cid, f.name)
        if stem == "idle-blink":
            blink = url
            continue
        if stem == "idle":
            blink_base = url
        poses.setdefault(stem.split("-")[0], []).append(url)
    return poses, blink, blink_base


def _sheets(d):
    anim = d / ANIM_DIR
    if not anim.is_dir():
        return {}
    return {f.stem: _url(d.name, ANIM_DIR, f.name) for f in sorted(anim.glob("*.webp"), key=lambda f: f.name)}


def manifest():
    chars = {}
    if CHARACTERS.is_dir():
        for d in sorted((x for x in CHARACTERS.iterdir() if x.is_dir()), key=lambda x: x.name):
            info = read_json(d / "character.json")
            if info is None:
                continue
            poses, blink, blink_base = _sprites(d)
            sheets = _sheets(d)
            if "idle" not in poses and "default" not in poses:
                animations = info.get("animations")
                idle = animations.get("idle") if isinstance(animations, dict) else None
                idle_sheets = idle.get("sheets") if isinstance(idle, dict) else None
                if not isinstance(idle_sheets, list) or not any(
                    isinstance(name, str) and name in sheets for name in idle_sheets
                ):
                    continue
            custom = names().get(d.name)
            if isinstance(custom, str) and custom.strip():
                info["name"] = custom.strip()
            info.update(poses=poses, blink=blink, blinkBase=blink_base, sheets=sheets)
            chars[d.name] = info
    return {"characters": chars}


def resolve_sprite(path):
    """claudia://data/characters/<角色>/<图> 或 …/<角色>/anim/<图> → 文件。只给 .webp / .png，别的一律不给"""
    parts = path.split("/")
    anim = len(parts) == 5 and parts[3] == ANIM_DIR
    if (len(parts) != 4 and not anim) or parts[0] != "" or parts[1] != "characters":
        return None
    character, name = urllib.parse.unquote(parts[2]), urllib.parse.unquote(parts[-1])
    for seg in (character, name):
        if not seg or seg in (".", "..") or "/" in seg or "\\" in seg or "\0" in seg:
            return None
    ext = os.path.splitext(name)[1].lower()
    if ext not in (".webp", ".png"):
        return None
    root = CHARACTERS.resolve()
    full = (root / character / ANIM_DIR / name) if anim else (root / character / name)
    full = full.resolve()
    if root not in full.parents:
        return None
    return full, ("image/webp" if ext == ".webp" else "image/png")
