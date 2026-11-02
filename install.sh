#!/usr/bin/env bash
# Install GenoTheme into the current user's KDE Plasma 6 profile (no sudo).
#
#   ./install.sh                 copy files only; does not change the running desktop
#   ./install.sh --apply         copy files and apply colours, style, icons, fonts,
#                                KWin, wallpaper, lock screen, Firefox and the panel layout
#   ./install.sh --layout        copy files and apply only the panel layout and desktop wallpaper
#   ./install.sh --restore-panels
#                                put back the panel config saved before the first --apply/--layout
#
# The panel layout is never written unless --apply, --layout or --restore-panels is passed.
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$(pwd)
T=themes
D=${XDG_DATA_HOME:-$HOME/.local/share}
C=${XDG_CONFIG_HOME:-$HOME/.config}
WALL="$D/wallpapers/GenoTheme/contents/images/3840x2160.png"
LAYOUT_JS="$D/plasma/look-and-feel/com.genocorp.genotheme/contents/layouts/org.kde.plasma.desktop-layout.js"
LAYOUT_TEMPLATE="$T/look-and-feel/com.genocorp.genotheme/contents/layouts/org.kde.plasma.desktop-layout.js"

APPLY=0
LAYOUT=0
RESTORE=0
for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    --layout) LAYOUT=1 ;;
    --restore-panels) RESTORE=1 ;;
    -h|--help)
      sed -n '2,12p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      echo "Try ./install.sh --help" >&2
      exit 2
      ;;
  esac
done

warn() { printf 'warning: %s\n' "$*" >&2; }

kconf() {
  # kconf <file> <group> [<group>...] -- <key> <value>
  local file=$1
  shift
  local -a groups=()
  while [[ $# -gt 0 && $1 != "--" ]]; do
    groups+=("$1")
    shift
  done
  [[ ${1:-} == "--" ]] && shift
  local key=$1 value=$2
  if command -v kwriteconfig6 >/dev/null 2>&1; then
    local -a cmd=(kwriteconfig6 --file "$file")
    local g
    for g in "${groups[@]}"; do cmd+=(--group "$g"); done
    cmd+=(--key "$key" "$value")
    "${cmd[@]}"
  else
    local -a py=(python3 "$ROOT/tools/kdeconfig.py" --config-home "$C" --file "$file")
    local g
    for g in "${groups[@]}"; do py+=(--group "$g"); done
    py+=(--key "$key" "$value")
    "${py[@]}"
  fi
}

install_files() {
  mkdir -p "$D"/{color-schemes,plasma/desktoptheme,plasma/look-and-feel,plasma/plasmoids,aurorae/themes,icons,konsole,themes,wallpapers} \
    "$C/Kvantum" "$HOME/.local/share/fonts/genotheme"
  cp    $T/color-schemes/GenoTheme.colors              "$D/color-schemes/"
  rm -rf "$D/plasma/desktoptheme/GenoTheme" "$D/aurorae/themes/GenoTheme" "$C/Kvantum/GenoTheme" \
      "$D/icons/GenoTheme-Icons" "$D/themes/GenoTheme-GTK" "$D/plasma/look-and-feel/com.genocorp.genotheme" "$D/wallpapers/GenoTheme"
  cp -r $T/plasma/desktoptheme/GenoTheme               "$D/plasma/desktoptheme/"
  cp -r $T/aurorae/themes/GenoTheme                    "$D/aurorae/themes/"
  cp -r $T/kvantum/GenoTheme                           "$C/Kvantum/"
  cp -a $T/icons/GenoTheme-Icons                       "$D/icons/"
  cp -r $T/gtk/GenoTheme-GTK                           "$D/themes/"
  cp    $T/konsole/GenoTheme.colorscheme $T/konsole/GenoTheme.profile "$D/konsole/"
  cp -r $T/look-and-feel/com.genocorp.genotheme        "$D/plasma/look-and-feel/"
  cp -r wallpaper-package/GenoTheme                    "$D/wallpapers/"
  local id
  for id in "$ROOT"/plasmoids/*; do
    [[ -d $id ]] || continue
    rm -rf "$D/plasma/plasmoids/$(basename "$id")"
    cp -a "$id" "$D/plasma/plasmoids/"
  done
  rm -rf "$HOME/.local/share/fonts/genotheme"
  mkdir -p "$HOME/.local/share/fonts/genotheme"
  cp -a "$ROOT/fonts/." "$HOME/.local/share/fonts/genotheme/"
  if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -f -t "$D/icons/GenoTheme-Icons" 2>/dev/null || true
  fi
  if command -v fc-cache >/dev/null 2>&1; then
    fc-cache -f "$HOME/.local/share/fonts/genotheme" >/dev/null 2>&1 || true
  fi
  echo "GenoTheme installed."
}

PLASMA_WAS_RUNNING=0
stop_plasmashell() {
  if ! pgrep -x plasmashell >/dev/null 2>&1; then
    return 0
  fi
  PLASMA_WAS_RUNNING=1
  if command -v kquitapp6 >/dev/null 2>&1; then
    kquitapp6 plasmashell >/dev/null 2>&1 || true
  fi
  local i
  for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 20; do
    pgrep -x plasmashell >/dev/null 2>&1 || return 0
    sleep 0.2
  done
  killall plasmashell >/dev/null 2>&1 || true
  sleep 0.3
}

start_plasmashell() {
  if [[ $PLASMA_WAS_RUNNING != 1 ]]; then
    return 0
  fi
  if ! command -v plasmashell >/dev/null 2>&1; then
    warn "plasmashell was running but is not on PATH, so it was not restarted."
    return 0
  fi
  if ! pgrep -x plasmashell >/dev/null 2>&1; then
    nohup plasmashell >/dev/null 2>&1 &
    disown || true
  fi
}

refresh_icons() {
  local cache=${XDG_CACHE_HOME:-$HOME/.cache}
  rm -f "$cache/icon-cache.kcache" "$HOME/.cache/icon-cache.kcache" 2>/dev/null || true
  if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -f -t "$D/icons/GenoTheme-Icons" 2>/dev/null || true
  fi
  if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
  fi
}

kvantum_missing() {
  if command -v kvantummanager >/dev/null 2>&1; then
    return 1
  fi
  local so
  for so in \
    /usr/lib64/qt6/plugins/styles/kvantum.so \
    /usr/lib64/qt6/plugins/styles/libkvantum.so \
    /usr/lib/qt6/plugins/styles/kvantum.so \
    /usr/lib/x86_64-linux-gnu/qt6/plugins/styles/kvantum.so
  do
    [[ -e $so ]] && return 1
  done
  return 0
}

apply_appearance() {
  if command -v plasma-apply-colorscheme >/dev/null 2>&1; then
    plasma-apply-colorscheme GenoTheme || warn "plasma-apply-colorscheme failed"
  fi
  kconf kdeglobals General -- ColorScheme GenoTheme
  kconf kdeglobals Icons -- Theme GenoTheme-Icons
  # The Kvantum bug: kvantummanager --set does not write this key.
  kconf kdeglobals KDE -- widgetStyle kvantum
  if kvantum_missing; then
    warn "Kvantum is not installed. widgetStyle=kvantum was written, but Qt apps will keep their current style until the package is installed (Fedora: sudo dnf install kvantum)."
  elif command -v kvantummanager >/dev/null 2>&1; then
    kvantummanager --set GenoTheme || warn "kvantummanager --set GenoTheme failed"
  fi
  if command -v plasma-apply-desktoptheme >/dev/null 2>&1; then
    plasma-apply-desktoptheme GenoTheme || warn "plasma-apply-desktoptheme failed"
  fi
  kconf plasmarc Theme -- name GenoTheme
  if [[ -x /usr/libexec/plasma-changeicons ]]; then
    /usr/libexec/plasma-changeicons GenoTheme-Icons || true
  elif command -v plasma-changeicons >/dev/null 2>&1; then
    plasma-changeicons GenoTheme-Icons || true
  fi

  kconf kdeglobals General -- font "Rajdhani,10,-1,5,500,0,0,0,0,0,0,0,0,0,0,1,Medium"
  kconf kdeglobals General -- menuFont "Rajdhani,10,-1,5,500,0,0,0,0,0,0,0,0,0,0,1,Medium"
  kconf kdeglobals General -- toolBarFont "Rajdhani,10,-1,5,500,0,0,0,0,0,0,0,0,0,0,1,Medium"
  kconf kdeglobals General -- smallestReadableFont "Rajdhani,8,-1,5,500,0,0,0,0,0,0,0,0,0,0,1,Medium"
  kconf kdeglobals General -- fixed "Hack,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
  kconf kdeglobals WM -- activeFont "Orbitron,8,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
  kconf kdeglobals KDE -- AnimationDurationFactor 0.7

  kconf kwinrc org.kde.kdecoration2 -- library org.kde.kwin.aurorae
  kconf kwinrc org.kde.kdecoration2 -- theme __aurorae__svg__GenoTheme
  kconf kwinrc org.kde.kdecoration2 -- BorderSize None
  kconf kwinrc org.kde.kdecoration2 -- BorderSizeAuto false
  kconf kwinrc org.kde.kdecoration2 -- ButtonsOnLeft ""
  kconf kwinrc org.kde.kdecoration2 -- ButtonsOnRight IAX
  # Plasma 6 also reads kdecoration3. Set the border only; do not switch the
  # theme to Klassy (that decoration is not part of GenoTheme).
  kconf kwinrc org.kde.kdecoration3 -- BorderSize None
  kconf kwinrc org.kde.kdecoration3 -- BorderSizeAuto false
  kconf kwinrc Effect-blur -- BlurStrength 7
  kconf kwinrc Effect-blur -- NoiseStrength 3
  kconf kwinrc Effect-translucency -- Dialogs 100
  kconf kwinrc Effect-translucency -- Inactive 100
  kconf kwinrc Effect-translucency -- MoveResize 90
  kconf kwinrc Plugins -- blurEnabled true
  kconf kwinrc Plugins -- contrastEnabled true
  kconf kwinrc Plugins -- fadingpopupsEnabled true
  kconf kwinrc Plugins -- magiclampEnabled true
  kconf kwinrc Plugins -- scaleEnabled true
  kconf kwinrc Plugins -- slideEnabled true
  kconf kwinrc Plugins -- translucencyEnabled true
  kconf kwinrc Plugins -- wobblywindowsEnabled false
  kconf kwinrc Plugins -- kwin4_effect_squashEnabled false
  kconf kwinrc TabBox -- LayoutName flip
  kconf kwinrc TabBox -- HighlightWindows false
  kconf kwinrc TabBox -- ShowScreenMode 1
  if command -v qdbus-qt6 >/dev/null 2>&1; then
    qdbus-qt6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
  fi
  echo "Skipped third-party KWin effects that are not shipped: kwin4_effect_shapecorners (rounded corners, size 10 on Balthasar) and kwin6_effect_tv_glitch (location unknown). The Bibata-Original-Classic cursor is not part of GenoTheme."

  kconf konsolerc "Desktop Entry" -- DefaultProfile GenoTheme.profile
  local wall_url
  wall_url=$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve().as_uri())' "$WALL")
  kconf kscreenlockerrc Greeter -- WallpaperPlugin org.kde.image
  kconf kscreenlockerrc Greeter Wallpaper org.kde.image General -- Image "$wall_url"
  kconf kscreenlockerrc Greeter Wallpaper org.kde.image General -- FillMode 2
}

apply_layout() {
  local -a cmd=(
    python3 "$ROOT/tools/apply_layout.py" apply
    --config-home "$C"
    --data-home "$D"
    --wallpaper "$WALL"
    --stamp-layout "$LAYOUT_JS"
    --layout-template "$LAYOUT_TEMPLATE"
  )
  if [[ $APPLY == 1 ]]; then
    cmd+=(--lock-screen)
  fi
  "${cmd[@]}"
}

install_files

if [[ $RESTORE == 1 ]]; then
  if [[ $APPLY == 1 || $LAYOUT == 1 ]]; then
    echo "--restore-panels replaces the panel config and does not also apply." >&2
  fi
  stop_plasmashell
  python3 "$ROOT/tools/apply_layout.py" restore --config-home "$C" --data-home "$D"
  start_plasmashell
  echo "Panel config restored. Colours, fonts, KWin and Firefox were left as they are."
  exit 0
fi

if [[ $APPLY == 1 || $LAYOUT == 1 ]]; then
  stop_plasmashell
  apply_layout
fi

if [[ $APPLY == 1 ]]; then
  apply_appearance
  python3 "$ROOT/tools/firefox_theme.py" apply --home "$HOME" --theme "$ROOT/themes/firefox/GenoThemeFox"
  refresh_icons
  echo "GenoTheme applied, including the panel layout, wallpaper, fonts, KWin and GenoThemeFox."
  echo "Restart already-open Qt apps to pick up Kvantum. Restart Firefox completely to pick up GenoThemeFox."
fi

reapply_layout_live() {
  # The on-disk lastScreen index follows kscreen-doctor priority order.
  # When Plasma is actually running, ask it to rebuild the panels so geometry
  # (not the priority index) picks the screen.
  [[ $PLASMA_WAS_RUNNING == 1 ]] || return 0
  local qdbus=""
  if command -v qdbus-qt6 >/dev/null 2>&1; then qdbus=qdbus-qt6
  elif command -v qdbus6 >/dev/null 2>&1; then qdbus=qdbus6
  elif command -v qdbus >/dev/null 2>&1; then qdbus=qdbus
  else
    warn "qdbus is not available, so Plasma will use the on-disk screen indexes (kscreen priority order)."
    return 0
  fi
  local i script
  script=$(cat "$LAYOUT_JS")
  for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
    if "$qdbus" org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$script" >/dev/null 2>&1; then
      echo "Reloaded the panel layout in the running Plasma session."
      return 0
    fi
    sleep 0.4
  done
  warn "plasmashell did not accept the layout script. The on-disk layout is still in place."
}

if [[ $APPLY == 1 || $LAYOUT == 1 ]]; then
  start_plasmashell
  reapply_layout_live
fi

if [[ $APPLY == 0 && $LAYOUT == 0 ]]; then
  echo "Files only. The running desktop, panel layout and Firefox profile were not changed."
  echo "Apply with: ./install.sh --apply"
fi
