# Development Notes

## Public APIs used

This plasmoid uses:

- Plasma 6 applet packaging with `metadata.json`
- Standard plasmoid configuration serialization through `contents/config/main.xml` and `plasmoid.configuration.*`
- The public Plasma compatibility module `org.kde.plasma.plasma5support` for its `executable` data source
- The public Plasma QML D-Bus module `org.kde.plasma.workspace.dbus`
- KWin's public D-Bus interface `org.kde.KWin.VirtualDesktopManager`

## APIs explicitly avoided

This project does not use:

- `org.kde.plasma.private.pager`
- Deprecated Plasma 5 pager examples
- Private pager models or pager internals
- A thumbnail pager or window preview backend

## Why D-Bus was used

KWin exposes a public virtual desktop manager D-Bus interface at:

```text
service: org.kde.KWin
path: /VirtualDesktopManager
interface: org.kde.KWin.VirtualDesktopManager
```

The installed `org.kde.kwin` QML import present on Plasma systems is primarily KWin's own scripting and effects API surface, not a normal plasmoid-targeted import module. For a regular Plasma 6 widget package, the safer public route is to talk to KWin through the documented D-Bus interface and use Plasma's public D-Bus QML helpers.

## How desktop state is observed

The plasmoid reads these public properties from `org.kde.KWin.VirtualDesktopManager`:

- `desktops`
- `current`
- `navigationWrappingAround`

It refreshes those properties on a short timer and re-normalizes the result into local QML state. In practice that covers:

- current desktop changes
- desktop count changes
- desktop creation and removal
- desktop data changes such as rename or reorder

The `desktops` property is normalized into an in-memory array of:

```text
{ position, id, name }
```

The indicators are rendered from that normalized list, sorted by position.

## How switching works

Desktop list, active desktop id, and wrapping behavior are refreshed from `org.kde.KWin.VirtualDesktopManager`.

Direct switching writes the public `current` property on `/VirtualDesktopManager` with the target desktop UUID.

In practice, the read side works reliably with the public QML D-Bus helpers, but the write side was not reliable enough in plasmoid context on the test system. The widget therefore uses the public `org.kde.plasma.plasma5support` executable data source as a minimal workaround to invoke `dbus-send` for the write operation while still reading state from the public D-Bus interface directly in QML.

Clicking a dot or wheel switching uses:

```text
org.freedesktop.DBus.Properties.Set(
    "org.kde.KWin.VirtualDesktopManager",
    "current",
    <desktop-id-as-string-variant>
)
```

Mouse wheel behavior is:

- wheel up: previous desktop
- wheel down: next desktop

The wheel handler computes the previous or next UUID from the ordered desktop list, respects KWin's `navigationWrappingAround` property, and applies a short cooldown so one physical wheel notch advances by one desktop even on higher-resolution wheel settings.

## Visual implementation notes

- Dots are still glyph-based, using `Text` as the source item rather than numbered labels or button backgrounds.
- Active and inactive states are expressed by glyph substitution.
- Each desktop gets a fixed-width cell based on font metrics so the row stays visually aligned.
- The effective font size is clamped against the available panel height to reduce clipping on shorter panels.
- Colors default to Plasma theme text colors unless configuration disables that behavior.
- Custom colors are applied through a color overlay on top of the rendered glyph source. That keeps font family, font size, bold active, and custom symbols working while forcing the chosen color reliably.
- The plasmoid refreshes desktop state explicitly on a short timer using public D-Bus property reads. This is a small workaround to keep the widget in sync in applet context without relying on private pager internals.

## Limitations and assumptions

- Plasma 6 and Qt 6 are required.
- The widget assumes a KWin-managed Plasma session because it depends on KWin's virtual desktop manager interface.
- The widget is intended for panel use, not desktop containment use.
- The widget intentionally does not show desktop thumbnails, previews, or names in the main UI.
- Right click is left to standard plasmoid handling by not accepting the right mouse button in the desktop delegates.
- Middle click is intentionally consumed and ignored on the dot delegates.
