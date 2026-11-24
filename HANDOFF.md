# claudia-pet 开发交接

更新：2026-11-22（开头「现在的状态」，在 Linux 虚拟机里又核对了一遍）。本文描述当前工作区。**0.4.2 已发版（2026-11-16）**：下面「下一步」里列的额度、圣诞树 v2、台词和运行方式都已随 0.4.2 提交、推送并发布（`9fc0e3a`），记录见 `docs/PUBLISHING_AUDIT.md`。**0.4.1 已发版（2026-11-10 晚）**：窗口跟随修复、桌面模式、多开（见「0.4.1」一节）。此前 **0.4.0 已发版（2026-11-10）**：0.3.0（11-07）之后的新动作（「之后」）和 11-08～10 的菜单修复、动作精简与重排（「2026-11-08～10」）一起发布，用户定不发 0.3.1。发版记录见 `docs/PUBLISHING_AUDIT.md`。

## 2026-11-24 下午：忙碌动画（已提交，未推送）
- 用户定：多会话的「忙碌」「忙不过来」各一套，不分左右；切换动作一律淡入淡出（照 dsh-pet），回待机时把这一圈播完；只管同一动作长时间循环要顺。
- 忙碌：Wan 3.0 8 秒，提示词 `prompt_busy_v2.txt`（快速左右看、不点头、不笑、平嘴、额角小汗珠——汗珠基本没画出来，用户接受）。视频 `D:\video llm\视频\忙碌\忙碌-v2-Wan3.0.mp4`。模型开头自己换了站姿，所以取原片第 15–207 帧（`--start 15 --step 2 --frames 97`，`--one-lut`）。配置 from 16、cycle [51, 81]（一直在转头，不站直）、exit 播到 96；look 标看左/看右帧段，卡片跟着亮；菜单点播时摆两张示意卡片。
- 下一个：忙不过来（swamped），现在还是左右两张静态图。

## 2026-11-24：派活动画 + 窗口加宽（`0d5ae2f`、`543b040` 已推送）
- 布偶出窗口的解法：窗口 260 → 330（Windows `Pet.cs`、Linux `pet.py`、`web/text-size.js`），Windows 碰边改按人物本体（`Pet.Follow.cs` 的 `BodyMargins` / `ClampToArea`，移植自 Linux `body_margins`），顺带修好 Windows 撞边离屏幕边空一截。合成脚本里「往中间挤」那段已删。Windows 全部测试 + `-MotionTests` 通过（`tests/MotionHandoff.cs` 改成 330），用户两边看过。

### 下面是凌晨停下时的记录（已过时，留作经过）
- 设计：她左手抱书、右手指挥，两只 Clawd 样子的方块小布偶绕她脚边跑圈。视频 `D:\video llm\视频\派活\派活-v3-Wan3.0-布偶跑圈指挥.mp4`（10 秒、30 帧/秒）。另一段 `派活-循环v1-…-不用.mp4` 用户说不用。用户定：**不再生成视频**。
- 精灵图流程：`video_to_sheet.py … --step 2 --frames 150 --loop --sr`（快动作别用 2.5 混合，会出残影）→ `lab_match.py … --mask-first --one-lut`（布偶会把颜色带偏、跑过脸前会闪）→ 得到 `D:\video llm\输出\派活\派活-v3-校色后-150帧.webp` → **`compose_layers.py`**（要 scipy，在 Linux 用临时 venv 跑）分层重拼成 171 帧：入场 0–87 原样，循环 88–129（她手势 80–121 + 布偶半圈 88–108 播两遍），离场 130–170。每帧先按头部对齐抵消晃动；她整个人用她的帧（不横切，横切会出发尾残影），帧里原本的布偶挖掉用第 0 帧补；布偶按和第 0 帧的差抠（只留贴地或够大的块）再叠上；最后反推半透明处的绿幕。用户 Linux 实看「动画没问题了」。
- 仓库里已改（未提交）：`characters/claude/anim/派活-小帮手跑圈.webp`（SHA 79ee2529c7d732a2，已装 Linux）、`character.json` 的 delegating（fps 15、frames 171、cycle [88,129]、exit.continue）、8 张静态派活图 git mv 进 archive、`SOURCE.md` / `NOTICE.md` / archive README、`web/sheet-player.js` + `index.html`（animations[].fps / frames、exit.continue / exit.jump）、`index.html` startFlip 减少动画也翻页（Linux xsettings 关动画导致只显示一张）、`test-anim` / `test-flip`、`plugin/hooks/register.ts`（子代理事件 agentId：保持派活、不庆祝不通知）。**Windows 上这批还没跑测试**（要跑 test-anim、test-flip、test-mood 再构建安装）。
- **没解决**：离场时两只布偶站在两端，跑出桌宠窗口（窗口 260 宽，只显示精灵图第 122–528 列，布偶到第 77–556 列）。两条路：
  1. `compose_layers.py` 里已写了一半的「布偶往中间挤」（VIEW/K/clawd_parts，按是否盖在她轮廓里决定画在她前还是后）：**写了没跑、没审查**，里面还有一行没用的 `soft = …` 要删。
  2. 用户提议：把窗口变宽，点击仍只认人物。点击穿透两边都已按 hitRects 做；Linux 碰边按 `body_margins()`（取最大的 hitRect）算，窗口变宽不影响；**Windows 碰边是不是也按人物算还没查完**（`Pet.Follow.cs` 的 WorkArea / AreaRect 附近）。用户倾向这条，明天先查完 Windows 再定。
- 用户要求：每版成品**先逐帧审查**（全部帧缩略 + 发尾等细节放大到原尺寸）再给他看；token 随便花。

## 2026-11-23 晚：自制动画「有事问你-举手」（`2b2bded` 已推送；之前 `9c38c03` Linux 修复、`6ed4e33` 查资料动画也已推送）
- 改用 LibTV 出片（不再用 Comfy），模型 Wan 3.0 标准版（32 积分/8 秒）。跑了 4 版：v1 手变大、v2 歪头变转头+斜眼、v3 嘴一直 O 型开合（用户不喜欢）、v4 采用。教训全在 `D:\video llm\工作流\提示词经验.md`（身体比例、嘴型、用户偏好、Wan 后期）。提示词 `prompt_asking_v4.txt`，视频 `D:\video llm\视频\有事问你\有事问你-v4-Wan3.0-采用.mp4`（11-23 起视频按动作放在 `D:\video llm\视频\` 下）。
- `video_to_sheet.py` 改了：抠像按每帧四边实测底色定阈值（Wan 整幅去饱和，绿底只有 (90~110,160,95~105)）；`--step` 可为小数，Wan 30 帧/秒用 `--step 2.5`，半帧处前后两帧各半混合（取整会 2、3 交替，动作忽快忽慢）。
- 配置：`"asking": { to: 47, cycle: [33, 47], exit: { from: 48, to: 95, continue: true } }`。Wan 后半段整体偏了，循环两头和放手对不上，所以新增 `exit.continue`（`web/index.html` 的 `leaveVia`）：离场从当前帧一直正着播到结尾，不跳、不倒放；回答后她会再摆 2～5 秒手才放下。睡觉不用这个。
- Windows 上 test-anim、test-mood 在 hold 版通过并装过；最终版（cycle + continue）的测试命令已给用户，用户两边看过说可以。**最终版在 Windows 上的测试结果没回报。**
- 下一个动作按顺序：派活（delegating）→ 忙碌 / 忙不过来。

## 2026-11-23：换到新虚拟机（Debian 13 + Openbox，外面套着 cage）上装 Linux 版（**`linux/claudia/main.py` 三处修复未提交**）
- 仓库在这台机器上是 `/c/Users/ASUS/claudia`（sshfs 挂的 Windows 仓库）。`main` 已到 `ee69ccd`（Codex 合了 PR #7：PR #6 的 60 帧、内置角色从安装目录读等）；工作区还有用户 / Codex 没提交的一批改动（新的查资料动画 `查资料-扫读翻页.webp`、查资料静态图移进 archive 等），装的时候一起装进去了。
- 用户要：不跟随 Claude 窗口（这台没有 GNOME，本来也用不了扩展），但跟着 Claude 启动 / 退出 → 运行方式「跟着 Claude，待在桌面上」。装法：用户 `sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1 libnotify-bin gir1.2-notify-0.7 gir1.2-ayatanaappindicator3-0.1 picom`，然后 `sh linux/install.sh --connect --no-extension`。插件接入写进了 `CLAUDE_CONFIG_DIR`（`/tmp/runtime-…/paths/…/settings.json`，其实链到 `~/.local/share/cage/claude-accounts/…/config/settings.json`，持久）；MCP 加进 `~/.config/Claude/claude_desktop_config.json`（原有 `computer` 保留，备份在同目录 `.bak-claudia-20261123-180907`）。
- 三处修复（都在 `linux/claudia/main.py`）：
  1. 启动就崩：Debian 13（GLib 2.84、PyGObject 3.50）有 `GLibUnix` 却没有 `signal_add`（只有 `signal_add_full`），原来只接 ValueError / ImportError → 改成按顺序找 `GLibUnix.signal_add` → `GLib.unix_signal_add` → `GLibUnix.signal_add_full`。
  2. Claude 重启后没把她拉起：这台 Claude 给 MCP 的环境只剩 6 个变量（`claude-desktop` 自己也没有 DISPLAY，再往上的 `cage-input-session` 才有；systemd 用户环境里没有；X 是 `:78` 不是 `:0`）→ 新增 `env_from_ancestors()`：沿父进程链找第一个有 DISPLAY / WAYLAND_DISPLAY 的进程补会话变量；`--ensure`、`--mcp` 一进来就补（拉起桌宠前，因为 MCP 进程很快就退、链会断）。用 `env -i` 模拟过，能补上 `:78` 和 XAUTHORITY、连得上。**真机「完全退出 Claude 再打开」还没验证。**
  3. 背景是黑的：这个桌面没有合成器 → 新增 `ensure_compositor()`：X11 下没人占 `_NET_WM_CM_S0` 且装了 picom，就 `picom --config /dev/null --backend xrender -b`（不读默认配置 = 没阴影、淡入淡出；纯软件合成）。cage 的会话脚本是系统的、没有用户自启入口，所以让桌宠跟着自己起来时拉。停掉 picom 后测过能拉起来；重启虚拟机后验证通过。
  4. 时不时出现黑方块、偶尔整屏发黑：这台屏幕是 Xtigervnc :78（无显卡），picom 默认只重画变化区域（use-damage），在 VNC 上漏画 → 参数加 `--no-use-damage --no-vsync`，日志写到 `~/.claudia/picom.log`。用户实测没问题了（CPU 几乎为 0）。
- 系统通知失败：这个桌面没有通知服务（`org.freedesktop.Notifications`），要的话另装一个（如 `dunst`）——没做。

## 交接（2026-11-22 晚，上下文快满时写）——最先读这一节

### Codex 补记（2026-11-22 晚）

- GitHub 与本地 `main` 已到 `ee69ccd`（PR #7）。PR #6 的循环动画限帧和内置角色直读已适配 Windows、Linux 并合入，保留 littlepec 的提交作者，额度逻辑沿用原行为。PR #6 已回复并关闭。最新正式版仍为 `v0.4.2`。
- Issue #2：报告者已回日志，原因是 Windows「辅助功能 → 文字大小」120%。在用户本机保持文字大小 120%、显示缩放 100%，用新版隔离实例启动，WebView2 实测得到 `217×302`（画布 `260×362`）。`refit` 缩放约 83.4%，短气泡和三行气泡完整显示。新版还未发布，用户决定先暂缓公开回复，保留 Issue，发布后可请报告者用新版复测。
- Issue #1：空气吉他 v2 已从 `main` 移除（`27a4e06`）。已告知报告者素材本身有问题，用户决定先等对方回复。
- macOS（Issue #4、PR #5）：用户没有 Mac，倾向让主仓库继续维护 Windows / Linux，由贡献者自行维护 macOS fork。#4 是 Swift fork，已有 Claude 窗口跟随。#5 是 Python/PyObjC，有多开，尚无 Claude 窗口跟随，当前与 `main` 有冲突。GitHub 状态均为打开，公开回复先给用户看稿。

以下保留当晚较早的记录。

- **GitHub `main` = 本地 `main` = `f199f42`**（11-22 用 `git ls-remote` 核实）。今天推上去的：`f6b574c` 工作区统一 LF（`.gitattributes`）、`b85f791` Linux 最小化 / 托盘 / 拖动计时器修复、`27a4e06` 去掉空气吉他 v2（issue #1）、`3565c67` Windows 桌宠窗口换成 DirectHost + 网页 `refit` 铺满 + 鼠标转发（换屏缩放根治、issue #2 兜底）、`f199f42` 右键 / 托盘菜单按所在屏幕的缩放显示。Release 仍是 `v0.4.2`，这些都**还没发版**。工作区只剩 `HANDOFF.md`（只留本机）和旧的 `CODEX_HANDOFF_2026-11-10.md`（未跟踪）。
- 都在 Windows 上编译、`-MotionTests`、7 个网页测试过了，用户实机测过（细节见下面各节）。没测的：占用变化。
- 工作方式（用户定）：以后在 **Linux 虚拟机里的 Claude** 干活，Windows 版和 Linux 版都在这个共享目录改（Linux 路径 `/media/sf_claude_ws_claudia_8d75acbe4023`，Windows 上就是 `C:\Users\ASUS\claudia`）。Linux 改完跑 `sh linux/install.sh`；Windows 由用户在 PowerShell 里跑 Claude 给的**一整行命令**（要带 `Set-Location C:\Users\ASUS\claudia`，用户要求能一键粘贴）。推送：用户已在 `.claude/settings.local.json` 加了 `Bash(git push origin main)`，用户说推再推。git 在 Linux 上已设 safe.directory；没配作者，提交时用 `-c user.name=kirito1207 -c user.email=327070581+kirito1207@users.noreply.github.com`，不加 Claude 署名。
- 公开发言（issue / PR 回复）**一律先把稿子给用户看**（11-22 有一次没给稿就在 #2 下发了请对方贴日志的回复）。
- **还没处理、等用户定的**：
  - issue #1 已修（`27a4e06`），要不要回复并关闭——先给稿。
  - issue #2：已请报告者贴 `windows.log`，还没回音；`refit` 应能兜住被裁，DirectHost 也可能顺带修好，等他反馈。
  - PR #6（littlepec）：用户定收 ① 60 帧（`c0b59c4`）② 内置角色从安装目录读（`0f6565a`），**不收** ③ 额度（`6a29e9e`），但说「PR 先不做」。注意 ① 改的是 `web/index.html`，今天 `3565c67` 也大改了它，cherry-pick 可能要手工合。做法：本地 cherry-pick 两个提交（保留作者）→ 测 → 推 → PR 下说明（先给稿）→ 关。不能点合并按钮（三个一起收）。本地有引用 `pr/6`。
  - PR #5（Skrrrrry，Python/PyObjC，和 Linux 版同构，没跟随 Claude 窗口，有冲突）和 issue #4（FLynn1213，Swift fork，有跟随 Claude 窗口）：用户还没定要不要支持 macOS。两者对比见下面「其他 11-22 事项」前后的记录和本次对话结论（Claude 倾向：要支持就收 PR #5，请他变基）。
  - Linux 版：拖动 Claude 时跟随延迟（快拖落后约 170 像素）；拖动后偶发崩溃（已开 faulthandler，再崩看 `~/.claudia/stderr.log`）。
  - 查资料动画 v4：要先给 Comfy 充值约 170 积分。
- 用户 Windows 上的运行方式现在是「独立运行」（为了不开 Claude 测试改的），要不要改回「跟着 Claude」用户没说。

## 交接给下一个对话（2026-11-18 晚起，11-21 核对过现状）——先读这一节

### 现在的状态（2026-11-21 核对，11-22 复核）
- **11-22 复核（在 Linux 虚拟机里经共享文件夹看的同一个仓库）**：提交历史和下面一致，`main` 仍在 `fdb1cbf`，`git ls-remote` 核实 GitHub 上的 `main` 也是 `fdb1cbf`。真正改了内容、没提交的仍然只有 `HANDOFF.md`。
  - **远端不止 `main`**（下面「远端只有 `main`」已过时）：还有分支 `linux-port`（停在 `7310289`，PR #3 已于 11-17 合并，内容已经由 `a6c3345` 同步进 `main`，分支没删）；以及两个**外部贡献者开着、没处理的 PR**（11-22 用 `gh` 只读查的）：
    - **#6**（littlepec，11-20，分支 `perf-fixes`，+84 -51）「Cap looping body animations at 60fps, load bundled characters in place, and keep quota across session start」：改 `Store.cs`、`register.ts`、`web/index.html` 等。GitHub 显示可以自动合并，但 `register.ts` 和 `index.html` 正是 Codex 在 `fdb1cbf` 里大改过的地方；「会话开始时保留额度」可能和 0.4.2 定的「会话开始没有认得的额度就清空」相反。**要逐行看过再决定，没看。**
    - **#5**（Skrrrrry，11-19，分支 `macos-port`，+3832 -6）「Add a macOS shell for the pet」：新增 `macos/` 整套外壳，和现在的 `main` 有冲突（CONFLICTING）。**没看。**
  - ⚠️ 在 Linux 里 `git status` 会显示另外 98 个文件「已修改」，**全是换行符差异**（Windows 签出是 CRLF，Linux 的 git 按 LF 比），`git diff --ignore-cr-at-eol` 下内容一字没变、也没有权限变化。**不要在 Linux 里提交或 `git add` 这些文件**，提交在 Windows 上做。
  - 在 Linux 里用 git 会报「dubious ownership」（共享文件夹属主是 root），用 `git -c safe.directory=<路径> …` 临时放行即可，没改全局配置。
  - 这台虚拟机没有 Node，7 个网页测试没跑；`tests/test_linux_store.py`（Codex 加的）在这里跑了，2 条全过。

### 2026-11-22：Linux 版三个问题（Ubuntu 虚拟机，GNOME 50.1，Wayland，桌宠走 XWayland）——**已提交 `b85f791`，已推送**
改动在仓库 `linux/claudia/xshape.py`、`pet.py`、`main.py`。用户在虚拟机里实测「基本上没问题了」。
- **最小化 Claude 后她停在原地不动、切回来又接着动**：扩展报了最小化，桌宠也把窗口外形设成了「零个矩形」并暂停网页，X 服务器也确认外形已空——但 **Mutter 不认空外形**，屏幕上还是窗口最后一帧（网页暂停了，所以看着「卡住」）。改成隐藏时外形留左上角 1×1（人物外面、本来透明）。随后发现 **Mutter 也不认「取消外形」**（`XShapeCombineMask` 给 None），1×1 之后她就再也不出来了；显示时改成设一个 32767×32767 的大矩形（服务器按窗口大小截掉，改尺寸也不用重设）。`xshape.py` 的 `set_visible`。
- **点 Claude 右上角 × 收进托盘后，桌面上多出一只能拖的**：Linux 版原来「扩展找不到 Claude 窗口就去桌面」，不管运行方式；Windows 版是只有独立运行才去桌面。改成：这次运行里找到过 Claude 窗口、后来没了（= 托盘）→ 跟着 Claude 时藏起来、独立运行时去桌面；从启动起一次都没找到（可能扩展认不出这个 Claude）→ 照旧先待桌面。`pet.py` 的 `want_desktop` + `claude_window_seen`。
- **拖动后 `pet.py:840: Warning: Source ID … was not found`**：`pump_pointer` 松手时返回 False（GLib 自己删计时器）却没清 `self.drag_timer`，`stop_motion` 再删一次旧编号。已清空。
- 实测（每 20 ms 同时读扩展报的 Claude 位置、桌宠窗口位置和外形，120 秒）：最小化两次都 1×1 隐藏、恢复都整窗显示；点 × 两次扩展报 `found=False`，她保持隐藏、没去桌面，Claude 再打开回原位。

### 代码放在哪、怎么改（2026-11-22 用户定）
- 用户以后在 **Linux 虚拟机里的 Claude** 干活；**Windows 版和 Linux 版都在这个共享目录（仓库）里改**，它是唯一的源码。Linux 里路径 `/media/sf_claude_ws_claudia_8d75acbe4023`。
- 链条：共享目录 → 在 Linux 上直接 `sh linux/install.sh`（不带 `--connect`）→ 安装版 `~/.local/share/claudia-pet` → Claude 桌面端 MCP（`~/.config/Claude/claude_desktop_config.json` 的 `claudia-pet.command` = `~/.local/bin/claudia-pet`）和 Claude Code 插件（`~/.claude/settings.json` 的 `CLAUDE_CODE_PLUGIN_DIRS` 只剩 `~/.local/share/claudia-pet/plugin`）**都只用安装版**。改了 Linux 代码 → 重新跑一次 install.sh。11-22 两处配置都已改；之前插件目录里同时列了旧签出和安装版，插件被加载了两次。
- 工作区统一 LF：`f6b574c` 加了 `.gitattributes`（`* text=auto eol=lf`，图片等标成 binary）。仓库里存的本来就全是 LF，所以没有内容变化；工作区原来 97 个 CRLF 文本文件已就地改成 LF（逐字节核对只改了换行）。之后 Windows 签出也会是 LF——**回到 Windows 时构建一次确认**（C#、PowerShell 7、Node 都认 LF，按理没问题，没实测）。
- 在 Linux 里用 git：共享目录属主是 root，git 会报「dubious ownership」；用户 11-22 已自己把它加进 `safe.directory`，现在直接用 `git`。这台 Linux 的 git 没配 user.name/email，提交时用 `-c user.name=kirito1207 -c user.email=327070581+kirito1207@users.noreply.github.com`（和以往提交一致，不加 Claude 署名）。
- 11-22 收尾：`f6b574c`（.gitattributes）、`b85f791`（Linux 三处修复）用户已自己推送，`git ls-remote` 核实 GitHub `main` = `b85f791`。用户重启 Claude 桌面端后，桌宠和 MCP 都从安装版运行；旧签出 `/home/kirito/code/claudia-pet`（644 MB，核对过没有未推送提交、stash，未提交内容仓库里都有）用 `gio trash` **移到了回收站**，没永久删，要找回去回收站。
- 推送权限：项目 `.claude/settings.local.json` 里原有 Windows 用的 `PowerShell(git push -u origin main)`；Linux 用 Bash 工具，要另加 `Bash(git push origin main)`（Claude 告诉了用户加法，由用户自己加；加没加没核对）。有权限也照旧：推送前要用户明确说。

### 2026-11-22：Windows 版换屏 / 换缩放后人物变小、显示不全（**最终：换成 CrossPet 的 DirectHost 窗口根治；11-22 Windows 上编译、`-MotionTests` 3 项、7 个网页测试都过了，已装到本机；**用户实机测过：显示和透明、点空白处穿透、单击、拖动和甩、右键和设置页、层级（跟 Claude / 桌面置顶）、隐藏快捷键（用户设的是 Ctrl+Alt+H）、藏着时点得透、走路都正常；外接 1080p 100% ↔ 笔记本 2K 150% 来回切、各种重启组合，大小都一致**。日志干净：每次切屏只有一行「系统缩放变了：现在 N%」，没有对不上、没有报错，旧窗口每次启动那个假的「100% → 100%」也没了。占用没测。已提交 `3565c67`、已推送**。test-anim 很慢，看着像卡住，等一会儿就过了）
- 现象（用户实测）：笔记本 2K 16 吋 150% 和外接 1080p 24 吋 100% 之间切换（或运行中改系统缩放），她会缩小一圈；重启后又是正常大小。用户定：重启后的大小才是对的，切换后变小要修。
- 日志（用户 Windows 的 `windows.log`，WebView2 157.0.4341.60）：100%→150% 后网页 174×242、应为 260×362（正好 1/1.5，网页区域停在旧缩放的像素上）；`ResizeWebBounds` 补对齐两次都没成；接着 `ZoomCheck.Fix` 把它当成「系统缩放算了两遍」（指纹恰好相同），网页缩放改成 0.667 → 人物缩小。150%→100% 反过来同样一遍、又改回 1。
- 第一版改法（重建网页控件）**没用**：同日 19:41 / 19:42 日志，补对齐两次失败后重建了网页控件，新控件照样停在旧缩放上（150% 时 174×242、回 100% 时 390×543）——错的不在控件本身，在整个 WPF 窗口那层。用户实测：重启后是正常大小；从 2K 150% 切回 1080p 100% 时网页比窗口大，只露左上角（显示不全；新加的「铺满窗口」会按偏大的网页放大，更显得被裁）。
- 第二版（补对齐失败就自动重启程序）写了，用户定**不测、直接根治**，已撤掉（`RenderRecovery.cs` 恢复原样）。
- **根治（用户定）：照 CrossPet 1.3.9 起的做法，桌宠窗口换成 `app/src/DirectHost.cs`**（CrossPet `app/windows/src/DirectHost.cs`，MIT，经 GitHub 接口在线读、按我们的代码改写；提交 `1fab899`、`b707b4c`）：普通 WinForms 窗口 + `WS_EX_NOREDIRECTIONBITMAP` + 普通 WebView2 子窗口（WinForms 版），网页由 DWM 直接合成、逐像素透明；普通 WebView2 子窗口自己跟着显示器缩放走；画面不经界面线程，外壳也不再每帧拷画面（理论上占用会降，没测）。网页内容（精灵图动画、canvas）照常由 WebView2 画，显示应该和原来一样。
  - `DirectHost.cs`：每 30 ms 按鼠标在不在能点区域里切 `WS_EX_TRANSPARENT`（按住左键时不切）；`ForcePassThrough`（藏起来时整个穿透）；`SetVisible`（不透明度 0/255，代替 WPF 的 Opacity）；`MessageHook`（快捷键 WM_HOTKEY）；截 `WM_DPICHANGED` 发 `DpiScaleChanged`；`DpiScale`（`GetDpiForWindow`）；`ReplaceWeb`（浏览器进程崩溃后换控件）。和 CrossPet 不同：不管置顶（我们的置顶由 `PlaceAbove` / `KeepOnTop` / `SwitchArea` 直接调系统）；去掉它的「按 Ctrl 让开」；拖动不走系统 `DragMove`，接我们自己的物理。
  - 网页 `index.html` 加 `setPointerBridge`（照 CrossPet）：按下 `{pointer:'down'}`（我们加的：外壳记下按下时的屏幕坐标，物理要知道从哪儿拎起来）、移动 >4px `{pointer:'drag'}`、单击 `{pointer:'click',x,y}`（画布坐标）、右键 `{pointer:'menu'}`；外壳在页面加载完调 `setPointerBridge(true)`。Linux 外壳不调，不受影响（已装上验证）。
  - `Pet.Mouse.cs` 重写：去掉 WPF 透明画布 `hit`；`UpdateHitRects` 把网页报来的画布坐标 × (窗口物理宽 / 画布宽) 交给 `Host.SetHitRects`；`HandlePointer` 接网页的 pointer 消息（down → StopMotion、记坐标；drag → 按键还按着才 `BeginDrag`；click → `handleClick`；menu → `ShowMenu`）。松手照旧由拖动物理每帧看物理按键（`releasedEarly`）。
  - `Pet.Physics.cs` / `Pet.Walk.cs`：每帧原来挂 WPF 的 `CompositionTarget.Rendering`，没有 WPF 窗口在画后不一定来，改成 16 ms 的 `DispatcherTimer`（Render 优先级）。
  - `Pet.cs`：`Window`/`grid`/`WebView2CompositionControl` → `Host`/`WebView2`（WinForms）；`ui` = 当前 Dispatcher 代替 `Window.Dispatcher`；换缩放时 `ApplyScale(…, Anchor.Feet)` 按新缩放重设物理像素大小；崩溃恢复用 `Host.ReplaceWeb()`。
  - `Pet.Settings.cs`：`ResizeHost`（物理像素 = 画布 × 人物大小 × `DpiScale`）；删掉只为旧控件的 `ResyncWebForDpi`、`ResizeWebBounds` 和「停在旧缩放上」那一整套；`CheckZoom` 只留日志和 `Fix`（「缩放算了两遍」），网页还有 `refit` 兜底。`ZoomCheck.StuckAtOldDpi` 现在没人调用，留着没删。
  - `Pet.Layer.cs`：藏起来改用 `Host.SetVisible(false)` + `Host.ForcePassThrough`；删掉「给背后的浏览器窗口加鼠标穿透」（只为旧控件，CrossPet 换完也删了）；`ApplyLayer` 改看窗口样式的置顶位。`Pet.Hotkey.cs`：`HotKeyHook` 改成 `bool (int msg, IntPtr wParam)`。`Pet.Pets.cs`：去掉 WPF 的 `Topmost`。
  - `tests/MotionHandoff.cs`：点击区域换算、拖动交接两项改成测 `DirectHost`（`DirectHost.HitRects` 是为测试加的只读属性）。`NOTICE.md` 补了从 CrossPet 新版本移植的说明。
  - 这台虚拟机没法编译，只做了静态检查（括号配平、删掉的成员没有残留引用、用到的成员和签名都在）。
- **待做（Windows）**：构建 + `-MotionTests` + 7 个网页测试；装好后按清单实测：透明边缘和光晕、点空白处能穿透、单击摸头、拖动和甩（火气、撞边）、右键菜单、设置页、跟着 Claude 时的层级、桌面模式置顶、多开、隐藏快捷键（Ctrl+Alt+P）、藏起来时点得透、外接屏和笔记本屏之间来回切（大小是否和重启后一样）、走路、占用。
- 和 issue #2 的关系：#2 报告者是 4K + 自定义缩放 169%→150%、重新登录后仍被裁，只少高度、人物完整，和这里「按比例变小」不完全一样，可能同源可能不同。11-22 已在 #2 下请他贴 `windows.log` 里「网页大小和画布对不上」那几行，并问自定义缩放是否还开着（这条回复 Claude 没先给用户看稿就发了，用户之后要求：公开发言一律先给稿子）。

### 2026-11-22：右键菜单在副屏上大小不对（**已提交 `f199f42`、已推送，用户实测没问题**）
- 现象（用户截图）：主屏是笔记本 2K 150%，切到外接 1080p 100% 上，人物大小对了，右键菜单的字和行高却大了一半。原来就有（菜单代码没动过），只是以前切屏后人物本身也不对，没人注意到菜单。
- 原因：WinForms（.NET Framework，没在 App.config 里开按显示器缩放）里，字号换成像素、菜单的 `DeviceDpi` 都按「系统缩放」（登录时主屏）算，菜单弹到缩放不同的屏上就跟着大 / 小一圈。CrossPet 没处理（普通菜单、App.config 没开 WinForms 的按显示器缩放），没有现成做法。
- 改法（`SoftMenu.cs` 的 `Apply`）：弹出前查鼠标所在屏的缩放（`MonitorFromPoint` + `GetDpiForMonitor`），字号和内边距乘「这块屏 ÷ 系统缩放」，宽度、箭头位置按这块屏的缩放算（不再读 `DeviceDpi`）；和系统缩放一样的屏上比例是 1、和原来完全一样。右键菜单和托盘菜单都走这里。没选 App.config 那个官方开关：它会影响整个程序的 WinForms，包括 DirectHost（换屏时窗口可能按系统建议自己改一次大小，和我们的 ApplyScale 打架），无父窗口的弹出菜单在 .NET Framework 上也不一定跟得对。
- 验证：Windows 上编译、`-MotionTests` 过；用户在两块屏上开右键菜单都正常。

### 2026-11-22：移植 CrossPet 1.3.9 的「网页自己铺满窗口」（**已改；Windows 上 7 个网页测试都过了（含 test-ui），已构建、装到本机；实机测过（用户的整套实测在 DirectHost 版上做的）；已随 `3565c67` 提交推送**）
- 来源：CrossPet 1.3.9（11-04，我们是从 1.3.8 分出来的，所以没有）更新日志「气泡和人物有时被挤到窗口外……以前是认出一种原因修一种，现在桌宠网页会量自己实际拿到多大，对不上就整体等比缩放、正好铺满窗口」；点名的一个原因是 Windows「辅助功能 → 文本大小」不是 100% 时网页多乘了这个比例。代码照抄它 `app/web/index.html` 的 `refit`（经 GitHub 接口在线读的，没下载仓库）。
- 改动全在 `web/index.html`：`#wrap` 外套一层 `#fit`；`setSizes` 记下画布尺寸并 `refit()`；`refit` 量 `innerWidth/innerHeight`，和画布差 1.5% 以上就把 `#fit` 等比缩放、左右居中底边对齐，`#wrap` 高度改用画布高（`--fit-h`）；`toCanvas` 把 `getBoundingClientRect` 换回画布坐标，`hitRects` 用它，外壳不用改；走路速度乘 `fit`。我们页面里交给外壳的坐标只有 `hitRects` 一处，`handleClick` 的坐标页面不用。
- 作用：issue #2 那种「网页比画布小一截、顶上气泡被裁」不管什么原因都会整体缩小塞进窗口、不再被裁。换屏后网页区域停在旧缩放上那种它只能缩小，真正的修法是上一节的重建网页控件。
- 验证：Linux 虚拟机内置浏览器里直接调 `refit`：画布=网页 → fit 1 不动；网页比画布大 → 放大 2.1215（理论值），居中、底边贴齐，`toCanvas` 还原成 0,0,260,362；网页比画布小 → 缩小 0.8533（理论值），整块在网页里、顶上不裁；`hitRects` 换算回画布坐标。Linux 版装上后正常运行、没有新的网页脚本错误。**Windows 上的 7 个网页测试和实机都还没跑**（test-ui 里有量点击区域的检查，要看）。

### 其他 11-22 事项（空气吉他已提交 `27a4e06`）
- issue #1 空气吉他：作者 v2 素材里吉他只画了琴颈（我们的文件和作者原件哈希一致），`character.json` 的 `air_guitar` 改成只轮换 v1、v3，`弹空气吉他v2.webp` 已 `git rm`（删除在暂存区里），`anim/SOURCE.md` 记了原因。Linux 已 install.sh 装上。网页测试没跑。
- PR #6：用户定收 ① 60 帧限制（`c0b59c4`）和 ② 内置角色从安装目录读（`0f6565a`），**不收** ③ 额度（`6a29e9e`），但又说「PR 先不做」，还没动 `main`。做法：本地 cherry-pick 这两个提交（作者保留 littlepec）→ 测试 → 推送 → 在 PR 下说明收了哪两项（先给用户看稿）→ 关 PR。PR 的提交已拉到本地引用 `pr/6`。不能直接点 GitHub 的合并按钮（会三个一起收）。
- PR #5 macOS：等用户定要不要支持 macOS（用户没 Mac 没法测）。

### Linux 版还没解决的（交给用户定）
- **拖动 Claude 窗口时跟随有延迟**：同一次实测，Claude 在动时她落后中位 19 像素、90% 在 170 像素以内；Claude 停下后 0.05 秒内对齐。链路是 扩展 → D-Bus → Python → XWayland → Mutter，每段晚一两帧，虚拟机没有 3D 加速更慢。根治要让 GNOME 扩展在拖动期间直接在合成器里挪桌宠窗口（结构改动），**没做**。
- **桌宠会崩**（原来就有，11-22 一天好几次，都在拖动桌宠之后）：`~/.claudia/stderr.log` 里是 glibc 的 `corrupted double-linked list` 后进程中止（内存损坏），`/var/crash` 没有报告。已在 `main.py` 开 `faulthandler`，下次崩时 stderr.log 里会有当时每个线程的 Python 调用栈——**再崩先看那里**。崩了以后插件下次 `--ensure` 会把她重新拉起来（用户看到的是「消失了，发消息又出现」）。
- ~~这台虚拟机有两份代码在用~~ → 已理顺，见下面「代码放在哪、怎么改（2026-11-22 定）」。
- MCP 服务进程拉起桌宠后不回收它：桌宠退出后留下一个僵尸进程（`<defunct>`），不占资源，没改。
- **本机 `main` 和 GitHub `origin/main` 一致，都在 `fdb1cbf`**，工作区只有 `HANDOFF.md`（只留本机，不推）和旧的 `CODEX_HANDOFF_2026-11-10.md`（未跟踪，不提交）。Release 仍是 `v0.4.2`（latest），之后的提交**还没发版**。远端只有 `main`。
- 本机安装版就是 `fdb1cbf`（`claudia-pet.exe` 2026-11-21 00:48 装的；安装目录的 `web/index.html` 和仓库一致，有 `sheet-player.js` 和三张 `.scaled.webp`）。
- 0.4.2 之后的提交（作者都记为 kirito1207；这几次不是本对话做的，内容按提交读出来的）：
  - `e111c2c`（11-17）Linux 版外壳。
  - `7310289`（11-18）GNOME 下跟随 Claude 窗口：`linux/gnome-extension/` 里的 Shell 扩展经 D-Bus（`io.github.kirito1207.ClaudiaPet`）报告 Claude 窗口位置、最小化、工作区和遮挡；没装扩展就待在桌面。`install.sh` 装扩展，`--no-extension` 跳过。
  - `74edf3c`（11-20）**原来本机没提交的那一大批**，内容见下面几条（静态图移出、省电模式删除、三个自制动画含小侦探）。
  - `a6c3345`（11-20）同步 Linux 的窗口跟随和动画支持。
  - `fdb1cbf`（11-21）「Stabilize updates and reduce desktop pet rendering overhead」：
    - 多会话状态改成每个会话各写 `claude-session-<sid>.json`（`plugin/hooks/register.ts`），外壳读 10 分钟内改过的（`Pet.Web.cs` 的 `PollSessionStates` → 网页 `setSessionStates`）。修掉了以前「多会话读改写 `claude-sessions.json` 会丢条目」的老问题；旧插件写的 `claude-sessions.json` 仍兼容读。
    - 待机呼吸、被拖起、原地小憩另附缩小版 `anim/*.scaled.webp`（每帧 448×252，`scripts/prepare-scaled-sheets.py` 生成），渲染尺寸用不到原图时用缩小版，省内存。见 `anim/SOURCE.md` 末尾。
    - 精灵图读取和播放从 `index.html` 拆到 `web/sheet-player.js`。
    - Linux：`notices.py`、`store.py`、`install.sh` 等改动，加了 `tests/test_linux_store.py`。
    - 11-22 读代码发现、**没改**的两点（交给用户定）：
      - `claude-session-<sid>.json` 每个会话一个，外壳只是不读超过 10 分钟的，**从不删除**，会话多了 `~/.claudia/state` 里会一直攒小文件（和以前 `claude-notify-*.json` 不清理是同一类）。
      - 三张 `.scaled.webp` 是**无损**压缩，每张约 5.7 MB，比原图（约 2.0 MB）大近 3 倍，安装包因此多约 17 MB；省的是运行时内存（解码约 54 MB 对 110 MB）。用的条件是显示宽度 × 屏幕缩放 ≤ 448 像素（`web/sheet-player.js`）。
- 以下是 11-18 当时记的「本机改动」，现在**都已在 `74edf3c` 里提交推送**：
  - 已有动画的姿态不留静态图：idle、idle-blink、listening、oops、update、avatar、portrait、portrait-card、reading、reading-2、proud 共 11 张 `git mv` 到 `archive/旧立绘-已被动画替换-不再使用/`（带 README 标明是旧的，不打包）。
  - `Store.Manifest` 有待机动画就算角色（`HasIdleSheet`）；网页里减少动画时也播精灵图、读不到改播待机动画；**省电模式整个删掉**（设置页、外壳、网页）。
  - 网页兜底：`sheet-on` 残留（有标记却没动画，静态图全透明、人不见）每 2 秒自动清，并记日志「sheet-on 残留已清除（姿态…）」。来源没查到，再出现就看日志。
  - 两个自制动画：`anim/看书-翻页.webp`（reading，整段循环）、`anim/得意-叉腰.webp`（proud，72 帧 `to: 71, full: true`）。来源写在 `anim/SOURCE.md` 末尾和 `NOTICE.md`。
  - 第三个自制动画 `anim/小侦探-放大镜.webp`（`detective`，96 帧 `to: 95, full: true`）：**闲置随机，玩耍组，不限时段**，菜单「动作 → 玩耍 → 小侦探」，台词「线索在哪儿呢……」「找到了！」（Claude 起草，用户未审）。本来是查资料第 2 版，像找东西不像查资料，用户定留作随机动作。test-anim 加了一条断言。
  - 11-18 晚 7 个网页测试、`-MotionTests` 全过（在 `74edf3c` 之前的工作区上跑的）。`fdb1cbf` 之后本对话**没有重跑测试**。
- 云端积分：用户 Comfy 账号充了 1055，已用约 75（作废）+ 212（看书）+ 127（得意 v2 作废）+ 127（得意 v3）+ 查资料 212 + 170 + 127，**现在约 0（界面显示负数）**。查资料 v4 点运行后任务列表出现 Failed，报错没看到原文，多半是余额不足；**要先充值约 170 才能跑 v4**。

### 查资料（searching）做到哪了（2026-11-18 晚）
- 三版都没成，过程和原因全记在本机 `D:\video llm\工作流\提示词经验.md` 的「作者动作包的写法」「查资料 v1 的教训」「查资料 v2、v3」三节；提示词 `prompt_searching_v1~v4.txt`、工作流 `查资料v1~v4-*.json` 都在同目录，视频在 ComfyUI `output\video\`。
  - v1（10 秒，放大镜一直举在眼前、从身后拿）：转成半侧脸、结尾放大镜没收走、眨单眼，作废。
  - v2（8 秒，魔法变出放大镜、书飘到肩旁、左右探着找）：动作都对、首尾对上，但不像查资料 → 改作上面的「小侦探」。
  - v3（6 秒，书飘到胸前自己开、翻页、放大镜扫书页）：书悬空后变大 3～4 倍、摊平朝镜头，书右半露出封面外侧，翻页糊成灰块，放大镜还是在眼前，作废。用户判断时间太紧，**以后这类动作至少 8 秒**。
- **下一步是 v4**（`prompt_searching_v4.txt`，8 秒，工作流 `查资料v4-Seedance2.0-480p-8秒.json` 已生成、在 ComfyUI 里截图核对过，种子跑失败后被随机成 1570620036，想保持一致就改回 42）：书一直在左手里、大小按首帧写（高约脸宽一半），书页朝她自己、上沿倾向镜头约 30 度，放大镜只在书页上方，翻页一次一张给 1 秒。计划只循环 2.4～5.6 秒的扫读翻页段，开头开书只播一次，「找到了 + 合书」做离场（程序里已有 `exit` / `leaveVia` 写法，具体怎么接出片后再定）。
- 用户定下的方向：查资料 = 书自己翻页、她拿放大镜看；道具用魔法变出来、变没；不要一直挡着眼睛；动作一直在动不发愣。
- 作者提示词原文在工作树 `build/aboutme-upstream/pets/claude/prompts/`（`00-通用前缀.md` 是总规则），写新动作前值得翻对应那册。

### 做一个新动作的流程（照这个来）
1. 写提示词前先读本机 `D:\video llm\工作流\提示词经验.md`（首帧、构图、道具、五官、颜色、清晰度的坑都在里面）。
2. 首尾帧：`D:\video llm\素材\idle_anim_green_1280.png`（作者待机动画第 1 帧绿底，**不要用 idle.webp**）。已在 ComfyUI 的 input 里。
3. 提示词照作者格式：【角色】【标准姿态】【颜色】【五官】【道具】【画面】【铁律】→ 动作概述 → 按秒分割（⚠️ 强调）→ 结束状态。
4. 做工作流：`python mkwf_seedance.py <提示词.txt> <秒数> <名字>`（在 `D:\video llm\工作流\`；默认 Seedance 2.0、480p、16:9、无音频、首尾帧 idle_anim_green_1280.png），用户在 Edge 里拖进 ComfyUI，Claude 截图（computer use，Edge 只读）核对首尾帧、模型、时长、价签后，用户点运行。**先给用户看方案再花钱。**
5. 转精灵图：`python video_to_sheet.py <视频> <未校色.webp> --loop --sr` → `python lab_match.py <未校色.webp> <仓库>\characters\claude\anim\待机呼吸休闲.webp <最终.webp>`。
6. 检查：脸放大看五官、逐帧人物范围不动、首尾帧差、颜色和作者对比，再换进 `anim/`、改 `character.json`、静态图 `git mv` 进 archive、改测试、构建、装到本机。

价格（Seedance 2.0）：480p 约 21 积分/秒（6 秒 127、10 秒 212），720p 约 46 积分/秒。480p 加超分就够清楚。

### 还差什么
**还没做动画的姿态（21 个，44 张图）**
| 类别 | 姿态 | 备注 |
|---|---|---|
| 干活 | 有事问你 asking、查资料 searching（翻页 3 张；动画在做，见上「查资料做到哪了」）、派活 delegating（翻页 8 张） | 都是循环状态 |
| 多会话 | 忙碌 busy_left / busy_right、忙不过来 swamped_left / swamped_right | 左右两张轮换；Codex 重画的往右看三版都不合格（最后一版脚变宽），可以改成从待机出发的一段左右张望 |
| 反应 | 道歉 sorry、累了 tired（额度见底，会停很久）、抱 Clawd clawd | |
| 生气一串 | 不耐烦 annoyed、鼓脸 puffed、红温 redhot、赌气 sulk、被哄 coaxed、原谅你了 forgiven、晕乎乎 dizzy | 用户 11-06 定过保持静态（按火气一档档换），要换先问 |
| 碰边 | 撞头 bonk（6）、站不稳 stagger（5）、摔倒 fallen（4）、趴地 faceplant（3） | 翻页，被甩撞边时短暂出现 |

**用户提过、还没做的**
- 「待在桌面上」要始终置顶、但**全屏应用时让开**（现在全屏也盖在上面）。
- 动画 WebP 代替精灵图省内存（精灵图解码一张约 110 MB）：要改播放器用 ImageDecoder 逐帧解码，先拿几个动作实测再决定。
- 「独立运行」时关掉 Claude、她留在桌面上：没实测过（要关掉 Claude 本身）。

**没处理的小问题**
- 自制动画的线条比作者略软（模型重画导致，超分只能改善）。
- 看书打开时书封面略偏红（提示词里加「封面颜色始终是深红棕色」没测过）。

## 交接给下一个对话（2026-11-15）

### 现在在哪（2026-11-15 核对过）

- 最新 Release 是 `v0.4.1`（标签 `5873fc0`「claudia-pet 0.4.1」，附件 `claudia-pet-0.4.1-win.zip` 约 277 MB）；GitHub `main` 在它之后只多了发版记录。上一版 `v0.4.0` 标签 `1c6f3da`。远端只有 `main`，贡献者只有 kirito1207。
- 11-08 起在**本机主仓库**（`main`，和 `origin/main` 一致）里做，不再用工作树 `.claude/worktrees/kind-blackburn-304e7f`；那个工作树还在，里面的 `build/aboutme-upstream`、`build/codex-imagegen/`、`build/perf-tools/` 等工具和素材仍可用（不进 git）。
- 本机安装的是 0.4.1（`scripts/install.ps1` 装的，不带 `-Connect`）。重开 Claude 后由 MCP 拉起，会有两个 `claudia-pet.exe`（`--mcp` 那个是 MCP 服务），属正常。
- 7 个网页测试和 `-MotionTests` 在 `5873fc0` 上全部通过（2026-11-10）；这些测试覆盖不到跟随、桌面模式和多开，那三样只在本机桌面上由用户实测过。
- 作者库（hunmer/aboutme-pets）现在 `cb205c2`（11-09）。Claude 角色还是 166 个动作、精灵图没变；11-09 新加了 8 段 m4a 音频（只有 8 个动作有）和每个动作的 `"facing": "left"`，**用户定暂时不加声音**。作者 11-08 前后改写过历史：我们记的 `da5a6fe` 现在不在作者分支上了（按哈希还能打开），分支上对应的是 `e1cebca`；以后再取素材按新哈希记。

### 2026-11-18：自制动画第二个「得意-叉腰」，转换流程定型（本机，未提交）

- 「得意」：Seedance 2.0 480p 6 秒（72 帧，配置 `to: 71, full: true`），叉腰挺胸、踮脚轻颠、头顶小金闪光。第 2 版提示词写了「眼睛一亮、睁大」被画成闪亮大眼作废，第 3 版加五官约束后可用。`proud.webp` 移进 archive；程序原来给得意画的金色闪光（`fx.proud = victory`）在有动画时不画，现在由动画里的闪光代替。
- 看书也重做了两次颜色：最终流程 `video_to_sheet.py --loop --sr`（BT.709 解码 + Real-ESRGAN 动漫视频模型超分 2 倍）→ `lab_match.py`（每帧 Lab 分布匹配到待机第 1 帧）。原因和数据记在本机 `D:\video llm\工作流\提示词经验.md`。
- 7 个网页测试、-MotionTests 全过，已装到本机。角色文件夹剩 44 张静态图。

### 2026-11-18：第一个自制动画「看书-翻页」（本机，未提交）

- 用 ComfyUI 云端节点 Seedance 2.0（480p、10 秒、首尾帧都是作者待机第 1 帧绿底）生成，`D:\video llm\工作流\video_to_sheet.py` 抠绿、抽 12 帧、对齐成作者同规格精灵图，放进 `anim/看书-翻页.webp`；`reading` 改成整条循环，原来的翻页配置删掉，`reading.webp`、`reading-2.webp` 移进 archive。来源写进 `anim/SOURCE.md` 末尾和 `NOTICE.md`。test-flip 的循环翻页改测查资料。7 个网页测试、-MotionTests 全过，构建通过。没装到本机。
- 提示词经验（书变大、开合变形怎么约束）记在本机 `D:\video llm\工作流\提示词经验.md`。
- 用户定：都在本机做，大部分动作替换完再一起上传 GitHub。

### 2026-11-18：静态图移出、省电模式删除（本机，未提交）

- 用户定：已经有动画的姿态，静态立绘全部移出程序（之前说「替换」，其实 idle.webp、idle-blink、listening、oops、update 还留着兜底，用户不满意）。`git mv` 到 `archive/旧立绘-已被动画替换-不再使用/`（带 README 标明是旧的，不打进安装包），连同程序早就没用的 avatar、portrait、portrait-card。角色文件夹剩 47 张，都是还没做动画的姿态。
- `Store.Manifest`：有 `animations.idle` 的精灵图也算一个角色（`HasIdleSheet`），不再要求 idle 静态图。素材同步发现文件数变了会整个替换数据目录里的角色文件夹，旧图不会残留。
- 网页：有动画的姿态一律播动画，系统要求减少动画时也播（只删了精灵图这一条；补帧翻页只显示第一张、点击 Q 弹等其他「减少动画」处理没动）；精灵图读不出来改播待机动画（`sheet.fallback`，只试一次）。
- **省电模式整个删掉**（设置页开关、外壳 `PowerSave`、网页 `setPowerSave`），用户说以后按程序实际另做。网页里闲着自动停特效的那段改名「特效降帧」，和设置无关。
- 测试：test-anim 改成断言有动画的姿态没有静态图、减少动画时照样播、读不到改播待机；test-ui 等待机动画画出来再量点击区域。7 个网页测试和 -MotionTests 全过，构建通过。**没装到本机、没在桌面上看过**（尤其启动时第一眼、换动作时有没有空白一下）。
- 生成新动作的标准站姿：作者 `anim/待机呼吸休闲.webp` 第一帧，绿底版在本机 `D:\video llm\素材\idle_anim_green_1280.png`。图生视频改用云端（Comfy 账号、海螺 H3 Max Turbo 和 Seedance），过程见本机记忆 local-video-gen。

### 下一步

2026-11-15 用户说：宣传视频**已经发布**；作者**不会再更新动作**，以后的新动作只能自己做。当时定这一轮只在本机做、交接也只留本机；11-16 用户改成发 0.4.2，代码已推送，交接文档用户没说要推，留在本机。

**2026-11-15～16 做的（已随 0.4.2 发布，本机也装了 0.4.2）**：
- 额度换模型后不清：`plugin/hooks/register.ts` 会话开始时 `$.session.usage()` 拿到结果但一个认得的额度都没有，就写空额度 `NO_QUOTA`（`{ text: '', low: false, bars: [] }`），网页不显示额度、不算紧张、不换钱袋档位。没直接删文件：外壳读不到文件时会跳过，旧数字一直留在页面上。`usage()` 抛错时不动。测试加在 `scripts/test-quota.cjs`。**没在真实会话里验证**：要重新 `install.ps1` 才生效；如果官方账号刚开会话时 `usage()` 也是空的，额度会在第一次回复前空一下，回复后由 `session.measure` 写回。
- 圣诞收了装点圣诞树 v2（三版随机）。之前说它超出窗口左边，量下来最左 124 像素，比已在用的装点圣诞树（132）只多 8 像素，好几段在用的动画更靠外；首尾都是抱书站姿。见 `anim/SOURCE.md` 末尾。
- 台词（用户让 Claude 看着改）：傲娇点击 `pout` 改成「哼，戳什么戳……」「才、才没有很开心呢！」「……哼，不理你了。」（原来说「摸」，但这段是点击反应、画面是扭头）；早上好「早上好～我先刷个牙」（画面在刷牙，原来说「刚刷完」）；中午「午饭真香～」（原来「想吃便当」，画面已经在吃）；晚上「晚上好，我在吃晚饭～」（原来「点上灯了」，画面是吃晚餐）。点击四段 `clipLines` 和新动作台词对照画面看过，没改。
- 7 个网页测试全过。
- **运行方式**（2026-11-16，用户要求「下载下来双击就能待在桌面上」，本机保持跟着 Claude、待在窗口里）：设置页「通用」新增「跟着 Claude / 独立运行」，所有几只共用，存在 `~/.claudia/run.json`（不放 settings.json：别的那只改了会被第一只存设置时盖掉），每只每秒按文件修改时间看一次，改了就跟上并刷新设置页。
  - 跟着 Claude = 0.4.1 的样子。独立运行 = Claude 关了也不走（`Pet.Follow.cs` 的 `FollowTick` 跳过退出）；选了「待在 Claude 窗口里」但看不到 Claude 窗口（没开或收进托盘，最小化不算）时先待在桌面上，Claude 窗口出来再回去（`WantDesktop` / `CheckRunMode` / `SwitchArea`，不改存着的 `mode`）。改回跟着 Claude 时重新计时 30 秒，不会马上退出。
  - 默认值（`Program.ChooseRunMode`，只在没有 run.json 时选一次）：已有 settings.json、由 Claude 叫出来（`--ensure` 现在带 `--by-claude` 启动）、已接入插件或 MCP 的，都是跟着 Claude；只有第一次用、自己双击、又没接入的才设独立运行 + 待在桌面上。所以 0.4.1 升上来的照旧。
  - 菜单退出的第一次提示按运行方式说「下次打开我就回来」/「下次打开 Claude 我再出来」；多开页说明改成「跟着 Claude 运行时，Claude 关掉后全部一起退出」。
  - 验证：构建通过，7 个网页测试和 `-MotionTests` 全过。2026-11-16 用户同意后做了桌面实测（单独数据目录、只停不带 `--mcp` 的进程，测完重新打开安装版）：第一次用 + Claude 叫出来 / 第一次用 + 自己打开（本机已接入）/ 升级上来 → 都是跟着 Claude、待在窗口里；独立运行 + 选窗口 → Claude 开着时待在窗口里，改 run.json 一秒内切到跟着 Claude 再切回；独立运行 + 选桌面 → 桌面。**没测到的**：独立运行时关掉 Claude 她留下并移到桌面（得关掉 Claude 本身）；设置页上点那两个按钮（测的是改文件，同一条路）；「没接入过 Claude」那条默认值分支（本机插件和 MCP 都接着）。

**接下来**：
0. **自己做新动作**：用户想在本机（RTX 4060 Laptop 8 GB）部署轻量开源图生视频模型做小动画。Claude 的评估见本次对话结论：可以试，候选 Wan2.2 TI2V-5B（ComfyUI + 显存卸载）或 FramePack；难点是透明底（要逐帧抠图，头发边缘会闪）、长相漂移、首尾回到标准站姿、镜头不能动。规格照作者的：640×360 一帧、120 帧、12 fps、8×15 拼成 5120×5400 的 webp，第 1 帧人物在 x 206–444、y 40–321。用户还没定要不要装。
1. 原来等作者出的放烟花（元旦）、吃饺子 / 收红包 / 写福字（春节）不会来了，要做只能自己做。
2. VS Code 支持、让桌宠接入 LLM 对话：用户定**暂时不做**。
3. **等用户实测确认的**：火气新数值（每秒降 4、门槛 25 / 55 / 90）；额度「已用」和橙色额度条；中间帧（撞头、站不稳、趴地、摔倒、派活、查资料、看书）。
4. **没处理、交给用户决定的**：静态姿态的晃动和特效 SVG 仍按 60 帧画；精灵图单张解码约 110 MB；审查遗留几条（见「0.3.0 → 代码审查」）；还剩 23 个单张静态 + 7 套翻页（见「2026-11-08～10」）。

### 做事的规矩（用户习惯）

- 输出用简体中文。Windows 上 shell 先用 Git Bash，PowerShell 只用 7；改现有文件前遵守 `~/.claude/skills/local-operation-gate-cc` 门禁。
- 已经定下的手感、火气数值、动画配置、观感，不经用户同意不改；会影响观感的改动先说清楚，用户只看最后的审核，交之前先自查（对齐、眼睛、书、手的左右、头顶高度）。
- 提交不加 Claude 署名（作者用 GitHub noreply 邮箱，项目 `.claude/settings.local.json` 已关署名）；只推 `main`，不要 `git push --all`；推送和发版要用户明确说。公开文件里不写本机用户路径、邮箱。
- 生图：本机 Codex 额度不多了（2026-11-07）。用户提过可以用 ChatGPT 网页版生图；内置浏览器不能上传附图，要附参考图得用 Claude in Chrome。能用合成、对齐解决的先不生图（有事问你那次的教训：分别画的几张眼睛、书的大小每张都不一样，最后去掉了翻页）。
- 测量和桌面行为的工具在工作树 `build/perf-tools/`（说明见里面的 README，不进 git）：测试版用单独数据目录和 WebView2 调试口启动，经 CDP 切状态测占用。

## 0.4.1（2026-11-10 晚）

用户定：在 0.4.0 上加「待在桌面上」和多开，参照 dsh-pet 的桌面模式，然后发 0.4.1，之后在这一版上做宣传视频。

- **窗口跟随**（`Pet.Follow.cs` 的 `WatchClaudeMoves` / `FollowPlace`）：原来每 0.1 秒查一次 Claude 窗口位置，拖窗口时一格一格跳着跟（用户说「一卡一卡」）。现在挂 `EVENT_OBJECT_LOCATIONCHANGE`，只挂在 Claude 主窗口所在的进程上，Claude 窗口一挪就摆；0.1 秒的定时检查留着兜底。dsh-pet 没有可参考的代码：它的窗口内模式是画在网页里的元素，不存在跨程序跟窗口。
- **桌面模式**（`Pet.Follow.cs` 的 `DesktopPlace` / `PlaceOnDesktop` / `KeepOnTop` / `AreaRect`，设置键 `mode` = `desktop`、`desk` = `{x, y}`）：照 dsh-pet 的行为，始终置顶、每 5 秒重新钉一次；活动范围是所在显示器的工作区，拖着时按鼠标所在的显示器算（能拖到另一块屏）；默认站在主屏右下角任务栏上面；Claude 关了一样退出。物理、走路、保存位置都改成问 `AreaRect`，不再直接问 `ClaudeRect`。
- **多开**（`Pet.Pets.cs`、`Program.cs`、`Store.cs`）：每只是一个独立进程，第一只叫 `main`，多开的由它带起来（`claudia-pet.exe --pet 2 [--mode desktop|claude]`），最多 4 只额外的。各有自己的设置文件和 WebView2 数据目录（`~/.claudia/pets/<编号>/`），所以名字、大小、待在哪、闲置动作互不影响；名单在 `~/.claudia/pets.json`。没有照 dsh-pet 做成一个进程多个窗口：现在「一个进程就是一只」的结构里托盘、快捷键、设置都是静态的，拆开风险大。
  - 托盘、系统通知、隐藏快捷键只归第一只。它把「hide / show / quit」写进 `~/.claudia/pets-signal`，别的每秒看一眼照做；第一只不在了，别的 3 秒内跟着退出。
  - 设置页「多开」（`web/settings.html` 的 `renderPets`，外壳 `PetList` / `HandlePetCommand`）一次管理所有的：改名、待在哪、送走、再来一只。改的是别的那只时，往 `~/.claudia/pets-cmd/<编号>.json` 放一条指令，那一只下一秒读到照做，所以页面要一两秒才刷新。
  - 右键菜单：所有的都有「多开和位置…」；多开的那几只底部是「送走这一只」「送走所有新加的」（用户定：不能连第一只一起退）。送走会从名单里去掉、不保留名字和位置。
- **没验证的**：多显示器（含把桌面上的她拖到另一块屏）；多只同时拖、飞的流畅度和实际内存；全屏应用时桌面上那只会盖在上面（dsh-pet 也是）。多开的那几只打开自己的设置时，「接入 Claude」「通知」「快捷键」几页对它们没有意义，没有隐藏。
- **已知小问题**：发版前有一次日志记到第 2 只「没能通知第一只退出」，当时的先后顺序没还原出来；那条路径（全部退出）之后已经换成「送走所有新加的」，不再走那个通知。`Program.cs` 里给它用的 `QuitAllEvent` 监听还留着，现在没有调用方。
- 宣传视频在 `build/video-tools/`（不进 git），**旁白和画面 2026-11-11 已定稿**：成片 `video/out/claudia-pet-宣传视频-v9-配音-晓伊.mp4`（2 分 28 秒，带字幕，edge-tts「晓伊」配音），封面定用橙底（16:10、16:9、4:3 各一张）。还没加背景音乐（等用户给有授权的曲子），还没发布。怎么改、怎么重新出片，以及用户对这条片子定过的事，都写在本机的 `build/video-tools/交接.md`。

## 项目定位

Windows 上独立维护的 Claude 桌宠。基于 CrossPet，参考 dsh-pet；来源与许可集中在 NOTICE.md、LICENSE 和素材说明中。关于页只简要介绍来源，不列出功能删改历史。

命名（用户 2026-11-04 定）：仓库名、项目名、软件名都是 `claudia-pet`（GitHub 仓库名同此；程序 `claudia-pet.exe`、安装目录 `Programs\claudia-pet`、插件名、MCP 配置项、窗口和托盘标题）。只有桌宠角色叫 `claudia`。数据目录 `~/.claudia` 和代码内部名称（C# 命名空间 `Claudia`、互斥锁、`claudia.app` / `claudia.data` 虚拟域名、localStorage 键）按用户选择没有改。0.1.0 叫 Claudia（`Programs\Claudia`、MCP 项 `claudia`），接入和撤销时会清掉这两个旧条目，卸载脚本也会删旧目录。

默认名牌为 `claudia`，支持用户改名。当前图标为 Claudia 抱 Clawd 的透明头像，程序与托盘使用同一份 ICO。

## 目录与组成

| 位置 | 职责 |
|---|---|
| `app/src/` | WPF、WebView2 外壳，跟随窗口、接入配置、通知、托盘和设置 |
| `web/` | 人物、气泡、特效、互动、物理驱动与设置页 |
| `plugin/` | Claude Code hooks，把状态、额度和通知写到本机 |
| `characters/claude/` | Claude 娘立绘、台词和角色配置 |
| `icon/` | 抱 Clawd 图标及生成说明 |
| `scripts/`、`tests/` | 构建、安装、卸载和验证 |
| `upstream/` | 原项目许可和版本来源记录 |

运行数据在 `%USERPROFILE%\.claudia`；安装目录为 `%LOCALAPPDATA%\Programs\claudia-pet`。数据放在用户主目录，以避开商店版 Claude 对部分 AppData 写入的重定向。

## 关键行为

- `Pet.Follow.cs`：识别 Claude 主窗口，按物理像素保存相对位置、限制范围和设置层级；不置顶于其他应用。
- `Ensure.cs` / `Mcp.cs`：通过 `--ensure` / `--mcp` 随 Claude 启动；启动路径使用独立进程以免随 Code 子进程树被回收。
- `Store.cs` / `SpriteResources.cs`：设置、角色同步、清单与图片资源。
- `Pet.Physics.cs`：只转发鼠标屏幕坐标、参数、边界及消息代次，接收网页位置并移动 HWND。拖动和飞行时窗口线程很忙，而 WPF 里鼠标输入的优先级低于网页消息和脚本回调，松开消息曾晚到 0.15～0.2 秒，导致甩不动、乱飞、松手有延迟。所以（2026-11-04 修）：轨迹点用 `GetMouseMovePointsEx` 取系统鼠标历史（真实坐标和发生时间），每帧统一发给网页一次；松手由每帧检查物理按键状态判断，不等松开消息；开始拖动前也确认按键确实还按着。`pet-motion.js` 松手时剔掉松手之后的点，再按 dsh-pet 原样取松手前 200ms 的轨迹算速度。
- `dsh-physics.js`：直接摘录的 dsh-pet 物理函数；`pet-motion.js` 用网页帧循环驱动拖动和飞行。不要再混入另一套 C# 物理公式。
- `idle-policy.js` / `Pet.Behavior.cs`：动作池及频率，安静／标准／活泼约为 90／45／20 秒，带 ±20% 浮动。
- `click-sequence.js`：220ms Q 弹后才执行原有点击互动；连点保留摸头次数，新工作或拖动优先。点击反应（2026-11-06 照 dsh-pet 改）：每点一下都从点击动画池随机抽一段、从第一帧重演（`index.html` 的 `pickClickPose` / `replay`）；池子是摸头 `pat` 4 段 + 傲娇 `pout`（「点击回应-傲娇生气」）1 段，每段机会一样。`pout` 的台词是 Claude 起草的，用户未审。
- 生气一串（2026-11-06 用户定）：不耐烦换回静态图（按新比例重画），和鼓脸、红温、赌气一样是静态、按火气一档档走；傲娇生气动画不再当不耐烦，只做点击反应。
- `motion-mood.js`：移动期间保存怒气，停稳 800–1200ms 后处理。工作、等待回答及多会话优先；最小化或手动隐藏时延后结算。普通飞行不加怒气；撞边加（2026-11-06 用户定）：用力撞边一次 +5，抽中碰边动作时只按动作算：撞头 +7、摔倒 +9、摇晃 → 趴地 +12（`index.html` 的 `ANGER_HIT` / `ANGER_TUMBLE`）。被甩照旧每次 +7。每秒降 4，25 / 55 / 90 分别是不耐烦 / 鼓脸 / 红温（2026-11-07 用户说太容易红温，从每秒降 2、20 / 45 / 75 调过来；`index.html` 的 `ANGER_DECAY`、`ANGER_AT`）。
- `tumble.js`：被扔出去碰边时演不演、演哪套（概率 n×50%÷7 封顶 50%，一次扔出最多一次）。碰顶边撞头，碰左右边撞头 / 摔倒 / 摇晃各 1/3，碰底边 6 成摔倒 4 成摇晃；撞头在撞上时换图，其余停稳后才演；每个动作先演开场再接循环动作（同 CrossPet 的 m-jolt 写法）；演完才结算情绪，演过就不再晕乎乎；干活时只闪 0.8 秒，等回答时只说一句，多会话不触发。
- 额度（2026-11-06 修）：插件只在 Code 会话收到回复时写 `claude-quota.json`，数字来自那次回复；Chat 标签里的对话插件收不到，桌宠就一直停在上次的数（插件这边补不了，`$.session.usage()` 也只给上一次回复的数）。所以外壳把文件修改时间一起交给 `setQuota`，网页用 `QuotaBars.fresh` 每分钟按当前时间重算：过了重置时间的窗口算满、标「已重置」，紧张与否和钱袋档位跟着重算；超过 20 分钟没更新加一行「N 分钟/小时前的数据」。测试：`scripts/test-quota.cjs`。
- `Pet.Notices.cs` / `TaskNoticePolicy.cs`：通知分类、前台过滤和去重。新版插件按会话保存短事件队列；旧会话兼容状态文件提醒。

## 动画动作（claude-pet 动作包）

2026-11-05 实现，已装到本机，已提交到 main（未发版）：
- 20 个姿态（待机、思考、写东西、敲命令、整理记忆、睡觉、开心、吃惊、被摸头、不耐烦、再见、哼歌、伸懒腰、打哈欠和六个节日）改播 hunmer 的 claude-pet 动作包精灵图，文件原样放在 `characters/claude/anim/`（24 张，约 45 MB），来源和每张的用途见其中的 `SOURCE.md`。作者已在 hunmer/aboutme-pets#1 书面授权（CC BY-NC-SA 4.0，署名 hunmer）。
- `Store.Manifest` 把 `anim\` 里的文件交给网页（`sheets`），`SpritePath` 多认 `/characters/<角色>/anim/<图>` 这一种地址。
- 播放在 `index.html` 的 `anim` / `playSheet` / `sheetTick`：两块 canvas 交叉淡入，按人物高、脚底、中线和静态立绘对齐（作者每个动作第 1 帧人物在 640×360 帧里的 x 206–444、y 40–321）。配置在 `character.json` 的 `animations`（sheets / from / to / loop / hold / full）。
- 被替换的 22 张静态立绘已移出项目，本机备份在 `build/旧立绘备份-已被动画替换/`（不进 git，附哈希和说明），只留 `idle.webp`、`idle-blink.webp`：程序靠待机图识别角色，减少动画、读不到动画时用它兜底；省电模式下只有还有静态图的待机 / 累了退回静态。原来的「动画动作」开关已去掉（网页里 `animOn` 还在，外壳不再发）。
- 测试：`scripts/test-anim.cjs`。
- 没有动画的姿态和哪些要重画，见 `docs/立绘比例统一清单.md`。本地试验版在 `build/aboutme-src`、`build/aboutme-test`（不进 git）。

- 同日又加了动作包里的新动作（共 41 张、约 78 MB）：拖着她时盖一层「被拎起来」（`dragSheet`，松手回到原来的常态动画，被甩出火气后不盖）；闲置随机的发呆小动作 / 魔法 / 偷吃零食 / Claude 梗四组（`idle-policy.js` 的 `fidget`、`magic`、`snack`、`claude`）；偷吃时点她接被抓包（`snack_caught`）；余额按剩得最少的窗口分五档，换档时演对应钱袋（`quotaTier`）。这些只有动画、没有静态图；右键菜单「动作 → 小动作 / 余额」可以预览。新动作的台词是 Claude 起草的，用户还没审。

- 同日再加：动作包里其余的闲置内容（才艺、玩耍、吃喝、时令共 37 个，加上动物环绕、蝴蝶蜜蜂）和走路（共 81 张、约 153 MB）。
  - 时令：`animations[].when` 按月份、几点、公历日期、农历日期（`Intl` 的 chinese 历，闰月不算）筛选；`weight` 调当天专属动作的权重。
  - 闲置抽签改成先在组里平均抽一组，再在组里按权重抽，动画小动作多了也不挤掉哼歌这些。
  - 走路：`startWalk` / `walkEnded` / `stopWalk`（网页）+ `Pet.Walk.cs`（外壳逐帧平移窗口，只走水平、不出 Claude 窗口，碰边或走够就停并记位置；被拖、隐藏、换状态都停）。动画进入 `cycle` 步伐循环才开始挪；奔跑只朝左，不镜像。这一步自动测试测不到外壳，要在桌面上看。

- 衔接审查（2026-11-05）见 `docs/动作衔接审查.md`：加了离场动作 `animations[].exit` / `leaveVia`（睡觉被点醒或要干活时先演醒来，偷吃没被抓先收起零食），不耐烦演满整段，落叶只用第二版（现在共 80 张），螃蟹步从第 8 帧起步；走路收尾用 `outro`。

- 20 张静态立绘已按动画比例重画并换进项目（2026-11-05，用的是第二轮；第一轮腿太长，备份在 `build/第一轮重画-偏瘦高/`）：原图在 `D:\claudia图codex生成`（编号_720.png 原图、_0.png 压缩图），`prepare-sprites.py --only` + 表 `STANDING` 处理，每张单独缩放到和待机图一样高（帽子不算）；旧图备份在 `build/旧立绘备份-比例统一前/`。对照表在 `docs/prompts/立绘重画-统一比例/提示词.md` 的生成记录。

- 节日（2026-11-05）：国庆删除（立绘、台词、特效、菜单、`festivalOf` 里的日期都去掉了）。修了节日只说台词不演动画：`timeGreet` 原来只认静态立绘，节日换成动画后就不演了，改成有动画也算。作者以后生成的放烟花（元旦）、吃饺子 / 收红包 / 写福字（春节，和舞狮头随机轮换）要加，记在 `docs/立绘比例统一清单.md` 第六节。

## 0.3.0（2026-11-07）

0.2.0 之后的动画动作包、走路、补帧（上文和「碰边动作」一节）加上 2026-11-07 这一轮，一起发为 0.3.0。

### 卡顿（已处理）

- 根因：网页控件 WebView2CompositionControl 把网页每一帧拷进 WPF 透明窗口，外壳开销和网页帧率成正比。光晕原来是常驻 CSS 动画，网页永远 60 帧。改成脚本每秒设 12 次、和精灵图同一拍（`index.html` 的 `auraPulse`）。实测待机外壳 15% → 2–4%，GPU 进程 13–24% → 3–8%（单核，测量方法和全部数字见本机共享笔记 `性能与审查-2026-11-06.md`）。
- 精灵图改成 fetch + createImageBitmap 后台解码（`loadSheet`），换动作时页面卡住从 290–345 ms 降到约 75 ms，代价是网页进程常驻约 +130 MB；换掉的图会取消读取、释放。
- 换动作时旧动画在新图解码和交叉淡入期间接着播（`fadeOut`），同一张图接着演下一段（走路收尾、睡醒、收起零食、点击重播）沿用画布不重读（`playSheet` 的复用分支）。
- Codex（2026-11-07）：点击区域改由网页在布局变化时上报（外壳不再每 0.25 秒问）、拖动时同一位置不重复移窗、精灵图和光晕计时按需开关、启动时素材没变就不重拷（原来每次删掉重拷约 150 MB）。
- 没改、交给以后：静态姿态（碰边、生气一串）的身体晃动和特效 SVG 仍按 60 帧画（降帧会影响观感）；精灵图单张 5120×5400 解码约 110 MB（dsh-pet 用透明 WebM 视频，改要动素材）。

### 代码审查（已处理）

- Codex 审查并修了 6 处：构建输出防误删（`-Out` 只能是 build/dist 的直接子目录、先在临时目录组装）、素材同步改成增量且失败可回退、精灵图换掉后取消旧加载、插件写额度失败仍交还 Claude、接入/撤销失败返回非零退出码（卸载脚本遇到失败停下；旧版安装没有构建标记时照常卸载、提示核对配置）、多会话卡片不再倒回旧动作。报告在 `docs/性能优化与审查修复报告-2026-11-07.md`。
- 窗口闪：Claude 被激活时系统把它提到桌宠上面，原来压住 60–95 ms 才摆回来。外壳订阅前台切换（`Pet.Follow.cs` 的 `OnForeground`），之后 0.5 秒后台线程每 1 ms 查一次（SWP_ASYNCWINDOWPOS）。每帧检查的版本实测降到 10–30 ms；后台线程版本没能在有效测试里量到，待用户实测。
- 已知没改：`index.html` 的 `shakingUntil`、`shakeEndTimer` 从未赋值、`resumeWork` 无人调用（拖动中来工作事件会立刻换姿态）；插件多会话读改写 `claude-sessions.json` 会丢条目、`claude-notify-*.json` 不清理；`Pet.Follow` 每秒枚举全部进程。

### 用户这一轮定的

- 中间帧：只给已经补过帧的八套加，没补过的不做；见 `docs/prompts/中间帧/说明.md`（五轮修改的原因都在里面）。有事问你最后去掉翻页、只留一张静态图；看书底图换成同一批画的一张；站着的几套按头顶对齐缩放。
- 撞头第一张停到飞行结束；有火气时摔倒、撞头后直接气呼呼站起来（不先回待机、不先笑）。
- 螃蟹步只往左走；向左跑收尾从第 69 帧开始。
- 点击四段各说自己的台词（`character.json` 的 `clipLines`，Claude 起草，用户未逐句审）。
- 火气：每秒降 4，门槛 25 / 55 / 90（原来每秒降 2、20 / 45 / 75）。
- 额度：照 Claude 的样子显示已用多少，额度条统一 Claude 橙，已用 ≥ 90% 百分比标红；数据里照旧存剩余比例 `left`。

0.3.0 已发布：Release `v0.3.0`，标签指向 `02132ad`，附件 `claudia-pet-0.3.0-win.zip`（约 155 MB），记录见 `docs/PUBLISHING_AUDIT.md`。

### 之后

- 作者新加的动作已接入（2026-11-07，0.3.0 之后，未发版）：取自 `da5a6fe`，82 张原样放进 `anim/`，共 162 张。替换静态图两处：哎呀 oops → 垂头叹气冒汗、抱礼物 update → 拆礼物；圣诞加入装点圣诞树（和 v3 轮换）。其余 79 个当闲置动作：发呆 16（含早上 6–10 点的晨间刷牙）、才艺 11 种（空气吉他三版轮换）、玩耍 13、吃喝 14（6 个按季节）、时令 9、新加的「手工」组 12、Claude 梗 2（拨算盘、犯懒碎碎念 v4，画面自带文字）。没收 4 个：被落叶淹没（结束时叶子还在）、放孔明灯（人物出画）、装点圣诞树v2（之前判为超出窗口左边，按现在的量法其实没出界，待用户定）、打瞌睡被惊醒（用户定被点醒播打哈欠）。没换的：早上好（台词是泡茶，配刷牙对不上）、鼓脸（生气一串保持静态）、累了（长时间停留，揉眼睛循环会怪）、打招呼（各时段有专属图）。分组、季节见 `anim/SOURCE.md`。同日用户定：拆礼物没有专门的触发时机，放进玩耍组随机；设置里的「允许的动作」去掉，所有组都参与随机（旧设置里存的 `idleActions` 不再读取）。我们在等的放烟花（元旦）、吃饺子 / 收红包 / 写福字（春节）还没有，见 `docs/立绘比例统一清单.md` 第六节。
- 双击托盘图标（2026-11-07 用户定）：只把藏起来的她叫出来、不挪位置（`Pet.Hotkey.cs` 的 `ShowAgain`）；右键「回到默认位置」不变；程序在跑时再打开一次 exe 仍回默认位置（用户定保持）。
- ~~下一版 0.3.1~~（2026-11-10 用户改成直接发 0.4.0，已发布）：原计划等作者（hunmer/aboutme-pets，现在停在 `da5a6fe`）出放烟花 / 吃饺子 / 收红包 / 写福字，接入后一起发。发版照 0.3.0：改 `VERSION` 和 `plugin/.claude-plugin/plugin.json`，zip 带 WebView2 许可，记录写进本文和 `docs/PUBLISHING_AUDIT.md`；动画现在 146 张约 276 MB（11-09 删了 16 张），zip 会比 0.3.0 大不少。
- 用户还没逐句审的：Claude 起草的新动作台词、点击四段台词。
- 生图：本机 Codex 额度不多了（2026-11-07 用户说）；工作树里的 `build/codex-imagegen/`（`run_mid.py`、`frames_mid.py`、`crown.py`、`eyes.py`）是这轮中间帧用的工具，不进 git。

### 2026-11-08～10（已推送 main，未发版）

- **右键菜单**（`SoftMenu.cs`）：每级宽度按菜单项定（两个边栏都关掉时 WinForms 把菜单项排得比窗口宽 11 像素、Padding 不生效、MinimumSize 只撑窗口不撑菜单项，于是一二级之间有缝、二级右边一大块空白、三级盖住二级）；每项宽度 = 文字起笔 12 + 最长文字**实际墨迹**宽（全角括号自带十来像素空白，按字宽算会不齐）+ 统一右留白 32，箭头离右边 11；这一级往左开了，下一级也往左开。测试办法：草稿目录里的小程序直接用 `SoftMenu.cs` 搭同样的菜单、量各级位置并截图。
- **菜单闪烁的真正原因**（`Pet.Follow.cs` 的 `PlaceAbove`）：WPF 给桌宠配的隐形属主窗口「Hidden Window」总夹在她和 Claude 之间，「Claude 上面紧挨着的是不是她」永远不成立，平时每 0.1 秒、切窗口后每 1 毫秒重排一次，三级盖住一级时一级会闪出来。改成跳过看不见的窗口再比。纯 WinForms 测不出闪，对比「只撤掉这处修改」的版本，窗口顺序每 ~0.1 秒变一次、三级偶尔从窗口列表里消失几毫秒；修好后都没了。
- **随机动作精简**（用户定：参照 dsh-pet，它 80 个随机动作、都随时能触发；我们可以略多但不能更少，按「随时能触发」的数算）：删 16 个（发呆 抠鼻子 / 挠脚心 / 揪耳朵 / 憋气鼓腮，才艺 打拍子数拍 / 按音叉 / 摇沙锤 / 敲三角铁 / 摇小风铃，手工 7 个只留 串珠链 / 折小纸船 / 捏陶土 / 磨墨 / 编草蚱蜢），精灵图一起删（要找回从作者库取）。之后又把一些动作并进问候 / 元旦（下一条），现在**随机池 103 个、随时能触发 78 个**（77 段动画 + 哼歌 / 伸懒腰 / 抱 Clawd），其余 25 个限月份、节日或时段。
- **合并的规矩**（用户定）：只有范围广的动作（问候、节日这类）能当合并对象，明确说了做什么的动作只能被合并进去；被合并的不再单独随机、不在菜单里单独出现，它原来的时间限制也不管了。
  - 元旦 `fest_newyear` = 堆雪人 / 吃糖葫芦 / 吃年糕 随机（播到第 118 帧，糖葫芦只有 119 帧）。
  - 问候：早上好 = 晨间刷牙（台词改成「早上好，刚刷完牙～」）、中午好 = 吃午餐、下午好 = 闻咖啡豆 / 冲可可随机、晚上好 = 吃晚餐、晚安 = 拍枕头，都 `full` 演满 10 秒（不然 5.5 秒就换回去）。凌晨问候删掉（2–5 点不打招呼）。
  - 被替换的静态图（fest_newyear、五张问候、greet_dawn）挪出项目，备份在 `build/旧立绘备份-已被动画替换/`（附哈希）。
- **听你说** `listening` = 轻快记录从第 10 帧起循环（发消息后只停 1.8 秒就转思考，这段里掏出本子开始记）；**写东西**只用写代码，免得两个看着一样。静态 `listening.webp` 还留着给减少动画时用。
- **菜单重排**（`Pet.Menu.cs` 的 `ActionGroups`，只管菜单里放哪，闲置随机按 `character.json` 的 `idle` 分组抽、和菜单无关）：15 组，顺序是 状态类（日常 6、工作 14、心情 10、互动 8、问候 5）→ 闲置（小动作 14、Claude 梗 5、才艺 19、玩耍 22、手工 5、吃喝 17）→ 日历（节日 13 按日期、四季 12 按春夏秋冬）→ 走路 3、余额 6。挪过的：拆礼物 → 玩耍、累了（其实是额度见底）→ 余额、有事问你 / 道歉 → 工作、晕乎乎 → 互动、五个魔法 → 才艺、偷吃零食 → 吃喝、七夕 / 中元 / 重阳和 清明青团 / 腊八粥 / 重阳糕 → 节日。节日类菜单名改成「节日 + 动作」：元旦迎新、春节舞狮、元宵吃汤圆、端午吃粽子、中秋赏月、万圣节讨糖、圣诞装点彩树、清明吃青团、腊八喝粥、重阳吃糕。「偷吃零食（点她会被抓包）」去掉括号。
- **还在用静态图的**：累了、抱 Clawd；忙碌（左 / 右）、忙不过来（左 / 右）；得意、道歉、有事问你、不耐烦、鼓脸、红温、赌气、被哄、原谅你了、晕乎乎（生气一串是用户定的静态）；翻页的 看书 2、查资料 4、派活 8、撞头 6、站不稳 5、摔倒 4、趴地 3 帧。作者库里没用上的只剩 4 个之前弃用的（落叶第一版、孔明灯、圣诞树 v2、打瞌睡被惊醒）加上 11-09 删的 16 个。
- 测试跟着改：`test-anim.cjs` 里手工组下限 12 → 5、写东西只认写代码、元旦 / 问候的检查；11-10 发现之前一次编辑把一月份那行断言挤进了注释里，已改回来。

### 2026-11-06 这一天做完的（随 0.3.0 发布）

- 额度：Chat 里的对话插件收不到、过了重置时间不刷新的问题（见「关键行为」额度一条）。
- 补帧翻页程序：`character.json` 的 `frames.<姿态> = { seq, ms, loop }`，`index.html` 的 `flipSeq` / `startFlip` / `flipNext` / `stopFlip`；翻页硬切不交叉淡入（淡入会让前后两帧叠成重影），后面几帧预先载入，减少动画时只显示第一张，8 秒随机换图跳过这些姿态。测试 `scripts/test-flip.cjs`。
- 碰边一套按新比例重画 + 补帧（撞头 3、站不稳 3、趴地 2、摔倒 3），见 `docs/prompts/碰边补帧/说明.md`；**爬起已去掉**（两种倒法接不上同一套爬起），倒地演完直接站回去。撞边加火气（见「关键行为」）。
- 工作状态循环补帧：有事问你（重画 + 3 帧）、派活（重画 + 2 帧）、查资料、看书各 + 1，见 `docs/prompts/工作状态补帧/说明.md`。累了不补。
- 生气一串：不耐烦换回静态图（按新比例重画），四档都是静态；「傲娇生气」动画改成点击反应。点击每次都从头重播（照 dsh-pet）。
- 得意按新比例重画。用户定：红温、抱礼物、抱 Clawd、道歉都不重画；生气一串不补帧。

### 生图怎么做

2026-11-06 起由 Claude 直接调用本机 Codex 命令行生图（`codex exec`，gpt-6.1-terra、medium、`service_tier="default"` 不加速、只读沙箱），用户只确认结果。做法、脚本和教训在本机 `build/codex-imagegen/README.md`（不进 git）：**每张新开会话**（一直 resume 同一个会话，每轮都重读之前所有图，用量会越滚越大）；Codex 桌面版开着时可能占住会话；`codex.exe` 所在目录随更新会变。原图都在 `D:\claudia图codex生成`，用 `scripts/prepare-sprites.py --only` 处理（站立单张进 `STANDING`；连续或循环翻页的帧进 `SEQUENCE`，同一套同一个缩放、按头的中线对齐）。

本机留着、不进 git 的：`build/旧立绘备份-*`（已被动画替换、比例统一前、碰边补帧前、得意重画前、工作状态补帧前，都有说明和哈希）、`build/第一轮重画-偏瘦高/`、`build/aboutme-claude/`（动作包原件）、`build/codex-imagegen/`（生图脚本、提示词、每轮对话记录、原图副本）、试验副本 `build/aboutme-src`（git worktree，detached，用完可 `git worktree remove build/aboutme-src`）和 `build/aboutme-test`。

## 碰边动作（撞头 / 摇晃 / 摔倒 / 趴地）

2026-11-04 实现，随 0.2.0 发布（2026-11-06 重画并补帧、去掉爬起，见上文）：
- 立绘由 `scripts/prepare-sprites.py` 从 Codex 原图（本机 `D:\claudia图codex生成`）生成到 `characters/claude/`。
- 碰边判断在 `web/tumble.js`，播放和衔接在 `index.html` 的 `tumble*` 函数，`pet-motion.js` 报出碰到哪条边。
- 设置开关 `tumbleActions` 默认打开，右键「动作 → 互动」里能单独预览。

台词已由用户审定写进 `character.json`；被晃出火气（或在赌气）时改说 `…Angry` 生气版台词，站回去后直接发火。特效在 `effects.js`：撞头时头顶转星星（`bonkStars`），摔倒、站不稳、趴地着地时扬一次灰（`landingDust`）。

还差：
- 实际甩动的手感（速度下限 200 像素/秒、各段时长）等用户实测后再调。

完整设计见本地文件 `build/new-sprites/交接-新动作.md`（不进 git），提示词和附图已提交在 `docs/prompts/`。

## 构建与验证

```powershell
pwsh -NoProfile -File scripts/build.ps1
```

构建脚本使用 PowerShell 7 自带的 Roslyn，引用 .NET Framework 4.8 和下载的 WebView2 SDK。默认生成 `dist/claudia-pet`。

JavaScript 验证需要 Node.js（本机使用 24 系列）。界面和情绪测试还需要可解析的 Playwright 模块和已安装的 Microsoft Edge。

本机 PATH 里没有 `node`，用 Codex 自带的 Node v24.22.1 和它的 Playwright；变量只在当前窗口生效，不改系统配置。该路径随 Codex 更新可能变化，使用前先核实：

```powershell
$nodeDir = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\node"
$node = "$nodeDir\bin\node.exe"
$env:NODE_PATH = "$nodeDir\node_modules"
& $node scripts/test-physics.cjs
& $node scripts/test-behavior.cjs
& $node scripts/test-ui.cjs
& $node scripts/test-mood.cjs
& $node scripts/test-anim.cjs
& $node scripts/test-quota.cjs
& $node scripts/test-flip.cjs
pwsh -NoProfile -File scripts/build.ps1 -Out build/native-tests -MotionTests
```

`scripts/test-physics.ps1` 直接调用 `node`，PATH 里没有 Node 时会失败，改用上面的写法。

`test-physics.cjs` 可额外接收原版 dsh-pet `shared-core.js` 路径进行数值对照。`-MotionTests` 使用未显示的 WPF 窗口检查松手位置、过期帧过滤及通知策略，不改用户配置。

## 验证边界

- 用户已确认当前抛掷手感；数值对照、浏览器帧循环、交接与情绪场景已做自动检查。
- Windows 系统通知的实际弹出尚未通过真实 Code 会话完整验收；通知受 Windows 设置影响。
- 2026-11-04 用户完全退出并重开 Claude 后验证：Claude 16:38:57 启动，16:39:02 MCP（`claudia-pet.exe --mcp`）以独立进程拉起桌宠；新插件路径同时生效，状态写入 `~/.claudia\state`。Claude 自动更新、右键退出后同一次运行不再出现（`user-quit`）仍未验证。
- 多显示器、不同 DPI 和 Windows 10 尚未完整验收。

## 修改与发布边界

保留现有用户设置、已接受的抛掷手感、来源说明和许可原文。普通修改不需要重做接入；`install.ps1` 不加 `-Connect` 可更新程序而不改 Claude 接入配置。

已清理旧内部命名、其他角色特效、旧层级策略、闲置反馈／皮肤卡片实现、空额度任务及过时注释。额度来自插件文件；没有自动更新器和额度提前恢复庆祝。来源和许可保留。验证与发布状态见 [发布审计](docs/PUBLISHING_AUDIT.md)。2026-11-04 已发布为公开仓库 https://github.com/kirito1207/claudia-pet（远端 `origin`，默认分支 `main`）。同日删库重建过一次：最初推上去的两个带 Claude 署名的提交改写后仍留在 GitHub、首页贡献者一直显示 claude，用户自己删了仓库，再用同名、同简介新建公开仓库，只推 `main`；核对后首页贡献者只有 kirito1207，旧提交 `af6e614`、`de92ba8` 已查不到。2026-11-04 发布了 0.2.0（GitHub Release `v0.2.0`，附解压即用的 `claudia-pet-0.2.0-win.zip`，详见发布审计）；以后发版：改 `VERSION` 和 `plugin/.claude-plugin/plugin.json`，构建后把 `dist/claudia-pet` 打成 zip 附上。整理前的完整开发历史在本地分支 `archive/full-history`，去掉 Claude 署名前的两个提交在 `archive/before-strip-coauthor`，都只留本机，不要推送：以后推送只推 `main`，不要用 `git push --all`。本项目的 `.claude/settings.local.json`（不进 git）放行了 `gh repo create kirito1207/claudia-pet *` 和 `git push -u origin main` 两条命令，并关闭了提交和 PR 的 Claude 署名（用户不希望 Claude 出现在 GitHub 贡献者里）。
