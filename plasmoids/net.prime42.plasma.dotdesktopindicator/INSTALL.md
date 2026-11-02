# Install

This plasmoid installs per-user with `kpackagetool6`. No system-wide packaging step is required.

The package id is:

```text
net.prime42.plasma.dotdesktopindicator
```

## Fedora / Nobara

Assuming you are already in a Plasma 6 session and this project directory exists locally:

```bash
cd /path/to/dot-desktop-indicator
kpackagetool6 -t Plasma/Applet -r net.prime42.plasma.dotdesktopindicator
kpackagetool6 -t Plasma/Applet -i .
systemctl --user restart plasma-plasmashell.service
```

After installation, add the widget from panel edit mode so Plasma inserts it into the panel rather than the desktop containment flow.

If the remove step reports that the package is not installed yet, ignore that and continue with the install command.

Upgrade without removing first:

```bash
cd /path/to/dot-desktop-indicator
kpackagetool6 -t Plasma/Applet -u .
systemctl --user restart plasma-plasmashell.service
```

Uninstall:

```bash
kpackagetool6 -t Plasma/Applet -r net.prime42.plasma.dotdesktopindicator
systemctl --user restart plasma-plasmashell.service
```

## Arch / CachyOS

The commands are the same for a local per-user install:

```bash
cd /path/to/dot-desktop-indicator
kpackagetool6 -t Plasma/Applet -r net.prime42.plasma.dotdesktopindicator
kpackagetool6 -t Plasma/Applet -i .
systemctl --user restart plasma-plasmashell.service
```

After installation, add the widget from panel edit mode.

Upgrade without removing first:

```bash
cd /path/to/dot-desktop-indicator
kpackagetool6 -t Plasma/Applet -u .
systemctl --user restart plasma-plasmashell.service
```

Uninstall:

```bash
kpackagetool6 -t Plasma/Applet -r net.prime42.plasma.dotdesktopindicator
systemctl --user restart plasma-plasmashell.service
```

## Install from a copied zip archive

If you copy the plasmoid to another machine as a zip archive, install it directly from the archive:

```bash
kpackagetool6 -t Plasma/Applet -r net.prime42.plasma.dotdesktopindicator
kpackagetool6 -t Plasma/Applet -i /path/to/net.prime42.plasma.dotdesktopindicator.zip
systemctl --user restart plasma-plasmashell.service
```

Example command to create that archive from the parent directory of this project:

```bash
cd /path/to/dot-desktop-indicator
mkdir -p dist
zip -r dist/net.prime42.plasma.dotdesktopindicator.zip metadata.json contents LICENSE README.md
```

## Fallback Plasma shell restart

If `systemctl --user restart plasma-plasmashell.service` is not available in your session, restart the shell with:

```bash
kquitapp6 plasmashell
plasmashell --replace &
```

## Where the package is installed

Per-user installs go into the standard local Plasma package location managed by KPackage:

```text
~/.local/share/plasma/plasmoids/net.prime42.plasma.dotdesktopindicator
```
