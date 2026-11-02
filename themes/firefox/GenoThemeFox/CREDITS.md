# GenoThemeFox

GenoThemeFox is a recolour of the **Daemon 2.0** Firefox theme (add-on id
`{28127a6f-9a96-4256-b4d9-87b54b7ffc1c}`, theme name `Daemon2.0`). The original
theme only sets `manifest.json` colours. Those colours are mapped with the same
Daemon → GenoCorp table as `tools/recolor.py`:

| Daemon | GenoTheme | Role in the theme |
|---|---|---|
| `rgb(51, 19, 25)` `#331319` | `#080a24` | frame, toolbar, popup |
| `rgb(33, 14, 21)` `#210e15` | `#020205` | toolbar field |
| `rgb(93, 244, 254)` `#5df4fe` | `#4d6bff` | toolbar, tab, field and popup text |
| `rgb(251, 48, 72)` `#fb3048` | `#ff0000` | tab line and tab loading |

The original add-on is signed. Release Firefox (including stock Fedora Firefox)
refuses unsigned add-ons, and `xpinstall.signatures.required` is ignored on
release builds, so GenoTheme does **not** install this manifest as an extension.
`install.sh --apply` writes the same colours into the default profile as
`chrome/userChrome.css` and `chrome/userContent.css`, and sets
`toolkit.legacyUserProfileCustomizations.stylesheets` in `user.js`. That path
works without a signature and is re-applied every time Firefox starts.

GenoThemeFox is distributed under the same **GPL-3.0-or-later** as the rest of
GenoTheme. The Daemon 2.0 theme is by Mathis Paquet (MathisP75).
