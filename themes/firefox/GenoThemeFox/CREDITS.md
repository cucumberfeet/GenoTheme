# GenoThemeFox

GenoThemeFox is a recolour of the **Daemon 2.0** Firefox theme (add-on id
`{28127a6f-9a96-4256-b4d9-87b54b7ffc1c}`, theme name `Daemon2.0`). The original
theme only sets `manifest.json` colours. Those colours are mapped with the same
Daemon → GenoCorp table as `tools/recolor.py`:

| Daemon | GenoTheme | Role in the theme |
|---|---|---|
| `rgb(51, 19, 25)` `#331319` | `#080a24` | frame, toolbar, popup |
| `rgb(33, 14, 21)` `#210e15` | `#020205` | toolbar field |
| `rgb(93, 244, 254)` `#5df4fe` | `#d9def5` | toolbar, tab, field, popup text and icons (lightened; `#4d6bff` was too dim on `#080a24`) |
| `rgb(251, 48, 72)` `#fb3048` | `#ff0000` | tab line and tab loading |
| accent (not in the original theme) | `#4d6bff` | field border, menu border, selection |

The original add-on is signed. Release Firefox (including stock Fedora Firefox)
refuses unsigned add-ons, and `xpinstall.signatures.required` is ignored on
release builds, so GenoTheme does **not** install this manifest as an extension.
`install.sh --apply` writes those colours into the default profile as
`chrome/userChrome.css` and `chrome/userContent.css`, and sets
`toolkit.legacyUserProfileCustomizations.stylesheets` in `user.js`.

The stylesheet paints the toolbox, tabs, URL bar and icons directly. Firefox
only applies `--lwt-*` variables when a lightweight theme is active, so the
System theme (`default-theme@mozilla.org`) and the built-in Dark theme ignore
a variable-only sheet. The Dark theme is still selected in `extensions.json`
when that file lists `firefox-compact-dark@mozilla.org`, and the Daemon 2.0
add-on `{28127a6f-9a96-4256-b4d9-87b54b7ffc1c}` is marked disabled, so it is
not the active theme. The `!important` rules also cover it if it stays
enabled until the next `--apply` after Firefox has quit.

GenoThemeFox is distributed under the same **GPL-3.0-or-later** as the rest of
GenoTheme. The Daemon 2.0 theme is by Mathis Paquet (MathisP75).
