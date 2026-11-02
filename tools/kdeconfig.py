#!/usr/bin/env python3
"""Tiny KConfig writer used when kwriteconfig6 is not installed.

Understands the same flags install.sh passes to kwriteconfig6:

    kdeconfig.py --file kdeglobals --group KDE --key widgetStyle kvantum
    kdeconfig.py --file kscreenlockerrc --group Greeter --group Wallpaper \\
        --group org.kde.image --group General --key Image file:///wallpaper.png

--file is resolved under --config-home (default $XDG_CONFIG_HOME or ~/.config)
unless it is absolute.
"""
import argparse
import os
import sys
from pathlib import Path


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


def write_entry(path, groups, key, value):
    path = Path(path)
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    sections = parse_ini(text)
    header = "".join(f"[{g}]" for g in groups)
    set_key(sections, header, key, value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_ini(sections), encoding="utf-8")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--file", required=True)
    p.add_argument("--group", action="append", required=True)
    p.add_argument("--key", required=True)
    p.add_argument("value")
    p.add_argument("--config-home", default="")
    args = p.parse_args(argv)
    path = Path(args.file)
    if not path.is_absolute():
        home = args.config_home or os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
        path = Path(home) / path
    write_entry(path, args.group, args.key, args.value)
    return 0


if __name__ == "__main__":
    sys.exit(main())
