#!/usr/bin/env python3
"""Headless checks for the panel layout, KConfig writer and GenoThemeFox."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import apply_layout as layout
import firefox_theme
import kdeconfig

BALTHASAR = """
Output: 1 DP-3 uuid-a
	enabled
	priority 1
	Geometry: 864,864 2560x1440
Output: 2 DP-2 uuid-b
	enabled
	priority 3
	Geometry: 0,864 864x1536
Output: 3 DP-1 uuid-c
	enabled
	priority 2
	Geometry: 408,0 1536x864
Output: 4 HDMI-A-1 uuid-d
	disabled
	priority 4
	Geometry: 0,0 1920x1080
"""

ALL_SENSORS = {
    layout.CPU, layout.MEM, layout.GPU,
    layout.CPU_MAX, layout.CPU_MIN, layout.GPU_TEMP,
}
ALL_PLASMOIDS = set(layout.THIRD_PARTY)


def exists_all(_name):
    return True


def plugins(plan, role):
    panel = next(p for p in plan["panels"] if p["role"] == role)
    return [w["plugin"] for w in panel["widgets"]]


def test_kscreen_and_balthasar_shape():
    screens = layout.parse_kscreen_text(BALTHASAR)
    assert [s["name"] for s in screens] == ["DP-3", "DP-1", "DP-2"]
    assert screens[0]["primary"] and screens[0]["landscape"]
    assert screens[1]["landscape"] and not screens[2]["landscape"]
    assert not layout.is_laptop(screens)
    plan = layout.build_plan(screens, ALL_SENSORS, ALL_PLASMOIDS, "file:///wall.png", exists_all)
    assert [p["role"] for p in plan["panels"]] == ["primary-status", "primary-dock", "landscape-mini"]
    assert plan["panels"][2]["screen"]["name"] == "DP-1"
    assert plan["panels"][2]["floating"] and plan["panels"][2]["height"] == 46
    status = plugins(plan, "primary-status")
    assert status[:6] == [
        "zayron.simple.separator",
        "org.kde.plasma.lock_logout",
        "zayron.simple.separator",
        "org.kde.plasma.systemtray",
        "zayron.simple.separator",
        "org.kde.plasma.panelspacer",
    ]
    assert status[-4:] == [
        "com.himdek.kde.plasma.overview",
        "zayron.simple.separator",
        "org.kde.plasma.digitalclock",
        "zayron.simple.separator",
    ]
    assert status.count("org.kde.plasma.systemmonitor.cpu") == 6
    titles = []
    for widget in next(p for p in plan["panels"] if p["role"] == "primary-status")["widgets"]:
        appearance = widget["config"].get("Appearance", {})
        if appearance.get("title"):
            titles.append((appearance["title"], appearance["chartFace"]))
    assert titles[0] == ("CPU", "org.kde.ksysguard.piechart")
    assert ("GPU", "org.kde.ksysguard.textonly") in titles
    cpu = next(w for w in next(p for p in plan["panels"] if p["role"] == "primary-status")["widgets"]
               if w["config"].get("Appearance", {}).get("title") == "CPU"
               and w["config"]["Appearance"]["chartFace"].endswith("piechart"))
    assert cpu["config"]["SensorColors"][layout.CPU] == "77,107,255"
    assert "org.kde.plasma.battery" not in plan["panels"][0]["widgets"][3]["config"]["General"]["extraItems"]
    dock = plugins(plan, "primary-dock")
    assert dock[:3] == [
        "org.kde.plasma.kickoff",
        "org.kde.plasma.panelspacer",
        "org.kde.plasma.icontasks",
    ]
    launchers = next(w for w in next(p for p in plan["panels"] if p["role"] == "primary-dock")["widgets"]
                     if w["plugin"] == "org.kde.plasma.icontasks")["config"]["General"]["launchers"]
    assert "applications:io.github.cucumberfeet.Glide.desktop" in launchers
    assert "applications:genocommand.desktop" in launchers
    assert "applications:shutter-encoder.desktop" in launchers
    assert launchers.split(",")[0] == "applications:org.kde.konsole.desktop"
    mini = plugins(plan, "landscape-mini")
    assert mini == [
        "org.kde.plasma.digitalclock",
        "org.kde.plasma.showdesktop",
        "org.kde.plasma.marginsseparator",
        "org.kde.plasma.kickoff",
        "org.kde.plasma.pager",
        "org.kde.plasma.icontasks",
    ]


def test_filters_missing_apps_sensors_and_laptop():
    screens = [{
        "name": "eDP-1", "index": 0, "x": 0, "y": 0, "width": 1707, "height": 1067,
        "primary": True, "landscape": True, "edp": True, "enabled": True, "priority": 1,
    }]
    assert layout.is_laptop(screens)
    have = {"org.kde.konsole.desktop", "systemsettings.desktop", "genocommand.desktop"}

    def exists(name):
        return name in have

    plan = layout.build_plan(
        screens, {layout.CPU, layout.MEM}, {"zayron.simple.separator"}, "file:///w.png", exists,
    )
    assert len(plan["panels"]) == 2
    assert plan["laptop"]
    tray = next(w for w in plan["panels"][0]["widgets"] if w["plugin"] == "org.kde.plasma.systemtray")
    assert "org.kde.plasma.battery" in tray["config"]["General"]["shownItems"]
    assert "org.kde.plasma.clipboard" not in tray["config"]["General"]["shownItems"]
    status = plugins(plan, "primary-status")
    assert "org.kde.netspeedWidget" not in status
    assert "org.kde.olib.thermalmonitor" not in status
    assert status.count("org.kde.plasma.systemmonitor.cpu") == 4  # cpu + ram, no gpu
    launchers = next(w for w in plan["panels"][1]["widgets"] if w["plugin"] == "org.kde.plasma.icontasks")
    text = launchers["config"]["General"]["launchers"]
    assert "shutter-encoder" not in text
    assert "io.github.cucumberfeet.Glide" not in text
    assert "applications:genocommand.desktop" in text
    assert "applications:org.kde.konsole.desktop" in text
    assert "preferred://filemanager" in text
    assert "applications:systemsettings.desktop" in text


def _paint(text, code="01;32"):
    return f"\x1b[{code}m{text}\x1b[0;0m"


def test_coloured_kscreen_doctor_output():
    # Plasma 6 colours the labels even when stdout is a pipe. Without stripping,
    # parse_kscreen_text used to match nothing and silently use default_screen().
    casper = "\n".join([
        _paint("Output: ") + "1 eDP-1 c5b9ff50-1111-2222-3333-444444444444",
        "\t" + _paint("enabled"),
        "\t" + _paint("connected"),
        "\t" + _paint("priority ") + "1",
        _paint("\tGeometry: ", "01;33") + "0,0 1707x1067",
        _paint("\tScale: ", "01;33") + "1.5",
        _paint("\tRotation: ", "01;33") + "1",
    ])
    screens = layout.parse_kscreen_text(casper)
    assert len(screens) == 1
    assert screens[0]["name"] == "eDP-1"
    assert (screens[0]["width"], screens[0]["height"]) == (1707, 1067)
    assert screens[0]["edp"] and screens[0]["primary"] and screens[0]["landscape"]
    assert layout.is_laptop(screens, batteries=[])
    plan = layout.build_plan(screens, {layout.CPU}, set(), "file:///w.png", exists_all, batteries=["BAT0"])
    assert plan["laptop"]
    assert "BAT0" in plan["laptopReason"]
    tray = next(w for w in plan["panels"][0]["widgets"] if w["plugin"] == "org.kde.plasma.systemtray")
    assert "org.kde.plasma.battery" in tray["config"]["General"]["shownItems"]

    melchior = "\n".join([
        _paint("Output: ") + "1 HDMI-A-1 aaaa",
        "\t" + _paint("enabled"),
        "\t" + _paint("priority ") + "1",
        _paint("\tGeometry: ", "01;33") + "0,0 1536x864",
        _paint("Output: ") + "2 DP-3 bbbb",
        "\t" + _paint("enabled"),
        "\t" + _paint("priority ") + "2",
        _paint("\tGeometry: ", "01;33") + "1536,0 864x1536",
        _paint("\tRotation: ", "01;33") + "2",
        _paint("Output: ") + "3 HDMI-A-2 cccc",
        "\t" + _paint("disabled", "01;31"),
        "\t" + _paint("priority ") + "3",
        _paint("\tGeometry: ", "01;33") + "0,0 1920x1080",
    ])
    screens = layout.parse_kscreen_text(melchior)
    assert [s["name"] for s in screens] == ["HDMI-A-1", "DP-3"]
    assert screens[0]["landscape"] and screens[0]["primary"]
    assert not screens[1]["landscape"]
    plan = layout.build_plan(screens, {layout.CPU}, set(), "file:///w.png", exists_all, batteries=[])
    assert [p["role"] for p in plan["panels"]] == ["primary-status", "primary-dock"]
    assert not plan["laptop"]
    text = layout.describe_screens(plan)
    assert "HDMI-A-1 1536x864 landscape primary" in text
    assert "DP-3 864x1536 portrait secondary" in text


def test_kscreen_json_scale_and_rotation():
    casper = json.dumps({
        "outputs": [{
            "name": "eDP-1",
            "enabled": True,
            "connected": True,
            "priority": 1,
            "pos": {"x": 0, "y": 0},
            "size": {"width": 2560, "height": 1600},
            "scale": 1.5,
            "rotation": 1,
        }]
    })
    screens = layout.parse_kscreen_json(casper)
    assert len(screens) == 1
    assert screens[0]["name"] == "eDP-1"
    assert (screens[0]["width"], screens[0]["height"]) == (1707, 1067)
    assert screens[0]["edp"]

    melchior = json.dumps({
        "outputs": [
            {
                "name": "HDMI-A-1",
                "enabled": True,
                "connected": True,
                "priority": 1,
                "pos": {"x": 0, "y": 0},
                "size": {"width": 1920, "height": 1080},
                "scale": 1.25,
                "rotation": 1,
            },
            {
                "name": "DP-3",
                "enabled": True,
                "connected": True,
                "priority": 2,
                "pos": {"x": 1536, "y": 0},
                "size": {"width": 1920, "height": 1080},
                "scale": 1.25,
                "rotation": 2,
            },
            {
                "name": "HDMI-A-2",
                "enabled": False,
                "connected": True,
                "priority": 3,
                "pos": {"x": 0, "y": 0},
                "size": {"width": 1920, "height": 1080},
                "scale": 1,
                "rotation": 1,
            },
        ]
    })
    screens = layout.parse_kscreen_json(melchior)
    assert [(s["name"], s["width"], s["height"], s["landscape"]) for s in screens] == [
        ("HDMI-A-1", 1536, 864, True),
        ("DP-3", 864, 1536, False),
    ]
    assert not layout.is_laptop(screens, batteries=["BAT0"])


def test_battery_marks_a_single_non_edp_screen_as_a_laptop():
    screens = [{
        "name": "Unknown-1", "index": 0, "x": 0, "y": 0, "width": 1920, "height": 1080,
        "primary": True, "landscape": True, "edp": False,
    }]
    assert not layout.is_laptop(screens, batteries=[])
    assert layout.is_laptop(screens, batteries=["BAT0"])
    plan = layout.build_plan(screens, set(), set(), "file:///w.png", exists_all, batteries=["BAT0"])
    assert plan["laptop"]
    tray = next(w for w in plan["panels"][0]["widgets"] if w["plugin"] == "org.kde.plasma.systemtray")
    assert "org.kde.plasma.battery" in tray["config"]["General"]["extraItems"]


def test_melchior_portrait_has_no_panel():
    screens = layout.parse_kscreen_text("""
Output: 1 HDMI-A-1 aaa
	enabled
	priority 1
	Geometry: 0,0 1536x864
Output: 2 DP-3 bbb
	enabled
	priority 2
	Geometry: 1536,0 864x1536
""")
    plan = layout.build_plan(screens, {layout.CPU}, set(), "file:///w.png", exists_all)
    assert [p["role"] for p in plan["panels"]] == ["primary-status", "primary-dock"]
    assert len(plan["screens"]) == 2


def test_appletsrc_roundtrip_and_backup():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        config = tmp / "config"
        data = tmp / "data"
        config.mkdir()
        original = """[Containments][10]
activityId=abc
formfactor=0
immutability=1
lastScreen=0
plugin=org.kde.plasma.folder
wallpaperplugin=org.kde.image

[Containments][10][Applets][11]
immutability=1
plugin=org.kde.plasma.analogclock

[Containments][10][Wallpaper][org.kde.image][General]
FillMode=0
Image=file:///old.png

[Containments][20]
formfactor=2
immutability=1
lastScreen=0
location=4
plugin=org.kde.panel

[Containments][20][Applets][21]
immutability=1
plugin=org.kde.plasma.kickoff

[Containments][20][General]
AppletOrder=21

[ScreenMapping]
itemsOnDisabledScreens=
"""
        (config / "plasma-org.kde.plasma.desktop-appletsrc").write_text(original, encoding="utf-8")
        (config / "plasmashellrc").write_text("[Updates]\nperformed=/usr/share/example.js\n", encoding="utf-8")
        screens = layout.parse_kscreen_text(BALTHASAR)
        plan = layout.build_plan(screens, {layout.CPU, layout.MEM}, ALL_PLASMOIDS, "file:///wall.png", exists_all)
        assert layout.backup_configs(config, data) is True
        layout.apply_plan_to_configs(config, plan, lock_screen=True)
        text = (config / "plasma-org.kde.plasma.desktop-appletsrc").read_text(encoding="utf-8")
        assert "plugin=org.kde.plasma.analogclock" in text
        assert "activityId=abc" in text
        assert "plugin=org.kde.plasma.kickoff" in text  # the new dock, not the old panel id
        assert "[Containments][20]" not in text
        assert "Image=file:///wall.png" in text
        assert "FillMode=2" in text
        assert text.count("plugin=org.kde.panel") == 3
        shell = (config / "plasmashellrc").read_text(encoding="utf-8")
        assert "performed=/usr/share/example.js" in shell
        assert "panelOpacity=2" in shell
        assert "floatingApplets=1" in shell
        assert "thickness=34" in shell
        assert "thickness=46" in shell
        lock = (config / "kscreenlockerrc").read_text(encoding="utf-8")
        assert "Image=file:///wall.png" in lock
        assert "FillMode=2" in lock
        backup_applets = (layout.backup_dir(data) / "plasma-org.kde.plasma.desktop-appletsrc").read_text(encoding="utf-8")
        assert layout.backup_configs(config, data) is False
        layout.apply_plan_to_configs(config, plan, lock_screen=True)
        assert (layout.backup_dir(data) / "plasma-org.kde.plasma.desktop-appletsrc").read_text(encoding="utf-8") == backup_applets
        assert (config / "plasma-org.kde.plasma.desktop-appletsrc").read_text(encoding="utf-8").count("plugin=org.kde.panel") == 3
        layout.restore_configs(config, data)
        assert (config / "plasma-org.kde.plasma.desktop-appletsrc").read_text(encoding="utf-8") == original


def test_kdeconfig_nested_and_commas():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "kdeglobals"
        kdeconfig.write_entry(path, ["KDE"], "widgetStyle", "kvantum")
        kdeconfig.write_entry(path, ["General"], "font", "Rajdhani,10,-1,5,500,0,0,0,0,0,0,0,0,0,0,1,Medium")
        kdeconfig.write_entry(path, ["KDE"], "widgetStyle", "kvantum")
        text = path.read_text(encoding="utf-8")
        assert text.count("widgetStyle=kvantum") == 1
        assert "font=Rajdhani,10,-1,5,500,0,0,0,0,0,0,0,0,0,0,1,Medium" in text
        lock = Path(tmp) / "kscreenlockerrc"
        kdeconfig.write_entry(lock, ["Greeter", "Wallpaper", "org.kde.image", "General"], "Image", "file:///x.png")
        assert "[Greeter][Wallpaper][org.kde.image][General]" in lock.read_text(encoding="utf-8")


def test_firefox_profiles_are_idempotent():
    theme = ROOT / "themes/firefox/GenoThemeFox"
    manifest = json.loads((theme / "manifest.json").read_text(encoding="utf-8"))
    colors = manifest["theme"]["colors"]
    assert colors["toolbar"] == "#080a24"
    assert colors["toolbar_text"] == "#4d6bff"
    assert colors["toolbar_field"] == "#020205"
    assert colors["tab_line"] == "#ff0000"
    assert colors["frame"] == colors["popup"] == "#080a24"
    assert colors["tab_loading"] == "#ff0000"
    css = (theme / "userChrome.css").read_text(encoding="utf-8")
    for value in colors.values():
        assert value in css
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)
        ini_dir = home / ".mozilla/firefox"
        ini_dir.mkdir(parents=True)
        profile = ini_dir / "abcd.default-release"
        profile.mkdir()
        (profile / "user.js").write_text('user_pref("browser.startup.homepage", "about:blank");\n', encoding="utf-8")
        (profile / "chrome").mkdir()
        (profile / "chrome/userChrome.css").write_text("/* user rule */\n#urlbar { opacity: 0.9; }\n", encoding="utf-8")
        (ini_dir / "profiles.ini").write_text(
            "[InstallABC]\nDefault=abcd.default-release\nLocked=1\n\n"
            "[Profile0]\nName=default-release\nIsRelative=1\nPath=abcd.default-release\nDefault=1\n",
            encoding="utf-8",
        )
        flat = home / ".var/app/org.mozilla.firefox/.mozilla/firefox"
        flat.mkdir(parents=True)
        (flat / "profiles.ini").write_text(
            "[Profile0]\nName=flat\nIsRelative=1\nPath=flat.default\nDefault=1\n",
            encoding="utf-8",
        )
        (flat / "flat.default").mkdir()
        written, messages = firefox_theme.apply_home(home, theme, running=True)
        assert len(written) == 2
        text = (profile / "user.js").read_text(encoding="utf-8")
        assert 'user_pref("browser.startup.homepage", "about:blank");' in text
        assert text.count("BEGIN GenoThemeFox") == 1
        assert 'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);' in text
        chrome = (profile / "chrome/userChrome.css").read_text(encoding="utf-8")
        assert "#urlbar { opacity: 0.9; }" in chrome
        assert chrome.count("BEGIN GenoThemeFox") == 1
        assert "#4d6bff" in chrome
        assert (flat / "flat.default/chrome/userContent.css").is_file()
        firefox_theme.apply_home(home, theme, running=False)
        assert (profile / "user.js").read_text(encoding="utf-8").count("BEGIN GenoThemeFox") == 1
        assert (profile / "chrome/userChrome.css").read_text(encoding="utf-8").count("BEGIN GenoThemeFox") == 1
        assert any("quit Firefox completely" in line for line in messages)


def test_install_script_does_not_touch_panels_until_apply():
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / "home"
        home.mkdir()
        env = os.environ.copy()
        env["HOME"] = str(home)
        env.pop("XDG_CONFIG_HOME", None)
        env.pop("XDG_DATA_HOME", None)
        env["GENOTHEME_SENSORS"] = "cpu/all/usage,memory/physical/usedPercent"
        env["GENOTHEME_DESKTOP_DIRS"] = str(home / "applications")
        (home / "applications").mkdir()
        (home / "applications/org.kde.konsole.desktop").write_text("[Desktop Entry]\n", encoding="utf-8")
        script = ROOT / "install.sh"
        subprocess.run(["bash", str(script)], check=True, env=env, cwd=ROOT)
        assert not (home / ".config/plasma-org.kde.plasma.desktop-appletsrc").exists()
        assert (home / ".local/share/plasma/plasmoids/org.kde.netspeedWidget/metadata.json").is_file()
        assert (home / ".local/share/icons/GenoTheme-Icons/scalable/apps/genocommand.svg").is_file()
        assert (home / ".local/share/fonts/genotheme/Rajdhani/OFL.txt").is_file()
        assert (home / ".local/share/fonts/genotheme/Hack/Hack-Regular.ttf").is_file()
        proc = subprocess.run(["bash", str(script), "--apply"], check=True, env=env, cwd=ROOT, capture_output=True, text=True)
        out = proc.stdout + proc.stderr
        assert "widgetStyle=kvantum" in (home / ".config/kdeglobals").read_text(encoding="utf-8")
        applets = (home / ".config/plasma-org.kde.plasma.desktop-appletsrc").read_text(encoding="utf-8")
        assert "plugin=org.kde.panel" in applets
        assert "genotheme-logo" in applets
        assert "org.kde.plasma.battery" not in applets
        assert "FillMode=2" in (home / ".config/kscreenlockerrc").read_text(encoding="utf-8")
        assert "Screens (fallback): unknown 1920x1080 landscape primary" in out
        assert "kscreen-doctor returned nothing usable" in out
        assert "Backed up the existing panel config" in out
        assert "Kvantum is not installed" in out or "kvantum" in out.lower()
        assert (home / ".local/share/genotheme/panel-backup/BACKUP_INFO.txt").is_file()
        # second apply keeps the backup and does not duplicate panels
        before = (home / ".local/share/genotheme/panel-backup/BACKUP_INFO.txt").read_text(encoding="utf-8")
        subprocess.run(["bash", str(script), "--apply"], check=True, env=env, cwd=ROOT, capture_output=True, text=True)
        assert (home / ".local/share/genotheme/panel-backup/BACKUP_INFO.txt").read_text(encoding="utf-8") == before
        assert applets.count("plugin=org.kde.panel") == (home / ".config/plasma-org.kde.plasma.desktop-appletsrc").read_text(encoding="utf-8").count("plugin=org.kde.panel")
        subprocess.run(["bash", str(script), "--restore-panels"], check=True, env=env, cwd=ROOT, capture_output=True, text=True)
        assert not (home / ".config/plasma-org.kde.plasma.desktop-appletsrc").exists()


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print("ok", test.__name__)
    print(f"{len(tests)} tests passed")


if __name__ == "__main__":
    main()
