# Dot Desktop Indicator

Dot Desktop Indicator is a KDE Plasma 6 plasmoid that shows one centered dot per virtual desktop in a compact horizontal row.

The active desktop is shown as a solid dot by default (`●`) and inactive desktops are shown as hollow dots by default (`○`). Each dot is clickable, mouse wheel switching can be enabled, and the widget is designed for panel use rather than thumbnails, labels, or preview paging.

This widget is intended for Plasma panels. Add it from panel edit mode or the panel's widget picker.

## Why this exists

This widget is intended as a small Plasma 6 replacement for older pager-style desktop indicators that depended on private pager internals and broke after Plasma changes.

This project avoids private pager imports such as `org.kde.plasma.private.pager` and uses public Plasma 6 and KWin interfaces instead.

## Features

- One indicator per virtual desktop
- Hollow dot for inactive desktops, solid dot for the active desktop by default
- Immediate updates when the active desktop changes
- Immediate updates when desktops are added, removed, reordered, or renamed
- Click a dot to switch directly to that desktop
- Optional mouse wheel switching
- Optional custom active and inactive colors
- Minimal configuration for symbols, font, spacing, colors, and wheel behavior

## Project structure

```text
.
├── .gitignore
├── LICENSE
├── metadata.json
├── README.md
├── INSTALL.md
├── DEVNOTES.md
├── STORE-LISTING.md
├── TEST-CHECKLIST.md
├── screenshots
│   └── ...
└── contents
    ├── config
    │   ├── config.qml
    │   └── main.xml
    └── ui
        ├── configGeneral.qml
        └── main.qml
```

## Dependencies

- KDE Plasma 6
- Qt 6
- KWin
- `kpackagetool6` for local install and upgrade
- `dbus-send` for the desktop-switching workaround path
- Plasma's public QML D-Bus helper module: `org.kde.plasma.workspace.dbus`

## Repository Assets

- `screenshots/` contains the panel and settings screenshots used for documentation and store publishing.
- `STORE-LISTING.md` contains prepared KDE Store/OpenDesktop listing text and release notes.
- `LICENSE` contains the repository license text.
- `dist/` is the ignored output directory for release archives built from this repo.

## Installation

Install from this project directory for the current user:

```bash
kpackagetool6 -t Plasma/Applet -i .
```

If a previous version is already installed, upgrade in place:

```bash
kpackagetool6 -t Plasma/Applet -u .
```

If you prefer a clean reinstall:

```bash
kpackagetool6 -t Plasma/Applet -r net.prime42.plasma.dotdesktopindicator
kpackagetool6 -t Plasma/Applet -i .
```

Detailed distro-oriented install steps are in [INSTALL.md](./INSTALL.md).

## Local update workflow

From the project directory:

```bash
kpackagetool6 -t Plasma/Applet -u .
systemctl --user restart plasma-plasmashell.service
```

If your session does not use the `plasma-plasmashell.service` unit, use one of these instead:

```bash
kquitapp6 plasmashell
plasmashell --replace &
```

## Uninstall

Remove the plasmoid from the current user account:

```bash
kpackagetool6 -t Plasma/Applet -r net.prime42.plasma.dotdesktopindicator
```

## Restarting Plasma Shell for testing

Preferred on Plasma 6 systems that expose the user unit:

```bash
systemctl --user restart plasma-plasmashell.service
```

Fallback:

```bash
kquitapp6 plasmashell
plasmashell --replace &
```

## Notes on Plasma 6 compatibility

- This package targets Plasma 6 and Qt 6 only.
- It uses `metadata.json`, not `metadata.desktop`.
- It does not use private pager imports.
- It does not use Plasma 5 pager examples or deprecated pager internals.
- It is intended for panel use and ships only horizontal and vertical form factors.
- It is Wayland-first in design, but because it talks to KWin's virtual desktop manager, it should behave the same way on X11-based Plasma sessions that expose the same public interface.

## Copying to another machine

You can copy either the project directory or a zip archive of it to another Plasma 6 machine and install it there with `kpackagetool6`.

Example clean release archive command:

```bash
cd /path/to/dot-desktop-indicator
mkdir -p dist
zip -r dist/net.prime42.plasma.dotdesktopindicator.zip metadata.json contents LICENSE README.md
```

Then install on the other machine:

```bash
kpackagetool6 -t Plasma/Applet -i /path/to/dist/net.prime42.plasma.dotdesktopindicator.zip
```
