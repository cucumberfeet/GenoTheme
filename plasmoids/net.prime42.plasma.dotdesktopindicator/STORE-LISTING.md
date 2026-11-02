# KDE Store Listing

Use this file as the source text for the OpenDesktop / KDE Store product page.

## Product Basics

- Product name: `Dot Desktop Indicator`
- Product id / plugin id: `net.prime42.plasma.dotdesktopindicator`
- Category: `Plasma 6 Applets`
- License: `GPL-3.0-or-later`
- Source code: `https://github.com/T313C0mun1s7/dot-desktop-indicator`
- Project homepage: `https://github.com/T313C0mun1s7/dot-desktop-indicator`

## Short Description

`A tiny Plasma 6 panel widget that shows one hollow or solid dot per virtual desktop.`

## Long Description

```text
Dot Desktop Indicator is a very small, panel-friendly virtual desktop indicator for KDE Plasma 6.

It shows one centered dot per virtual desktop:
- inactive desktop = hollow dot
- active desktop = solid dot

The widget is designed as a clean replacement for older desktop indicator and pager-style widgets that depended on private pager internals and broke after Plasma changes.

Features:
- one dot per virtual desktop
- immediate tracking of the active desktop
- immediate updates when desktops are added, removed, renamed, or reordered
- click a dot to switch directly to that desktop
- optional mouse wheel switching
- configurable active/inactive symbols
- configurable font family and size
- configurable spacing
- optional custom active and inactive colors
- optional bold active symbol
- optional dim inactive symbols

This widget intentionally does not show thumbnails, labels, tabs, or window previews. The primary active-state indicator is glyph substitution by state.

Compatibility:
- KDE Plasma 6
- Qt 6
- Wayland-first Plasma environments
```

## Suggested Tags

Use whichever tags the form allows:

- `plasma`
- `plasma6`
- `plasmoid`
- `widget`
- `virtual-desktop`
- `desktop`
- `panel`
- `linux`
- `kde`

## Suggested Screenshot Order

1. `screenshots/Theme Colors - Active Normal - Inactive Not Dimmed (Panel).png`
2. `screenshots/Manual Colors - Active Bold - Inactive Dimmed (Panel).png`
3. `screenshots/Manual Colors - Active Bold - Inactive Dimmed (Settings).png`
4. `screenshots/Theme Colors - Active Bold - Inactive Dimmed (Settings).png`

## Suggested First Release Note

`Initial public Plasma 6 release. Panel-friendly virtual desktop dot indicator with click switching, mouse wheel switching, configurable symbols, spacing, font, and optional custom colors.`

## Upload File

Upload the prepared release archive:

```text
dist/net.prime42.plasma.dotdesktopindicator.zip
```

Build it from the repo root with:

```bash
mkdir -p dist
zip -r dist/net.prime42.plasma.dotdesktopindicator.zip metadata.json contents LICENSE README.md
```

## Pre-Publish Checklist

- Confirm the GitHub repo is public
- Confirm the latest code is pushed to `main`
- Confirm the release zip exists in `dist/`
- Confirm screenshots are ready
- Confirm the category is `Plasma 6 Applets`
- Confirm the license is `GPL-3.0-or-later`
