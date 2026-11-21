-- Pointer speed relative to the original curve. Lower values move the cursor less.
local pointer_speed = 0.50
hl.device({
    name = "apple-inc.-magic-trackpad",
    accel_profile = string.format("custom 1 0 %.4f %.4f %.4f %.4f",
        0.65 * pointer_speed, 1.60 * pointer_speed, 3.00 * pointer_speed, 4.40 * pointer_speed),
    scroll_points = "1 0 0.75 1.70 2.90 4.10",
    scroll_factor = 0.1,
    natural_scroll = true,
    clickfinger_behavior = true,
    tap_to_click = true,
    tap_and_drag = true,
    drag_lock = 0,
    drag_3fg = 0,
})

-- Use the same focus action as Ctrl+Super+Left/Right, once on release.
hl.gesture({ fingers = 4, direction = "horizontal", action = "unset" })
local swipe_x = 0
local commit_distance = 180 -- previous threshold: 450 * 0.40
hl.gesture({
    fingers = 4,
    direction = "horizontal",
    action = {
        start = function()
            swipe_x = 0
        end,
        update = function(event)
            swipe_x = swipe_x + event.delta.x
        end,
        finish = function(event)
            if event.cancelled or math.abs(swipe_x) < commit_distance then return end
            -- Natural direction: swipe left to bring the workspace on the right into view.
            local workspace = swipe_x < 0 and "r+1" or "r-1"
            hl.dispatch(hl.dsp.focus({ workspace = workspace }))
        end,
    },
})

-- Free the three-finger pinch and use a four-finger contraction for search.
hl.gesture({ fingers = 3, direction = "pinch", action = "unset" })
hl.gesture({
    fingers = 4,
    direction = "pinchout",
    action = {
        finish = function(event)
            if not event.cancelled then
                hl.dispatch(hl.dsp.exec_cmd("qs -c ii ipc call search open"))
            end
        end,
    },
})
