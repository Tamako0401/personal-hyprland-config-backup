hl.on("hyprland.start", function()
    hl.exec_cmd("hyprlock --immediate-render --no-fade-in")
    hl.exec_cmd("fcitx5 -d")
end)
