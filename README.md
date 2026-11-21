# Design My Hyprland

Arch Linux 上的 Hyprland + end_4 Illogical Impulse 个人配置，包含 Magic Trackpad 手感、四指手势、Quickshell 顶栏布局与硬件读数、Fcitx5 中文输入，以及 KDE 壁纸配色同步。

## 版本与依赖

配置取自 Hyprland **0.57.2**、libinput **1.32.0**、Matugen **4.2.0** 和 Plasma **6.8.3**。先安装带 Quickshell 的 [end_4 Illogical Impulse](https://ii.clsty.link/en/ii-qs/01setup/)，对应的 [上游提交是 `21733c3`](https://github.com/end-4/dots-hyprland/tree/21733c3ca7f4edc20faafedea844dc96002c6f7f)。

- 输入与快捷键使用 Fcitx5、Kitty、Dolphin 和 Hyprlock。Fuzzel 为搜索键的备用启动器。
- 顶栏硬件读数使用 `lm_sensors` 的 `sensors` 和 `nvtop`。CPU 温度读取 Intel `coretemp` 的封装温度，GPU 使用 `nvtop` 列出的第一块卡。
- 配色使用 Matugen、Python 3、systemd 用户服务、`kreadconfig6`、`kwriteconfig6` 和 `plasma-apply-colorscheme`。GTK 设置使用 Breeze 光标、Fluent 图标与 MiSans 字体，按需安装。
- ChatGPT 桌面入口适用于可执行文件位于 `/usr/bin/chatgpt` 的安装。

## 安装覆盖文件

从仓库根目录在 Bash 执行。已有同名配置会保留带编号的备份。

```bash
config_dir=${XDG_CONFIG_HOME:-$HOME/.config}
data_dir=${XDG_DATA_HOME:-$HOME/.local/share}
install -d "$config_dir" "$data_dir/color-schemes"
cp -a --backup=numbered config/. "$config_dir/"
cp --backup=numbered data/color-schemes/*.colors "$data_dir/color-schemes/"
for patch in "$PWD"/patches/end4-{switchwall,shell}.patch; do
  if git -C "$config_dir" apply --reverse --check "$patch" 2>/dev/null; then
    continue
  fi
  git -C "$config_dir" apply --check "$patch" &&
    git -C "$config_dir" apply "$patch" || break
done
```

`config/hypr/custom/` 由 end_4 的 `hyprland.lua` 加载。[壁纸补丁](patches/end4-switchwall.patch)保留 GNOME 的明暗偏好切换，移除了自动替换 GTK 主题和改写 VS Code 配色的调用。[桌面补丁](patches/end4-shell.patch)包含 Quickshell 顶栏、资源弹窗、简体中文翻译和 end_4 快捷键调整。升级 end_4 后，先用 `git apply --check` 检查补丁兼容性。

如需同步完整的 Quickshell 个性化设置，以下命令将模板中的壁纸和录屏目录替换为当前账号的路径。把最后一个参数 `""` 改为本机壁纸的绝对路径，或稍后运行 `qs -c ii ipc call wallpaperSelector toggle` 选择。

```bash
python3 - "$config_dir/illogical-impulse/config.json.in" "$config_dir/illogical-impulse/config.json" "" <<'PY'
import json
import shutil
import sys
from pathlib import Path

source, target = map(Path, sys.argv[1:3])
settings = json.loads(source.read_text(encoding="utf-8"))
settings["background"]["wallpaperPath"] = sys.argv[3]
settings["screenRecord"]["savePath"] = str(Path.home() / "Videos")
if target.is_file():
    shutil.copy2(target, target.with_suffix(".json.before-hyprland"))
target.write_text(json.dumps(settings, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
PY
```

重载 Hyprland 后用 `hyprctl configerrors` 检查 Lua，用 `qs -c ii log` 查看 Quickshell 日志。重新登录会加载输入法环境，并从 Hyprland 的启动钩子启动 Hyprlock 和 Fcitx5。

## Quickshell 顶栏与组件宽度

桌面补丁将活动窗口标题宽度上限设为 **350 个逻辑像素**，并按左右模块宽度补偿中心偏移。标准布局为详细媒体区预留 280 个逻辑像素，紧凑布局预留 36 个。资源和媒体所在的左侧组以栏宽的 28% 为上限计算扩展空间，再应用基础宽度下限。资源项按可用宽度缩放，长媒体标题由布局约束。

资源区常驻 CPU、GPU、内存百分比。详情弹窗显示 CPU 与 GPU 温度及内存和交换空间用量，达到 **75%** 或 **75 °C** 时使用警示色。缺少的 CPU 或 GPU 传感器读数显示为 `—`。展开与紧凑布局的宽度逻辑位于补丁中的 `BarContent.qml`。

Quickshell 的 JSON 模板保存了工具按钮、天气小部件位置、工作区编号延时 **200 ms** 和夜间色温 **5810 K**。顶栏工具按钮提供取色和录屏入口。

## 触摸板、鼠标和快捷键

[general.lua](config/hypr/custom/general.lua) 中的设备名来自 `hyprctl devices`，本机蓝牙 Magic Trackpad 为 `apple-inc.-magic-trackpad`。如果本机名称不同，修改设备块的 `name`。其中 `pointer_speed = 0.50` 缩放自定义指针曲线，`scroll_points` 定义双指滚动曲线，`scroll_factor = 0.10` 控制滚动总量。点击、轻点拖动和自然滚动也在此设备块内。Hyprland 的普通鼠标沿用 end_4 和 libinput 的默认输入设置。若同时使用 Plasma，[可选的鼠标滚动设置](optional/plasma/kcminputrc) 记录了原机两个接收器的设备级值，可按本机设备 ID 合并。

| 操作 | 行为 |
| --- | --- |
| 四指横扫 | 松手后切到相邻工作区，走与 `Ctrl+Super+←/→` 相同的完整动画。横向净位移达到 `commit_distance = 180` 才切换。 |
| 四指向内捏合 | 打开 Quickshell 应用搜索。 |
| 四指上下滑动 | 使用 end_4 的工作区总览。 |
| `Super+Alt+Space` | 打开或关闭搜索。 |
| `Super+Space` | 切换活动窗口的浮动或平铺状态。 |
| `Ctrl+Alt+A` | 区域截图。 |
| `Super+Shift+1…0` | 将窗口移到对应编号的工作区。 |

手势注册作用于 Hyprland 会话中的触摸板。调完设备倍率或横扫阈值，可用 `hyprctl reload config-only` 立即重载。

## 同步 KDE 配色

Quickshell 换壁纸或主题后，Matugen 更新 `$XDG_STATE_HOME/quickshell/user/generated/colors.json`，默认状态目录为 `~/.local/state`。systemd 的路径单元监听这个文件。Python 脚本按背景亮度生成 `IllogicalImpulseDark.colors` 或 `IllogicalImpulseLight.colors`，调用 Plasma 工具应用配色，并通过 `ColorSchemeHash` 核对加载结果。两份预生成的配色也可以单独在 Plasma 系统设置中使用。

首次启用前先在 Illogical Impulse 中换一次壁纸，生成当前调色板。如果另有 `kde-material-you-colors` 在更新同一份 KDE 配色，在 Illogical Impulse 中关闭 **Qt app theming**，让本仓库的路径服务接管。

```bash
systemctl --user daemon-reload
systemctl --user enable --now illogical-kde-colors.path
systemctl --user start illogical-kde-colors.service
kreadconfig6 --file kdeglobals --group General --key ColorScheme
journalctl --user -u illogical-kde-colors.service -n 20
```

配色写入当前账号的 `kdeglobals`，同一账号下的 KDE 应用和 Plasma 会共享这个方案。停用自动同步时执行 `systemctl --user disable --now illogical-kde-colors.path`，然后在 Plasma 系统设置中选择所需方案。

## 可选 ChatGPT 输入法入口

该包装脚本在 Hyprland Wayland 会话中为 ChatGPT 启用 Wayland text-input v3。桌面文件与脚本一同安装后，应用启动器即可使用这个入口。

```bash
install -Dm755 bin/chatgpt-hyprland "$HOME/.local/bin/chatgpt-hyprland"
install -d "$data_dir/applications"
sed "s|@CHATGPT_WRAPPER@|$HOME/.local/bin/chatgpt-hyprland|" \
  data/applications/chatgpt.desktop.in > "$data_dir/applications/chatgpt.desktop"
```

## 上游来源

Matugen 配置和两份桌面补丁以 [end-4/dots-hyprland](https://github.com/end-4/dots-hyprland/tree/21733c3ca7f4edc20faafedea844dc96002c6f7f) 为基础，适用其 [GPL-3.0 许可](LICENSES.end-4.GPL-3.0.txt)。
