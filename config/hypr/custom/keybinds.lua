-- Open the shell's launcher with a dedicated chord as well as the default Super tap.
hl.bind("SUPER + ALT + Space", hl.dsp.exec_cmd("qs -c ii ipc call search toggle || fuzzel"),
    { description = "Shell: Toggle search" })

-- Keep the workspace move chord from the previous configuration.
local numberKeycodes = { 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 }
for workspace, keycode in ipairs(numberKeycodes) do
    hl.bind("SUPER + SHIFT + code:" .. keycode, function()
        hl.dispatch(hl.dsp.window.move({ workspace = workspace_in_group(workspace) }))
    end, { description = "Window: Move to workspace " .. workspace })
end
