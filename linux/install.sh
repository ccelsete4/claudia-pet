#!/bin/sh
# 给当前用户安装 claudia-pet Linux 版（不需要 root）。
#
#   sh linux/install.sh [--connect] [--no-extension] [--no-start]
#
# 程序装到 ~/.local/share/claudia-pet，命令 ~/.local/bin/claudia-pet，应用菜单里有「claudia-pet」。
# 设置、日志和立绘在 ~/.claudia，重装不会丢。
# --connect 同时接入 Claude Code 插件和 Claude 桌面端（MCP）；不加的话之后在右键「设置…」→「接入 Claude」里接入。
# GNOME 桌面上还会装一个 GNOME Shell 扩展（让她能待在 Claude 窗口里），注销电脑、重新登录一次后生效；
# --no-extension 不装它（她就只待在桌面上）。
# 不加开机自启：接入后由 Claude 把她叫出来。
set -eu

SRC=$(cd "$(dirname "$0")/.." && pwd)
DST="${XDG_DATA_HOME:-$HOME/.local/share}/claudia-pet"
BIN="$HOME/.local/bin"
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
CONNECT=0
START=1
EXTENSION=1
for a in "$@"; do
  case "$a" in
    --connect) CONNECT=1 ;;
    --no-start) START=0 ;;
    --no-extension) EXTENSION=0 ;;
    *) echo "不认识的参数：$a" >&2; exit 2 ;;
  esac
done

# ---- 依赖：Python 3 的 GTK 3 和 WebKitGTK 4.1 绑定（Ubuntu 桌面版自带）；托盘要另装一个小包 ----
if ! python3 -I -c 'import gi; gi.require_version("Gtk", "3.0"); gi.require_version("WebKit2", "4.1"); from gi.repository import Gtk, WebKit2' 2>/dev/null; then
  echo "缺少运行库，请先装：" >&2
  echo "  sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1 libnotify-bin gir1.2-notify-0.7" >&2
  exit 1
fi
if ! python3 -I -c 'import gi; gi.require_version("AyatanaAppIndicator3", "0.1"); from gi.repository import AyatanaAppIndicator3' 2>/dev/null; then
  echo "提示：没有托盘图标。想要的话装：sudo apt install gir1.2-ayatanaappindicator3-0.1"
fi

# ---- 先停掉正在跑的 ----
if [ -x "$BIN/claudia-pet" ]; then "$BIN/claudia-pet" --quit >/dev/null 2>&1 || true; sleep 1; fi
pkill -f "^python3 -I $DST/linux/claudia/main.py" 2>/dev/null || true

# ---- 复制 ----
mkdir -p "$DST" "$BIN" "$APPS"
TMP="$DST.new"
rm -rf "$TMP"
mkdir -p "$TMP/linux" "$TMP/icon"
cp -rp "$SRC/web" "$SRC/characters" "$SRC/plugin" "$TMP/"
cp -p "$SRC/VERSION" "$SRC/LICENSE" "$SRC/NOTICE.md" "$TMP/"
cp -p "$SRC/icon/AppIcon.png" "$TMP/icon/"
cp -rp "$SRC/linux/claudia" "$TMP/linux/"
cp -rp "$SRC/linux/gnome-extension" "$TMP/linux/"
cp "$SRC/linux/claudia-pet" "$SRC/linux/uninstall.sh" "$TMP/linux/"
find "$TMP" -name __pycache__ -type d -prune -exec rm -rf {} +
chmod +x "$TMP/linux/claudia-pet" "$TMP/linux/uninstall.sh"
rm -rf "$DST.old"
[ -d "$DST" ] && mv "$DST" "$DST.old"
mv "$TMP" "$DST"
rm -rf "$DST.old"
ln -sf "$DST/linux/claudia-pet" "$BIN/claudia-pet"

cat > "$APPS/claudia-pet.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=claudia-pet
Comment=Claude 娘桌宠（非官方同人项目）
Exec=$BIN/claudia-pet
Icon=$DST/icon/AppIcon.png
Terminal=false
Categories=Utility;
StartupWMClass=claudia-pet
EOF
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS" 2>/dev/null || true
echo "已安装到 $DST"

case ":$PATH:" in
  *":$BIN:"*) ;;
  *) echo "提示：$BIN 不在 PATH 里，命令行里用完整路径 $BIN/claudia-pet" ;;
esac

if [ "$CONNECT" = 1 ]; then
  "$BIN/claudia-pet" --connect plugin
  "$BIN/claudia-pet" --connect mcp
fi
case "${XDG_CURRENT_DESKTOP:-}" in
  *GNOME*|*gnome*)
    if [ "$EXTENSION" = 1 ]; then
      "$BIN/claudia-pet" --connect gnome
      echo "提示：跟着 Claude 窗口要用的 GNOME 扩展已经装好，注销电脑、重新登录一次后生效（不是 Claude 账号）。"
    fi ;;
esac
if [ "$START" = 1 ]; then
  setsid "$BIN/claudia-pet" >/dev/null 2>&1 < /dev/null &
  echo "claudia-pet 已经打开。"
fi
