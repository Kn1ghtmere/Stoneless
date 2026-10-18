# Hyprland setup for the lock screen

The lock windows have the X11 class `WaterLock` (set in `config.py` as `WINDOW_CLASS`).
Hyprland needs rules so those windows are floating, fullscreen and pinned on every monitor.

Hyprland changed its rule syntax so many times so make sure to check ur version by running this command : 

    hyprctl version

Then add the block that matches it.

## Hyprland 0.53 / 0.54 (hyprlang, `match:` syntax)

    windowrule = match:class ^(WaterLock)$, float on
    windowrule = match:class ^(WaterLock)$, fullscreen on
    windowrule = match:class ^(WaterLock)$, pin on

## Hyprland 0.55 and newer (Lua config)

    hl.window_rule({
      match = { class = "^(WaterLock)$" },
      float = true,
      fullscreen = true,
      pin = true,
    })

## Older than 0.53 (windowrulev2)

    windowrulev2 = float, class:^(WaterLock)$
    windowrulev2 = fullscreen, class:^(WaterLock)$
    windowrulev2 = pin, class:^(WaterLock)$

## Check that it worked

1. Run the app and press "lock now (test)".
2. In another terminal run `hyprctl clients | grep -A3 WaterLock`.
3. The windows should show `class: WaterLock`, `floating: 1`, `pinned: 1`.

If the class shows up under a different name, change `WINDOW_CLASS` in `config.py` and the rules to match.

## Known limits XD

- Hyprland keybinds run inside the compositor. The lock screen cannot block them, so workspace
  switching and `exec` binds still work. This is a soft lock by design.
- Multi-monitor placement of XWayland windows depends on the Hyprland version and your scaling.
  If a second monitor is not covered, note the output of `hyprctl monitors -j` for the debugging log.
