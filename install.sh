#!/usr/bin/env bash
# Install GenoTheme into the current user's KDE Plasma 6 profile (no sudo needed).
# Installs only; apply with:  ./install.sh --apply   (does NOT apply the global theme / panel layout)
set -euo pipefail
cd "$(dirname "$0")"
T=themes; D=${XDG_DATA_HOME:-$HOME/.local/share}; C=${XDG_CONFIG_HOME:-$HOME/.config}
mkdir -p "$D"/{color-schemes,plasma/desktoptheme,plasma/look-and-feel,aurorae/themes,icons,konsole,themes,wallpapers} "$C/Kvantum"
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
gtk-update-icon-cache -q -f -t "$D/icons/GenoTheme-Icons" 2>/dev/null || true
echo "GenoTheme installed."

if [[ "${1:-}" == "--apply" ]]; then
  plasma-apply-colorscheme GenoTheme
  plasma-apply-desktoptheme GenoTheme
  kvantummanager --set GenoTheme
  /usr/libexec/plasma-changeicons GenoTheme-Icons 2>/dev/null || kwriteconfig6 --file kdeglobals --group Icons --key Theme GenoTheme-Icons
  kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
  kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__GenoTheme
  qdbus-qt6 org.kde.KWin /KWin reconfigure
  kwriteconfig6 --file konsolerc --group "Desktop Entry" --key DefaultProfile GenoTheme.profile
  echo "GenoTheme applied (global theme / layout untouched)."
fi
