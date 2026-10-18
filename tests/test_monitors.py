import json

from lock.monitors import Monitor, order, parse_hyprctl, parse_xrandr

XRANDR = """Screen 0: minimum 320 x 200, current 4480 x 1440, maximum 16384 x 16384
eDP-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 344mm x 193mm
   1920x1080     60.01*+
HDMI-1 connected 2560x1440+1920+0 (normal left inverted right x axis y axis) 597mm x 336mm
DP-1 disconnected (normal left inverted right x axis y axis)
DP-2 connected (normal left inverted right x axis y axis)
"""


def test_parse_xrandr_finds_connected_monitors_with_geometry():
    found = parse_xrandr(XRANDR)
    assert found == [
        Monitor(0, 0, 1920, 1080, True),
        Monitor(1920, 0, 2560, 1440, False),
    ]


def test_parse_xrandr_handles_negative_offsets():
    text = "HDMI-1 connected 1920x1080+-1920+0 (normal)"
    assert parse_xrandr(text) == [Monitor(-1920, 0, 1920, 1080, False)]


def test_parse_hyprctl_applies_scale_and_rotation():
    data = [
        {"x": 0, "y": 0, "width": 3840, "height": 2160, "scale": 2.0, "transform": 0, "focused": True},
        {"x": 1920, "y": 0, "width": 1080, "height": 1920, "scale": 1.0, "transform": 1, "focused": False},
    ]
    found = parse_hyprctl(json.dumps(data))
    assert found[0] == Monitor(0, 0, 1920, 1080, True)
    assert found[1] == Monitor(1920, 0, 1920, 1080, False)


def test_order_puts_primary_first_and_drops_bad_sizes():
    monitors = [
        Monitor(1920, 0, 2560, 1440, False),
        Monitor(0, 0, 0, 0, False),
        Monitor(0, 0, 1920, 1080, True),
    ]
    result = order(monitors)
    assert result[0].primary
    assert len(result) == 2


def test_order_marks_leftmost_primary_when_none_flagged():
    result = order([Monitor(1920, 0, 100, 100), Monitor(0, 0, 100, 100)])
    assert result[0] == Monitor(0, 0, 100, 100, True)
    assert result[1].primary is False
    