#!/usr/bin/env python3
"""Build and apply the Balthasar GenoTheme panel layout.

The plan adapts to the machine: launchers are kept only when the desktop file
exists, sensors that are not present are dropped, and a single eDP screen gets
a battery tray item. Portrait non-primary screens get no panel. The primary
screen always gets the bottom status bar and the left dock.

`--apply` / the `apply` command writes plasma-org.kde.plasma.desktop-appletsrc
and the panel geometry in plasmashellrc. The first run copies the previous
files to $XDG_DATA_HOME/genotheme/panel-backup and later runs leave that
backup alone. `restore` copies it back.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

BLUE = "77,107,255"
MUTED = "106,112,149"
CPU = "cpu/all/usage"
MEM = "memory/physical/usedPercent"
GPU = "gpu/all/usage"
CPU_MAX = "cpu/all/maximumTemperature"
CPU_MIN = "cpu/all/minimumTemperature"
GPU_TEMP = "gpu/gpu0/temperature"

THIRD_PARTY = (
    "zayron.simple.separator",
    "org.kde.netspeedWidget",
    "org.kde.olib.thermalmonitor",
    "org.kde.mediabar",
    "com.himdek.kde.plasma.overview",
    "net.prime42.plasma.dotdesktopindicator",
)

PRIMARY_LAUNCHERS = [
    "org.kde.konsole.desktop",
    "preferred://filemanager",
    "FFPWA-01M5KAHGNZ0F3774XERCPBYQF5.desktop",
    "grok-bot.desktop",
    "preferred://browser",
    "org.kde.kate.desktop",
    "com.discordapp.Discord.desktop",
    "net.venipa.ytmdesktop.desktop",
    "steam.desktop",
    "com.blackmagicdesign.resolve.desktop",
    "com.obsproject.Studio.desktop",
    "shutter-encoder.desktop",
    "stacher7.desktop",
    "affinity-portable.desktop",
    "GLIDE",
    "org.kde.kdeconnect.sms.desktop",
    "SETTINGS",
]
SECONDARY_LAUNCHERS = [
    "preferred://filemanager",
    "FFPWA-01M5KAHGNZ0F3774XERCPBYQF5.desktop",
    "grok-bot.desktop",
    "preferred://browser",
    "SETTINGS",
]
GENOCOMMAND_DESKTOPS = (
    "genocommand.desktop",
    "io.github.cucumberfeet.GenoCommand.desktop",
    "io.github.cucumberfeet.genocommand.desktop",
    "GenoCommand.desktop",
)
CPU_HWMON = {"coretemp", "k10temp", "zenpower", "cpu_thermal", "k8temp"}
GPU_HWMON = {"amdgpu", "nvidia", "nouveau", "i915", "xe", "radeon"}
BACKUP_FILES = (
    "plasma-org.kde.plasma.desktop-appletsrc",
    "plasmashellrc",
    "kscreenlockerrc",
)


def parse_ini(text):
    sections = []
    header = None
    lines = []
    for line in text.splitlines(keepends=True):
        raw = line.rstrip("\r\n")
        if raw.startswith("[") and raw.endswith("]") and raw.count("[") == raw.count("]"):
            sections.append((header, lines))
            header = raw
            lines = []
        else:
            lines.append(line if line.endswith("\n") else line + "\n")
    sections.append((header, lines))
    return sections


def dump_ini(sections):
    out = []
    for header, lines in sections:
        if header:
            out.append(header + "\n")
        out.extend(line if line.endswith("\n") else line + "\n" for line in lines)
    text = "".join(out)
    if text and not text.endswith("\n"):
        text += "\n"
    return text


def ensure(sections, header):
    for i, (h, _lines) in enumerate(sections):
        if h == header:
            return i
    sections.append((header, []))
    return len(sections) - 1


def set_key(sections, header, key, value):
    i = ensure(sections, header)
    h, lines = sections[i]
    new = []
    found = False
    prefix = key + "="
    for line in lines:
        raw = line.rstrip("\r\n")
        if raw.startswith(prefix):
            if not found:
                new.append(f"{key}={value}\n")
                found = True
        else:
            new.append(line if line.endswith("\n") else line + "\n")
    if not found:
        new.append(f"{key}={value}\n")
    sections[i] = (h, new)


def get_key(lines, key):
    prefix = key + "="
    for line in lines:
        raw = line.rstrip("\r\n")
        if raw.startswith(prefix):
            return raw[len(prefix):]
    return None


# kscreen-doctor -o colours its labels even when stdout is not a terminal.
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def strip_ansi(text):
    return ANSI_RE.sub("", text or "")


def _finish_screens(outputs):
    enabled = [o for o in outputs if o.get("enabled") and o.get("width") and o.get("height")]
    enabled.sort(key=lambda o: (o["priority"], o["name"]))
    for i, output in enumerate(enabled):
        output["index"] = i
        output["primary"] = i == 0
        output["landscape"] = output["width"] >= output["height"]
        output["edp"] = "edp" in output["name"].lower()
    return enabled


def parse_kscreen_text(text):
    outputs = []
    current = None
    for line in strip_ansi(text).splitlines():
        m = re.match(r"Output:\s+\d+\s+(\S+)", line)
        if m:
            if current:
                outputs.append(current)
            current = {
                "name": m.group(1),
                "enabled": False,
                "priority": 1000 + len(outputs),
                "x": 0,
                "y": 0,
                "width": 0,
                "height": 0,
            }
            continue
        if current is None:
            continue
        stripped = line.strip()
        if stripped == "enabled":
            current["enabled"] = True
        elif stripped == "disabled":
            current["enabled"] = False
        m = re.search(r"priority\s+(\d+)", line)
        if m:
            current["priority"] = int(m.group(1))
        m = re.search(r"Geometry:\s+(-?\d+),(-?\d+)\s+(\d+)x(\d+)", line)
        if m:
            current["x"] = int(m.group(1))
            current["y"] = int(m.group(2))
            current["width"] = int(m.group(3))
            current["height"] = int(m.group(4))
    if current:
        outputs.append(current)
    return _finish_screens(outputs)


def parse_kscreen_json(text):
    """Parse `kscreen-doctor -j` (KScreen::ConfigSerializer).

    `size` is Output::size(): hardware pixels of the current mode, already
    transposed when rotation is Left (2) or Right (8). The Geometry line of
    `kscreen-doctor -o` is that size divided by `scale`, at `pos`. Swapping
    on rotation again turns a portrait panel (Melchior DP-3: size 1080x1920,
    rotation 8, scale 1.25, Geometry 864x1536) into a landscape one.
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    raw_outputs = data.get("outputs") if isinstance(data, dict) else data
    if not isinstance(raw_outputs, list):
        return []
    outputs = []
    for index, output in enumerate(raw_outputs):
        if not isinstance(output, dict):
            continue
        if output.get("connected") is False:
            continue
        name = str(output.get("name") or "")
        if not name:
            continue
        size = output.get("size") or {}
        pos = output.get("pos") or output.get("position") or {}
        try:
            scale = float(output.get("scale") or 1) or 1.0
            width = int(round(float(size.get("width") or 0) / scale))
            height = int(round(float(size.get("height") or 0) / scale))
        except (TypeError, ValueError):
            continue
        priority = output.get("priority") or 0
        try:
            priority = int(priority)
        except (TypeError, ValueError):
            priority = 0
        if priority <= 0:
            priority = 1000 + index
        enabled = output.get("enabled")
        if enabled is None:
            enabled = True
        outputs.append({
            "name": name,
            "enabled": bool(enabled),
            "priority": priority,
            "x": int(pos.get("x") or 0),
            "y": int(pos.get("y") or 0),
            "width": width,
            "height": height,
        })
    return _finish_screens(outputs)


def default_screen():
    return [{
        "name": "unknown",
        "enabled": True,
        "priority": 1,
        "x": 0,
        "y": 0,
        "width": 1920,
        "height": 1080,
        "index": 0,
        "primary": True,
        "landscape": True,
        "edp": False,
        "source": "fallback",
    }]


def _tag(screens, source):
    for screen in screens:
        screen["source"] = source
    return screens


def _run_kscreen(args):
    try:
        proc = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0 and not (proc.stdout or "").strip():
        return None
    return proc.stdout or ""


def detect_screens():
    text_override = os.environ.get("GENOTHEME_SCREEN_TEXT")
    if text_override:
        parsed = parse_kscreen_text(Path(text_override).read_text(encoding="utf-8", errors="replace"))
        return _tag(parsed, "text") if parsed else default_screen()
    json_override = os.environ.get("GENOTHEME_SCREEN_JSON")
    if json_override:
        parsed = parse_kscreen_json(Path(json_override).read_text(encoding="utf-8", errors="replace"))
        return _tag(parsed, "json") if parsed else default_screen()
    raw = _run_kscreen(["kscreen-doctor", "-j"])
    if raw:
        parsed = parse_kscreen_json(raw)
        if parsed:
            return _tag(parsed, "json")
    raw = _run_kscreen(["kscreen-doctor", "-o"])
    if raw:
        parsed = parse_kscreen_text(raw)
        if parsed:
            return _tag(parsed, "text")
    return default_screen()


def detect_batteries():
    """Names of /sys/class/power_supply/BAT* supplies, or GENOTHEME_BATTERIES if set.

    An empty GENOTHEME_BATTERIES means "this machine has no battery".
    """
    override = os.environ.get("GENOTHEME_BATTERIES")
    if override is not None:
        return [name for name in override.split(",") if name]
    root = Path("/sys/class/power_supply")
    if not root.is_dir():
        return []
    found = []
    for supply in sorted(root.iterdir()):
        if not supply.name.upper().startswith("BAT"):
            continue
        type_file = supply / "type"
        if type_file.is_file():
            try:
                kind = type_file.read_text(encoding="utf-8", errors="replace").strip().lower()
            except OSError:
                kind = "battery"
            if kind and kind != "battery":
                continue
        found.append(supply.name)
    return found


def laptop_decision(screens, batteries):
    """A single eDP panel is a laptop. A single screen plus BAT* is too.

    Extra monitors (a docked laptop, or Melchior) do not get a tray battery.
    """
    batteries = list(batteries or [])
    if len(screens) != 1:
        why = "no screens" if not screens else f"{len(screens)} screens"
        return False, why
    screen = screens[0]
    name = screen.get("name") or "screen"
    if screen.get("edp") and batteries:
        return True, f"single {name} and battery {', '.join(batteries)}"
    if screen.get("edp"):
        return True, f"single {name}"
    if batteries:
        return True, f"single {name} and battery {', '.join(batteries)}"
    return False, f"single {name}, no eDP connector and no battery"


def is_laptop(screens, batteries=None):
    if batteries is None:
        batteries = detect_batteries()
    laptop, _why = laptop_decision(screens, batteries)
    return laptop


def desktop_search_dirs():
    override = os.environ.get("GENOTHEME_DESKTOP_DIRS")
    if override:
        return [Path(p) for p in override.split(os.pathsep) if p]
    dirs = []
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    dirs.append(data_home / "applications")
    dirs.append(Path.home() / ".local/share/flatpak/exports/share/applications")
    dirs.append(Path("/var/lib/flatpak/exports/share/applications"))
    xdg = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share")
    for item in xdg.split(":"):
        if item:
            dirs.append(Path(item) / "applications")
    return dirs


def desktop_exists(name, dirs=None):
    dirs = desktop_search_dirs() if dirs is None else dirs
    for directory in dirs:
        if (directory / name).is_file():
            return True
    return False


def filter_launchers(items, exists):
    out = []
    for item in items:
        if item == "GLIDE":
            if exists("io.github.cucumberfeet.Glide.desktop"):
                out.append("applications:io.github.cucumberfeet.Glide.desktop")
            for name in GENOCOMMAND_DESKTOPS:
                if exists(name):
                    out.append("applications:" + name)
        elif item == "SETTINGS":
            if exists("systemsettings.desktop"):
                out.append("applications:systemsettings.desktop")
            elif exists("org.kde.systemsettings.desktop"):
                out.append("applications:org.kde.systemsettings.desktop")
        elif item.startswith("preferred://"):
            out.append(item)
        elif exists(item):
            out.append("applications:" + item)
    return out


def _hwmon_names():
    root = Path("/sys/class/hwmon")
    found = []
    if not root.exists():
        return found
    for namefile in root.glob("hwmon*/name"):
        try:
            name = namefile.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        temps = list(namefile.parent.glob("temp*_input"))
        found.append((name, bool(temps)))
    return found


def sysfs_sensors():
    found = set()
    if Path("/proc/stat").exists():
        found.add(CPU)
    if Path("/proc/meminfo").exists():
        found.add(MEM)
    names = _hwmon_names()
    if any(name in CPU_HWMON and temps for name, temps in names):
        found.add(CPU_MAX)
        found.add(CPU_MIN)
    gpu = any(name in GPU_HWMON for name, _temps in names)
    gpu = gpu or Path("/proc/driver/nvidia/gpus").exists()
    drm = Path("/sys/class/drm")
    if drm.exists():
        if any(drm.glob("card*/device/gpu_busy_percent")):
            gpu = True
        if any(drm.glob("card*/device/hwmon/hwmon*/temp*_input")):
            found.add(GPU_TEMP)
    if gpu:
        found.add(GPU)
    if any(name in GPU_HWMON and temps for name, temps in names):
        found.add(GPU_TEMP)
    return found


def detect_sensors():
    override = os.environ.get("GENOTHEME_SENSORS")
    if override is not None:
        return {item for item in override.split(",") if item}
    ids = set()
    for cmd in (
        ["qdbus6", "org.kde.ksystemstats", "/org/kde/ksystemstats", "org.kde.KSysGuardDaemon.allSensors"],
        ["qdbus", "org.kde.ksystemstats", "/org/kde/ksystemstats", "org.kde.KSysGuardDaemon.allSensors"],
    ):
        try:
            proc = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=5)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
        if proc.returncode != 0 or not proc.stdout:
            continue
        ids.update(re.findall(r"[A-Za-z][A-Za-z0-9_./]*", proc.stdout))
        if CPU in ids or MEM in ids:
            return ids
    return sysfs_sensors()


def installed_plasmoids(data_home):
    found = set()
    roots = [
        Path(data_home) / "plasma/plasmoids",
        Path("/usr/share/plasma/plasmoids"),
        Path("/usr/local/share/plasma/plasmoids"),
    ]
    for plugin in THIRD_PARTY:
        for root in roots:
            if (root / plugin / "metadata.json").is_file():
                found.add(plugin)
                break
    return found


def _monitor(title, sensor, face, label, colors):
    config = {
        "_root": {"CurrentPreset": "org.kde.plasma.systemmonitor"},
        "Appearance": {
            "chartFace": face,
            "showTitle": "false",
            "title": title,
        },
        "SensorColors": colors,
        "Sensors": {
            "highPrioritySensorIds": json.dumps([sensor], separators=(",", ":")),
            "lowPrioritySensorIds": "[]",
            "totalSensors": "[]",
        },
    }
    if label:
        config["SensorLabels"] = {sensor: label}
    if face == "org.kde.ksysguard.piechart":
        config["org.kde.ksysguard.piechart/General"] = {"smoothEnds": "false"}
    return {"plugin": "org.kde.plasma.systemmonitor.cpu", "config": config}


def _sep():
    return {"plugin": "zayron.simple.separator", "config": {}}


def _sensor_group(title, sensor, colors, label):
    return [
        _monitor(title, sensor, "org.kde.ksysguard.piechart", None, colors),
        _monitor(title, sensor, "org.kde.ksysguard.textonly", label, colors),
        _sep(),
    ]


def status_widgets(sensors, laptop, plasmoids):
    widgets = [
        _sep(),
        {
            "plugin": "org.kde.plasma.lock_logout",
            "config": {
                "General": {
                    "actionsOrder": "lockScreen,switchUser,requestShutDown,requestReboot,requestLogout,requestLogoutScreen,suspendToRam,suspendToDisk",
                    "show_lockScreen": "false",
                    "show_requestLogout": "true",
                    "show_requestLogoutScreen": "false",
                    "show_requestReboot": "true",
                    "show_requestShutDown": "true",
                    "show_suspendToRam": "true",
                }
            },
        },
        _sep(),
        _tray(laptop),
        _sep(),
        {"plugin": "org.kde.plasma.panelspacer", "config": {}},
    ]
    use_sep = "zayron.simple.separator" in plasmoids
    if not use_sep:
        widgets = [w for w in widgets if w["plugin"] != "zayron.simple.separator"]
    groups = []
    if CPU in sensors:
        groups.extend(_sensor_group("CPU", CPU, {CPU: BLUE}, "CPU"))
    if MEM in sensors:
        groups.extend(_sensor_group("RAM", MEM, {CPU: MUTED, MEM: BLUE}, "RAM"))
    if GPU in sensors:
        groups.extend(_sensor_group("GPU", GPU, {CPU: MUTED, GPU: BLUE}, "GPU"))
    if "org.kde.netspeedWidget" in plasmoids:
        groups.append({"plugin": "org.kde.netspeedWidget", "config": {}})
        groups.append(_sep())
    temps = []
    if GPU_TEMP in sensors:
        temps.append({"name": "GPU Temperature", "sensorId": GPU_TEMP})
    if CPU_MAX in sensors:
        temps.append({"name": "Maximum CPU Temperature", "sensorId": CPU_MAX})
    if CPU_MIN in sensors:
        temps.append({"name": "Minimum CPU Temperature", "sensorId": CPU_MIN})
    if temps and "org.kde.olib.thermalmonitor" in plasmoids:
        groups.append({
            "plugin": "org.kde.olib.thermalmonitor",
            "config": {"General": {"sensors": json.dumps(temps, separators=(",", ":"))}},
        })
        groups.append(_sep())
    if not use_sep:
        groups = [w for w in groups if w["plugin"] != "zayron.simple.separator"]
    widgets.extend(groups)
    widgets.append({"plugin": "org.kde.plasma.panelspacer", "config": {}})
    if "org.kde.mediabar" in plasmoids:
        widgets.append({"plugin": "org.kde.mediabar", "config": {}})
        if use_sep:
            widgets.append(_sep())
    widgets.append({"plugin": "org.kde.plasma.showdesktop", "config": {}})
    if "com.himdek.kde.plasma.overview" in plasmoids:
        widgets.append({"plugin": "com.himdek.kde.plasma.overview", "config": {}})
    if use_sep:
        widgets.append(_sep())
    widgets.append({
        "plugin": "org.kde.plasma.digitalclock",
        "config": {
            "Appearance": {
                "dateDisplayFormat": "BesideTime",
                "dateFormat": "isoDate",
                "showSeconds": "0",
                "use24hFormat": "2",
            }
        },
    })
    if use_sep:
        widgets.append(_sep())
    return widgets


def _tray(laptop):
    extra = [
        "org.kde.plasma.clipboard",
        "org.kde.plasma.notifications",
        "org.kde.plasma.bluetooth",
        "org.kde.plasma.volume",
        "org.kde.plasma.brightness",
        "org.kde.plasma.devicenotifier",
        "org.kde.kdeconnect",
        "org.kde.plasma.networkmanagement",
        "org.kde.plasma.printmanager",
        "org.kde.plasma.weather",
    ]
    if laptop:
        extra.append("org.kde.plasma.battery")
    shown = [item for item in extra if item != "org.kde.plasma.clipboard"]
    return {
        "plugin": "org.kde.plasma.systemtray",
        "config": {
            "General": {
                "extraItems": ",".join(extra),
                "shownItems": ",".join(shown),
                "hiddenItems": "org.kde.plasma.clipboard",
                "disabledStatusNotifiers": "Xwayland Video Bridge,xdg-desktop-portal-kde,plasmashell_microphone",
            }
        },
    }


def dock_widgets(launchers, plasmoids):
    widgets = [
        {
            "plugin": "org.kde.plasma.kickoff",
            "config": {"General": {"favoritesPortedToKAstats": "true", "icon": "genotheme-logo"}},
        },
        {
            "plugin": "org.kde.plasma.panelspacer",
            "config": {"General": {"expanding": "false", "length": "10"}},
        },
        {
            "plugin": "org.kde.plasma.icontasks",
            "config": {
                "General": {
                    "fill": "false",
                    "iconSpacing": "0",
                    "launchers": ",".join(launchers),
                }
            },
        },
    ]
    if "net.prime42.plasma.dotdesktopindicator" in plasmoids:
        widgets.append({
            "plugin": "net.prime42.plasma.dotdesktopindicator",
            "config": {"General": {"fontSize": "10", "spacing": "4"}},
        })
    widgets.append({
        "plugin": "org.kde.plasma.pager",
        "config": {"General": {"displayedText": "Number", "showOnlyCurrentScreen": "false"}},
    })
    return widgets


def mini_widgets(launchers):
    return [
        {"plugin": "org.kde.plasma.digitalclock", "config": {}},
        {"plugin": "org.kde.plasma.showdesktop", "config": {}},
        {"plugin": "org.kde.plasma.marginsseparator", "config": {}},
        {
            "plugin": "org.kde.plasma.kickoff",
            "config": {"General": {"favoritesPortedToKAstats": "true"}},
        },
        {"plugin": "org.kde.plasma.pager", "config": {}},
        {
            "plugin": "org.kde.plasma.icontasks",
            "config": {"General": {"launchers": ",".join(launchers)}},
        },
    ]


def _panel(role, screen, location, height, length_mode, alignment, floating, floating_applets, widgets):
    return {
        "role": role,
        "screen": {
            "index": screen["index"],
            "name": screen["name"],
            "x": screen["x"],
            "y": screen["y"],
            "width": screen["width"],
            "height": screen["height"],
            "primary": screen["primary"],
        },
        "location": location,
        "height": height,
        "lengthMode": length_mode,
        "alignment": alignment,
        "floating": floating,
        "floatingApplets": floating_applets,
        "opacity": "translucent",
        "hiding": "none",
        "widgets": widgets,
    }


def describe_screens(plan):
    screens = plan.get("screens") or []
    source = plan.get("screenSource") or "provided"
    if not screens:
        return f"Screens ({source}): none"
    bits = []
    for screen in screens:
        orient = "landscape" if screen.get("landscape", screen["width"] >= screen["height"]) else "portrait"
        role = "primary" if screen.get("primary") else "secondary"
        edp = " eDP" if screen.get("edp") else ""
        bits.append(f"{screen['name']} {screen['width']}x{screen['height']} {orient} {role}{edp}")
    text = f"Screens ({source}): " + ", ".join(bits)
    if source == "fallback":
        text += " — kscreen-doctor returned nothing usable, so this is one assumed 1920x1080 display"
    return text


def build_plan(screens, sensors, plasmoids, wallpaper, exists, batteries=None):
    if batteries is None:
        batteries = detect_batteries()
    laptop, laptop_reason = laptop_decision(screens, batteries)
    primary_launchers = filter_launchers(PRIMARY_LAUNCHERS, exists)
    secondary_launchers = filter_launchers(SECONDARY_LAUNCHERS, exists)
    primary = next(screen for screen in screens if screen["primary"])
    panels = [
        _panel("primary-status", primary, "bottom", 34, "fill", "center", False, False,
               status_widgets(sensors, laptop, plasmoids)),
        _panel("primary-dock", primary, "left", 46, "fit", "left", False, True,
               dock_widgets(primary_launchers, plasmoids)),
    ]
    for screen in screens:
        if screen["primary"] or not screen["landscape"]:
            continue
        panels.append(_panel(
            "landscape-mini", screen, "bottom", 46, "fit", "left", True, False,
            mini_widgets(secondary_launchers),
        ))
    return {
        "wallpaper": wallpaper,
        "fillMode": 2,
        "laptop": laptop,
        "laptopReason": laptop_reason,
        "batteries": list(batteries),
        "screenSource": (screens[0].get("source") if screens else None) or "provided",
        "launchers": primary_launchers,
        "secondaryLaunchers": secondary_launchers,
        "sensors": sorted(sensors),
        "screens": [
            {
                "index": screen["index"],
                "name": screen["name"],
                "x": screen["x"],
                "y": screen["y"],
                "width": screen["width"],
                "height": screen["height"],
                "primary": screen["primary"],
                "landscape": screen["landscape"],
                "edp": bool(screen.get("edp")),
            }
            for screen in screens
        ],
        "panels": panels,
    }


def backup_dir(data_home):
    return Path(data_home) / "genotheme" / "panel-backup"


def backup_configs(config_home, data_home):
    dest = backup_dir(data_home)
    info = dest / "BACKUP_INFO.txt"
    if info.exists():
        return False
    dest.mkdir(parents=True, exist_ok=True)
    config_home = Path(config_home)
    for name in BACKUP_FILES:
        src = config_home / name
        if src.is_file():
            shutil.copy2(src, dest / name)
            (dest / f"{name}.existed").write_text("1\n", encoding="utf-8")
        else:
            (dest / f"{name}.missing").write_text("1\n", encoding="utf-8")
    info.write_text(
        "GenoTheme panel backup taken before the first --apply/--layout.\n"
        "Restore with: ./install.sh --restore-panels\n"
        "Files: plasma-org.kde.plasma.desktop-appletsrc, plasmashellrc, kscreenlockerrc.\n",
        encoding="utf-8",
    )
    return True


def restore_configs(config_home, data_home):
    dest = backup_dir(data_home)
    if not (dest / "BACKUP_INFO.txt").is_file():
        raise SystemExit(
            f"No GenoTheme panel backup at {dest}. Nothing to restore."
        )
    config_home = Path(config_home)
    config_home.mkdir(parents=True, exist_ok=True)
    for name in BACKUP_FILES:
        target = config_home / name
        if (dest / f"{name}.missing").is_file():
            if target.exists():
                target.unlink()
        elif (dest / name).is_file():
            shutil.copy2(dest / name, target)
    return dest


def _containment_id(header):
    m = re.match(r"\[Containments\]\[(\d+)\]", header or "")
    return int(m.group(1)) if m else None


def _panel_ids(sections):
    ids = []
    for header, lines in sections:
        if not re.fullmatch(r"\[Containments\]\[(\d+)\]", header or ""):
            continue
        if get_key(lines, "plugin") == "org.kde.panel":
            ids.append(_containment_id(header))
    return ids


def _max_id(sections):
    highest = 0
    for header, _lines in sections:
        if not header:
            continue
        for number in re.findall(r"\[(\d+)\]", header):
            highest = max(highest, int(number))
    return highest


def _drop_containments(sections, ids):
    banned = set(ids)
    return [(h, lines) for h, lines in sections if _containment_id(h) not in banned]


def _drop_views(sections, ids):
    banned = {str(i) for i in ids}
    kept = []
    for header, lines in sections:
        m = re.match(r"\[PlasmaViews\]\[Panel (\d+)\]", header or "")
        if m and m.group(1) in banned:
            continue
        kept.append((header, lines))
    return kept


def _write_widget(sections, panel_id, applet_id, widget):
    base = f"[Containments][{panel_id}][Applets][{applet_id}]"
    set_key(sections, base, "immutability", "1")
    set_key(sections, base, "plugin", widget["plugin"])
    config = widget.get("config") or {}
    for group, entries in config.items():
        if group == "_root":
            header = base + "[Configuration]"
        else:
            header = base + "[Configuration]" + "".join(f"[{part}]" for part in group.split("/"))
        for key, value in entries.items():
            set_key(sections, header, key, value)


def _view_keys(panel):
    keys = {
        "floating": "1" if panel["floating"] else "0",
        "shell": "org.kde.plasma.desktop",
        "panelOpacity": {"adaptive": "0", "opaque": "1", "translucent": "2"}[panel["opacity"]],
    }
    if panel["lengthMode"] == "fit":
        keys["panelLengthMode"] = "1"
    elif panel["lengthMode"] == "custom":
        keys["panelLengthMode"] = "2"
    if panel["alignment"] == "left":
        keys["alignment"] = "1"
    elif panel["alignment"] == "right":
        keys["alignment"] = "2"
    if panel.get("floatingApplets"):
        keys["floatingApplets"] = "1"
    return keys


LOCATIONS = {"bottom": "4", "top": "3", "left": "5", "right": "6"}
FORMFACTORS = {"bottom": "2", "top": "2", "left": "3", "right": "3"}


def _folder_sections(sections):
    found = []
    for header, lines in sections:
        if not re.fullmatch(r"\[Containments\]\[(\d+)\]", header or ""):
            continue
        if get_key(lines, "plugin") in ("org.kde.plasma.folder", "org.kde.desktopcontainment"):
            found.append((header, lines))
    return found


def _apply_wallpaper_to_folders(sections, wallpaper, fill_mode, screens, next_id):
    folders = _folder_sections(sections)
    activity = ""
    screens_present = set()
    for header, lines in folders:
        if not activity:
            activity = get_key(lines, "activityId") or ""
        last = get_key(lines, "lastScreen")
        if last is not None:
            screens_present.add(last)
        set_key(sections, header, "wallpaperplugin", "org.kde.image")
        cid = _containment_id(header)
        wall = f"[Containments][{cid}][Wallpaper][org.kde.image][General]"
        set_key(sections, wall, "FillMode", str(fill_mode))
        set_key(sections, wall, "Image", wallpaper)
    if not folders:
        for screen in screens:
            cid = next_id
            next_id += 1
            header = f"[Containments][{cid}]"
            set_key(sections, header, "activityId", activity)
            set_key(sections, header, "formfactor", "0")
            set_key(sections, header, "immutability", "1")
            set_key(sections, header, "lastScreen", str(screen["index"]))
            set_key(sections, header, "location", "0")
            set_key(sections, header, "plugin", "org.kde.plasma.folder")
            set_key(sections, header, "wallpaperplugin", "org.kde.image")
            wall = f"[Containments][{cid}][Wallpaper][org.kde.image][General]"
            set_key(sections, wall, "FillMode", str(fill_mode))
            set_key(sections, wall, "Image", wallpaper)
            screens_present.add(str(screen["index"]))
    else:
        for screen in screens:
            if str(screen["index"]) in screens_present:
                continue
            cid = next_id
            next_id += 1
            header = f"[Containments][{cid}]"
            set_key(sections, header, "activityId", activity)
            set_key(sections, header, "formfactor", "0")
            set_key(sections, header, "immutability", "1")
            set_key(sections, header, "lastScreen", str(screen["index"]))
            set_key(sections, header, "location", "0")
            set_key(sections, header, "plugin", "org.kde.plasma.folder")
            set_key(sections, header, "wallpaperplugin", "org.kde.image")
            wall = f"[Containments][{cid}][Wallpaper][org.kde.image][General]"
            set_key(sections, wall, "FillMode", str(fill_mode))
            set_key(sections, wall, "Image", wallpaper)
    return next_id


def apply_plan_to_configs(config_home, plan, lock_screen=False):
    config_home = Path(config_home)
    config_home.mkdir(parents=True, exist_ok=True)
    applets_path = config_home / "plasma-org.kde.plasma.desktop-appletsrc"
    shell_path = config_home / "plasmashellrc"
    applets_text = applets_path.read_text(encoding="utf-8") if applets_path.exists() else ""
    shell_text = shell_path.read_text(encoding="utf-8") if shell_path.exists() else ""
    sections = parse_ini(applets_text)
    shell_sections = parse_ini(shell_text)
    old_panels = _panel_ids(sections)
    sections = _drop_containments(sections, old_panels)
    shell_sections = _drop_views(shell_sections, old_panels)
    next_id = _max_id(sections) + _max_id(shell_sections) + 1
    screens = plan.get("screens") or []
    if not screens:
        screen_by_index = {}
        for panel in plan["panels"]:
            screen_by_index[panel["screen"]["index"]] = panel["screen"]
        screens = [screen_by_index[index] for index in sorted(screen_by_index)]
    next_id = _apply_wallpaper_to_folders(sections, plan["wallpaper"], plan["fillMode"], screens, next_id)
    for panel in plan["panels"]:
        panel_id = next_id
        next_id += 1
        header = f"[Containments][{panel_id}]"
        set_key(sections, header, "activityId", "")
        set_key(sections, header, "formfactor", FORMFACTORS[panel["location"]])
        set_key(sections, header, "immutability", "1")
        set_key(sections, header, "lastScreen", str(panel["screen"]["index"]))
        set_key(sections, header, "location", LOCATIONS[panel["location"]])
        set_key(sections, header, "plugin", "org.kde.panel")
        set_key(sections, header, "wallpaperplugin", "org.kde.image")
        applet_ids = []
        for widget in panel["widgets"]:
            applet_id = next_id
            next_id += 1
            applet_ids.append(applet_id)
            _write_widget(sections, panel_id, applet_id, widget)
        set_key(
            sections,
            f"[Containments][{panel_id}][General]",
            "AppletOrder",
            ";".join(str(i) for i in applet_ids),
        )
        view = f"[PlasmaViews][Panel {panel_id}]"
        for key, value in _view_keys(panel).items():
            set_key(shell_sections, view, key, value)
        set_key(shell_sections, view + "[Defaults]", "thickness", str(panel["height"]))
    applets_path.write_text(dump_ini(sections), encoding="utf-8")
    shell_path.write_text(dump_ini(shell_sections), encoding="utf-8")
    if lock_screen:
        lock_sections = parse_ini(
            (config_home / "kscreenlockerrc").read_text(encoding="utf-8")
            if (config_home / "kscreenlockerrc").exists() else ""
        )
        set_key(lock_sections, "[Greeter]", "WallpaperPlugin", "org.kde.image")
        wall = "[Greeter][Wallpaper][org.kde.image][General]"
        set_key(lock_sections, wall, "Image", plan["wallpaper"])
        set_key(lock_sections, wall, "FillMode", str(plan["fillMode"]))
        (config_home / "kscreenlockerrc").write_text(dump_ini(lock_sections), encoding="utf-8")
    return applets_path, shell_path


def stamp_layout(template, destination, plan):
    template = Path(template)
    destination = Path(destination)
    body = template.read_text(encoding="utf-8")
    prelude = "var GENOTHEME_PLAN = " + json.dumps(plan, separators=(",", ":")) + ";\n"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(prelude + body, encoding="utf-8")


def make_plan(data_home, wallpaper, exists=None, screens=None, sensors=None, plasmoids=None):
    screens = detect_screens() if screens is None else screens
    sensors = detect_sensors() if sensors is None else set(sensors)
    plasmoids = installed_plasmoids(data_home) if plasmoids is None else set(plasmoids)
    if exists is None:
        exists = desktop_exists
    return build_plan(screens, sensors, plasmoids, wallpaper, exists)


def cmd_apply(args):
    wallpaper = args.wallpaper
    if not wallpaper.startswith("file:") and wallpaper != "GenoTheme":
        wallpaper = Path(wallpaper).resolve().as_uri()
    backed = backup_configs(args.config_home, args.data_home)
    plan = make_plan(args.data_home, wallpaper)
    apply_plan_to_configs(args.config_home, plan, lock_screen=args.lock_screen)
    if args.stamp_layout and args.layout_template:
        stamp_layout(args.layout_template, args.stamp_layout, plan)
    if backed:
        print(f"Backed up the existing panel config to {backup_dir(args.data_home)}")
    else:
        print(f"Kept the existing panel backup at {backup_dir(args.data_home)}")
    print(describe_screens(plan))
    if plan.get("screenSource") == "fallback":
        print(
            "warning: screen detection used the fallback display. "
            "Check that kscreen-doctor -j (or -o) works in this session.",
            file=sys.stderr,
        )
    battery = "yes" if plan["laptop"] else "no"
    print(
        f"GenoTheme panels: {len(plan['panels'])} "
        f"(laptop battery: {battery} — {plan.get('laptopReason', '')}, "
        f"dock launchers: {len(plan['launchers'])})"
    )
    return 0


def cmd_restore(args):
    dest = restore_configs(args.config_home, args.data_home)
    print(f"Restored panel config from {dest}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    apply_p = sub.add_parser("apply")
    apply_p.add_argument("--config-home", required=True)
    apply_p.add_argument("--data-home", required=True)
    apply_p.add_argument("--wallpaper", required=True)
    apply_p.add_argument("--lock-screen", action="store_true")
    apply_p.add_argument("--stamp-layout", default="")
    apply_p.add_argument("--layout-template", default="")
    apply_p.set_defaults(func=cmd_apply)
    plan_p = sub.add_parser("plan")
    plan_p.add_argument("--data-home", required=True)
    plan_p.add_argument("--wallpaper", required=True)
    plan_p.set_defaults(func=lambda args: print(json.dumps(make_plan(args.data_home, args.wallpaper), indent=2)) or 0)
    restore_p = sub.add_parser("restore")
    restore_p.add_argument("--config-home", required=True)
    restore_p.add_argument("--data-home", required=True)
    restore_p.set_defaults(func=cmd_restore)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
