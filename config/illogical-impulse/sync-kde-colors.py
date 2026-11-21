#!/usr/bin/env python3
"""Translate the current Illogical Impulse palette into a Plasma color scheme."""

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import NamedTemporaryFile


def scheme_text(palette: dict[str, str], mode: str) -> str:
    def rgb(hex_color: str) -> str:
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", hex_color):
            raise ValueError(f"Invalid palette color: {hex_color!r}")
        return ",".join(str(channel) for channel in bytes.fromhex(hex_color[1:]))

    window = "surface_container"
    header = "secondary_container"
    header_text = "on_secondary_container"
    neutral, positive = ("#e9c16a", "#8cdb9d") if mode == "Dark" else ("#7c5900", "#1f693b")
    rows = {
        "Window": (window, "surface_container_high", "on_surface", "on_surface_variant"),
        "View": ("surface", "surface_container_low", "on_surface", "on_surface_variant"),
        "Button": ("surface_container_high", "surface_container_highest", "on_surface", "on_surface_variant"),
        "Header": (header, "surface_variant", header_text, header_text),
        "Header][Inactive": (window, "surface_container_high", "on_surface_variant", "on_surface_variant"),
        "Selection": ("primary", "primary", "on_primary", "on_primary"),
        "Tooltip": ("surface_container_high", "surface_container_highest", "on_surface", "on_surface_variant"),
        "Complementary": ("surface_container_low", "surface_container", "on_surface", "on_surface_variant"),
    }

    parts = [
        "# Generated from the active Illogical Impulse Material palette.",
        "",
        "[General]",
        f"Name=Illogical Impulse {mode}",
        f"ColorScheme=IllogicalImpulse{mode}",
        "",
        "[KDE]",
        "frameContrast=0.2",
        "",
        "[ColorEffects:Inactive]",
        "Enable=false",
        "ChangeSelectionColor=true",
        "Color=0,0,0",
        "ColorAmount=0",
        "ColorEffect=0",
        "ContrastAmount=0",
        "ContrastEffect=0",
        "IntensityAmount=0",
        "IntensityEffect=0",
        "",
        "[ColorEffects:Disabled]",
        "Enable=true",
        "ChangeSelectionColor=false",
        "Color=0,0,0",
        "ColorAmount=0",
        "ColorEffect=0",
        "ContrastAmount=0.5",
        "ContrastEffect=1",
        "IntensityAmount=0",
        "IntensityEffect=0",
    ]

    for name, (background, alternate, foreground, muted) in rows.items():
        selected = name == "Selection"
        use_text = selected or name.startswith("Header")
        parts += [
            "",
            f"[Colors:{name}]",
            f"BackgroundNormal={rgb(palette[background])}",
            f"BackgroundAlternate={rgb(palette[alternate])}",
            f"ForegroundNormal={rgb(palette[foreground])}",
            f"ForegroundInactive={rgb(palette[muted])}",
            f"ForegroundActive={rgb(palette[foreground if use_text else 'primary'])}",
            f"ForegroundLink={rgb(palette[foreground if use_text else 'primary'])}",
            f"ForegroundVisited={rgb(palette[foreground if use_text else 'tertiary'])}",
            f"ForegroundNegative={rgb(palette[foreground if selected else 'error'])}",
            f"ForegroundNeutral={rgb(palette[foreground] if selected else neutral)}",
            f"ForegroundPositive={rgb(palette[foreground] if selected else positive)}",
            f"DecorationFocus={rgb(palette['on_primary' if selected else 'primary'])}",
            f"DecorationHover={rgb(palette['on_primary' if selected else 'primary'])}",
        ]

    parts += [
        "",
        "[WM]",
        f"activeBackground={rgb(palette[header])}",
        f"activeBlend={rgb(palette[header])}",
        f"activeForeground={rgb(palette[header_text])}",
        f"inactiveBackground={rgb(palette[window])}",
        f"inactiveBlend={rgb(palette[window])}",
        f"inactiveForeground={rgb(palette['on_surface_variant'])}",
    ]
    return "\n".join(parts) + "\n"


def read_kde_setting(key: str) -> str:
    return subprocess.check_output(
        ["kreadconfig6", "--file", "kdeglobals", "--group", "General", "--key", key],
        text=True,
    ).strip()


def main() -> None:
    home = Path.home()
    state_home = Path(os.environ.get("XDG_STATE_HOME") or home / ".local/state")
    data_home = Path(os.environ.get("XDG_DATA_HOME") or home / ".local/share")
    palette_path = state_home / "quickshell/user/generated/colors.json"
    palette = json.loads(palette_path.read_text(encoding="utf-8"))

    # Match Quickshell's hslLightness < 0.5 mode check.
    channels = bytes.fromhex(palette["background"].removeprefix("#"))
    mode = "Dark" if min(channels) + max(channels) < 255 else "Light"
    scheme_id = f"IllogicalImpulse{mode}"
    scheme_file = data_home / "color-schemes" / f"{scheme_id}.colors"
    contents = scheme_text(palette, mode).encode("utf-8")

    scheme_file.parent.mkdir(parents=True, exist_ok=True)
    if not scheme_file.is_file() or scheme_file.read_bytes() != contents:
        with NamedTemporaryFile(dir=scheme_file.parent, delete=False) as temporary_file:
            pending_scheme = Path(temporary_file.name)
            temporary_file.write(contents)
        try:
            pending_scheme.replace(scheme_file)
        finally:
            pending_scheme.unlink(missing_ok=True)

    current_scheme = read_kde_setting("ColorScheme")
    current_hash = read_kde_setting("ColorSchemeHash")
    expected_hash = hashlib.sha1(contents, usedforsecurity=False).hexdigest()
    accent = read_kde_setting("AccentColor")

    if accent:
        subprocess.run(
            ["kwriteconfig6", "--file", "kdeglobals", "--group", "General", "--key", "AccentColor", "--delete"],
            check=True,
        )

    if current_scheme != scheme_id:
        subprocess.run(["plasma-apply-colorscheme", scheme_id], check=True)
    elif current_hash != expected_hash or accent:
        # KDE's native same-scheme reload. A transparent accent leaves the scheme colors intact.
        subprocess.run(["plasma-apply-colorscheme", "--accent-color", "transparent"], check=True)

    if read_kde_setting("ColorSchemeHash") != expected_hash:
        raise RuntimeError(f"Plasma did not load the generated {scheme_id} palette")


if __name__ == "__main__":
    main()
