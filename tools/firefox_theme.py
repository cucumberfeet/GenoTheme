#!/usr/bin/env python3
"""Install GenoThemeFox into Firefox default profiles.

Release Firefox rejects unsigned themes, so this writes userChrome.css,
userContent.css and a marked block in user.js instead of an .xpi.
"""
import argparse
import configparser
import json
import os
import subprocess
import sys
from pathlib import Path

BEGIN_CSS = "/* BEGIN GenoThemeFox */"
END_CSS = "/* END GenoThemeFox */"
BEGIN_JS = "// BEGIN GenoThemeFox"
END_JS = "// END GenoThemeFox"
DAEMON_THEME_ID = "{28127a6f-9a96-4256-b4d9-87b54b7ffc1c}"
DARK_THEME_ID = "firefox-compact-dark@mozilla.org"

ROOTS = (
    Path(".mozilla/firefox/profiles.ini"),
    Path(".config/mozilla/firefox/profiles.ini"),
    Path(".var/app/org.mozilla.firefox/.mozilla/firefox/profiles.ini"),
    Path(".var/app/org.mozilla.firefox/.config/mozilla/firefox/profiles.ini"),
)


def upsert_block(text, begin, end, body):
    block = f"{begin}\n{body.strip()}\n{end}\n"
    start = text.find(begin)
    finish = text.find(end)
    if start != -1 and finish != -1 and finish >= start:
        finish_end = finish + len(end)
        if finish_end < len(text) and text[finish_end] == "\n":
            finish_end += 1
        return text[:start] + block + text[finish_end:]
    if text and not text.endswith("\n"):
        text += "\n"
    if text and not text.endswith("\n\n"):
        text += "\n"
    return text + block


def read_profiles(ini_path):
    parser = configparser.RawConfigParser()
    parser.optionxform = str
    parser.read(ini_path, encoding="utf-8")
    base = ini_path.parent
    chosen = []
    for section in parser.sections():
        if section.startswith("Install") and parser.has_option(section, "Default"):
            chosen.append(parser.get(section, "Default"))
    if not chosen:
        for section in parser.sections():
            if section.startswith("Profile") and parser.get(section, "Default", fallback="") == "1":
                if parser.has_option(section, "Path"):
                    chosen.append(parser.get(section, "Path"))
                    break
    if not chosen:
        for section in parser.sections():
            if section.startswith("Profile") and parser.has_option(section, "Path"):
                chosen.append(parser.get(section, "Path"))
                break
    resolved = []
    for rel in chosen:
        is_rel = True
        for section in parser.sections():
            if parser.has_option(section, "Path") and parser.get(section, "Path") == rel:
                is_rel = parser.get(section, "IsRelative", fallback="1") == "1"
                break
        path = Path(rel)
        if is_rel and not path.is_absolute():
            path = base / rel
        resolved.append(path)
    return resolved


def profile_roots(home):
    home = Path(home)
    found = []
    for rel in ROOTS:
        ini = home / rel
        if ini.is_file():
            found.append(ini)
    return found


def firefox_is_running():
    try:
        proc = subprocess.run(
            ["pgrep", "-a", "-f", "firefox"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return False
    for line in proc.stdout.splitlines():
        # Ignore this installer if it ever shows up, and ignore the pgrep line.
        if "firefox_theme.py" in line:
            continue
        lower = line.lower()
        if "firefox" in lower:
            return True
    return False


def select_dark_theme(profile):
    """Disable the Daemon2.0 theme and enable the built-in Dark theme.

    extensions.activeThemeID in user.js is not enough: Firefox stores the
    enabled theme in extensions.json and rewrites that file when it quits.
    Compact Dark is an in-app theme, not a lightweight theme, so the chrome
    colours still come from userChrome.css. Returns a short status string.
    """
    path = Path(profile) / "extensions.json"
    if not path.is_file():
        return "no extensions.json yet; userChrome.css still paints the window"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "extensions.json is not valid JSON; left it unchanged"
    addons = data.get("addons")
    if not isinstance(addons, list):
        return "extensions.json has no add-on list; left it unchanged"
    themes = [a for a in addons if isinstance(a, dict) and a.get("type") == "theme"]
    dark = next((a for a in themes if a.get("id") == DARK_THEME_ID), None)
    daemon = next((a for a in themes if a.get("id") == DAEMON_THEME_ID), None)
    if dark is None and daemon is None:
        return "no Dark or Daemon theme entry in extensions.json"
    backup = path.with_name("extensions.json.bak-genotheme")
    if not backup.exists():
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    if dark is None:
        daemon["userDisabled"] = True
        daemon["active"] = False
    else:
        for theme in themes:
            enable = theme.get("id") == DARK_THEME_ID
            theme["userDisabled"] = not enable
            theme["active"] = enable
            if "softDisabled" in theme:
                theme["softDisabled"] = False
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if dark is None:
        return "Daemon2.0 theme disabled; built-in Dark theme is not in this profile"
    if daemon is None:
        return f"active theme set to {DARK_THEME_ID}"
    return f"active theme set to {DARK_THEME_ID}; Daemon2.0 disabled"


def apply_profile(profile, theme_dir):
    profile = Path(profile)
    profile.mkdir(parents=True, exist_ok=True)
    chrome = profile / "chrome"
    chrome.mkdir(parents=True, exist_ok=True)
    for name, begin, end in (
        ("userChrome.css", BEGIN_CSS, END_CSS),
        ("userContent.css", BEGIN_CSS, END_CSS),
    ):
        body = (theme_dir / name).read_text(encoding="utf-8")
        dest = chrome / name
        current = dest.read_text(encoding="utf-8") if dest.exists() else ""
        dest.write_text(upsert_block(current, begin, end, body), encoding="utf-8")
    body = (theme_dir / "user.js").read_text(encoding="utf-8")
    dest = profile / "user.js"
    current = dest.read_text(encoding="utf-8") if dest.exists() else ""
    dest.write_text(upsert_block(current, BEGIN_JS, END_JS, body), encoding="utf-8")
    return select_dark_theme(profile)


def apply_home(home, theme_dir, running=None):
    """Return (profiles_written, messages)."""
    messages = []
    written = []
    for ini in profile_roots(home):
        profiles = read_profiles(ini)
        if not profiles:
            messages.append(f"GenoThemeFox: {ini} has no default profile.")
            continue
        for profile in profiles:
            if not profile.is_dir():
                messages.append(f"GenoThemeFox: default profile path does not exist yet: {profile}")
                continue
            theme_status = apply_profile(profile, theme_dir)
            written.append(profile)
            messages.append(f"GenoThemeFox installed in {profile} ({theme_status})")
    if not written and not any("no default profile" in m or "does not exist" in m for m in messages):
        messages.append(
            "GenoThemeFox: no Firefox profiles.ini under ~/.mozilla/firefox, "
            "~/.config/mozilla/firefox, or the org.mozilla.firefox flatpak. "
            "Start Firefox once so it creates a profile, then re-run ./install.sh --apply."
        )
    is_running = firefox_is_running() if running is None else running
    if written and is_running:
        messages.append(
            "Firefox is running. Quit it completely (including the tray) and start it "
            "again so userChrome.css loads. If it is still open it will save the old "
            "theme choice over extensions.json when it quits; run ./install.sh --apply "
            "once more after it has quit so Daemon2.0 stays disabled."
        )
    elif written:
        messages.append("Restart Firefox if it is open so GenoThemeFox loads.")
    return written, messages


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("apply",))
    p.add_argument("--home", default=str(Path.home()))
    p.add_argument("--theme", required=True)
    args = p.parse_args(argv)
    theme = Path(args.theme)
    _written, messages = apply_home(args.home, theme)
    for line in messages:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
