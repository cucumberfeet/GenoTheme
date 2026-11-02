# Test Checklist

## Install and load

- Install the plasmoid with `kpackagetool6 -t Plasma/Applet -i .`
- Restart Plasma Shell
- Confirm `Dot Desktop Indicator` appears in the widget picker
- Add it to a panel
- Remove it from the panel and add it again

## Desktop state updates

- Confirm one dot is shown for each current virtual desktop
- Change the active desktop with a keyboard shortcut and confirm the solid dot moves immediately
- Add a virtual desktop in Plasma settings and confirm a new dot appears immediately
- Remove a virtual desktop and confirm the dot count decreases immediately
- Rename or reorder desktops in Plasma settings and confirm the widget keeps following KWin's desktop order without stale state

## Interaction

- Click each dot and confirm it switches to that desktop
- Middle click a dot and confirm nothing happens
- Right click the widget and confirm the normal plasmoid context menu still appears
- Scroll wheel up over the widget and confirm it switches to the previous desktop when wheel switching is enabled
- Scroll wheel down over the widget and confirm it switches to the next desktop when wheel switching is enabled
- Disable wheel switching in the widget settings and confirm the wheel no longer switches desktops

## Configuration

- Change the inactive symbol and confirm all inactive desktops update
- Change the active symbol and confirm the active desktop updates
- Change the font family override and confirm the dots use it
- Clear the font family override and confirm the widget goes back to the default font
- Change the font size and confirm the dots resize without clipping at common panel heights
- Change spacing and confirm the gaps between dots update
- Disable theme colors and confirm the inactive and active color pickers control the dots
- Reopen the settings dialog after disabling theme colors and confirm the toggle state persists
- Enable `Bold active symbol` and confirm only the active dot changes weight
- Enable `Dim inactive symbols` and confirm inactive dots become visually quieter

## Panel sizes

- Test the widget on a short panel height
- Test the widget on a medium panel height
- Test the widget on a taller panel height
- Confirm the dots remain visually centered and do not look vertically offset
