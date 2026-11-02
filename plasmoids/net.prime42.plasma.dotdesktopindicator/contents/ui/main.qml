pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects as GraphicalEffects

import org.kde.kirigami as Kirigami
import org.kde.plasma.plasmoid
import org.kde.plasma.plasma5support as Plasma5Support
import org.kde.plasma.workspace.dbus as DBus

PlasmoidItem {
    id: root

    readonly property string kwinService: "org.kde.KWin"
    readonly property string virtualDesktopPath: "/VirtualDesktopManager"
    readonly property string virtualDesktopInterface: "org.kde.KWin.VirtualDesktopManager"

    property var desktopEntries: []
    property string currentDesktopId: ""
    property bool navigationWrappingAround: false
    property bool refreshQueued: false
    property bool wheelSwitchCooldownActive: false

    readonly property string inactiveSymbolText: sanitizedSymbol(Plasmoid.configuration.inactiveSymbol, "○")
    readonly property string activeSymbolText: sanitizedSymbol(Plasmoid.configuration.activeSymbol, "●")
    readonly property string effectiveFontFamily: Plasmoid.configuration.fontFamily.length > 0
        ? Plasmoid.configuration.fontFamily
        : Kirigami.Theme.defaultFont.family
    readonly property string currentDesktopName: desktopNameForId(currentDesktopId)

    Plasmoid.icon: "preferences-desktop-virtual"
    toolTipMainText: Plasmoid.title
    toolTipSubText: currentDesktopName
    preferredRepresentation: compactRepresentation
    compactRepresentation: indicatorRepresentation
    fullRepresentation: indicatorRepresentation

    function sanitizedSymbol(value, fallback) {
        return value && value.length > 0 ? value : fallback;
    }

    function boolFromConfig(value, fallback) {
        if (value === undefined || value === null) {
            return fallback;
        }

        if (typeof value === "string") {
            const lowered = value.toLowerCase();
            if (lowered === "true" || lowered === "1") {
                return true;
            }
            if (lowered === "false" || lowered === "0") {
                return false;
            }
        }

        return Boolean(value);
    }

    function parsedConfiguredColor(value, fallback) {
        if (value === undefined || value === null || value === "") {
            return fallback;
        }

        if (typeof value === "string") {
            const parts = value.split(",");
            if (parts.length === 3 || parts.length === 4) {
                const red = Number(parts[0]) / 255;
                const green = Number(parts[1]) / 255;
                const blue = Number(parts[2]) / 255;
                const alpha = parts.length === 4 ? Number(parts[3]) / 255 : 1;

                if ([red, green, blue, alpha].every(Number.isFinite)) {
                    return Qt.rgba(red, green, blue, alpha);
                }
            }
        }

        return value;
    }

    function useThemeColors() {
        return !boolFromConfig(Plasmoid.configuration.useCustomColors, false);
    }

    function indicatorColor(isCurrent) {
        const baseColor = useThemeColors()
            ? Kirigami.Theme.textColor
            : parsedConfiguredColor(
                isCurrent ? Plasmoid.configuration.activeColor : Plasmoid.configuration.inactiveColor,
                Kirigami.Theme.textColor
            );

        return isCurrent ? baseColor : dimmedColor(baseColor, Plasmoid.configuration.dimInactiveSymbols);
    }

    function dimmedColor(colorValue, enabled) {
        if (!enabled) {
            return colorValue;
        }

        return Qt.rgba(colorValue.r, colorValue.g, colorValue.b, Math.min(colorValue.a, 0.62));
    }

    function toArray(candidate) {
        if (candidate === null || candidate === undefined || typeof candidate === "string") {
            return [];
        }

        if (Array.isArray(candidate)) {
            return candidate;
        }

        if (typeof candidate.length === "number") {
            const values = [];
            for (let index = 0; index < candidate.length; ++index) {
                values.push(candidate[index]);
            }
            return values;
        }

        return [];
    }

    function normalizeDesktopEntry(rawEntry) {
        const tuple = toArray(rawEntry);
        if (tuple.length >= 3) {
            return {
                position: Number(tuple[0]),
                id: String(tuple[1]),
                name: String(tuple[2])
            };
        }

        if (!rawEntry || typeof rawEntry !== "object") {
            return null;
        }

        if ("id" in rawEntry) {
            return {
                position: Number(rawEntry.position ?? rawEntry.number ?? 0),
                id: String(rawEntry.id),
                name: String(rawEntry.name ?? "")
            };
        }

        return null;
    }

    function normalizedDesktops(rawValue) {
        const normalized = [];
        const entries = toArray(rawValue);

        for (let index = 0; index < entries.length; ++index) {
            const entry = normalizeDesktopEntry(entries[index]);
            if (entry && entry.id.length > 0) {
                normalized.push(entry);
            }
        }

        normalized.sort((left, right) => {
            if (left.position !== right.position) {
                return left.position - right.position;
            }

            return left.id.localeCompare(right.id);
        });

        return normalized;
    }

    function syncFromProperties() {
        const propertyMap = desktopProperties.properties;
        desktopEntries = normalizedDesktops(propertyMap ? propertyMap.desktops : []);
        currentDesktopId = propertyMap && propertyMap.current !== undefined ? String(propertyMap.current) : "";
        navigationWrappingAround = propertyMap ? Boolean(propertyMap.navigationWrappingAround) : false;
    }

    function requestRefresh() {
        if (!kwinWatcher.registered || refreshQueued) {
            if (!kwinWatcher.registered) {
                desktopEntries = [];
                currentDesktopId = "";
                navigationWrappingAround = false;
            }
            return;
        }

        refreshQueued = true;
        Qt.callLater(() => {
            refreshQueued = false;
            desktopProperties.updateAll();
        });
    }

    function desktopIndexForId(desktopId) {
        for (let index = 0; index < desktopEntries.length; ++index) {
            if (desktopEntries[index].id === desktopId) {
                return index;
            }
        }

        return -1;
    }

    function desktopNameForId(desktopId) {
        const index = desktopIndexForId(desktopId);
        return index >= 0 ? desktopEntries[index].name : "";
    }

    function setCurrentDesktopById(desktopId) {
        if (!desktopId || !kwinWatcher.registered) {
            return;
        }
        commandRunner.exec("/usr/bin/dbus-send --session --type=method_call --dest=org.kde.KWin /VirtualDesktopManager org.freedesktop.DBus.Properties.Set string:org.kde.KWin.VirtualDesktopManager string:current variant:string:" + desktopId);
    }

    function activateDesktop(desktopId) {
        if (!desktopId || desktopId === currentDesktopId) {
            return;
        }

        setCurrentDesktopById(desktopId);
    }

    function switchRelativeDesktop(delta) {
        if (desktopEntries.length === 0 || !kwinWatcher.registered) {
            return;
        }

        const currentIndex = desktopIndexForId(currentDesktopId);
        if (currentIndex < 0) {
            return;
        }

        let nextIndex = currentIndex + delta;
        if (navigationWrappingAround) {
            if (nextIndex < 0) {
                nextIndex = desktopEntries.length - 1;
            } else if (nextIndex >= desktopEntries.length) {
                nextIndex = 0;
            }
        } else {
            nextIndex = Math.max(0, Math.min(desktopEntries.length - 1, nextIndex));
        }

        if (nextIndex !== currentIndex) {
            setCurrentDesktopById(desktopEntries[nextIndex].id);
        }
    }

    function handleWheelSwitch(deltaY) {
        if (!Plasmoid.configuration.enableMouseWheelSwitching || wheelSwitchCooldownActive || deltaY === 0) {
            return false;
        }

        wheelSwitchCooldownActive = true;
        wheelCooldownTimer.restart();

        if (deltaY > 0) {
            switchRelativeDesktop(-1);
        } else {
            switchRelativeDesktop(1);
        }

        return true;
    }

    DBus.DBusServiceWatcher {
        id: kwinWatcher
        busType: DBus.BusType.Session
        watchedService: root.kwinService

        onRegisteredChanged: root.requestRefresh()
    }

    DBus.Properties {
        id: desktopProperties
        busType: DBus.BusType.Session
        service: root.kwinService
        path: root.virtualDesktopPath
        iface: root.virtualDesktopInterface

        onRefreshed: root.syncFromProperties()
        onPropertiesChanged: root.syncFromProperties()
        onPropertyMapChanged: root.syncFromProperties()
    }

    Plasma5Support.DataSource {
        id: commandRunner
        engine: "executable"
        connectedSources: []

        onNewData: (sourceName, data) => {
            disconnectSource(sourceName);
            root.requestRefresh();
        }

        function exec(command) {
            connectSource(command);
        }
    }

    Component.onCompleted: requestRefresh()

    Timer {
        interval: 150
        repeat: true
        running: kwinWatcher.registered
        onTriggered: root.requestRefresh()
    }

    Timer {
        id: wheelCooldownTimer
        interval: 140
        repeat: false
        onTriggered: root.wheelSwitchCooldownActive = false
    }

    Component {
        id: indicatorRepresentation

        Item {
            id: representation

            readonly property real horizontalPadding: Kirigami.Units.smallSpacing
            readonly property real verticalPadding: 1
            readonly property int fontPixelSize: Math.max(
                6,
                Math.min(
                    Plasmoid.configuration.fontSize,
                    Math.floor(Math.max(8, height - (verticalPadding * 2)) * 0.82)
                )
            )
            readonly property font inactiveFont: Qt.font({
                family: root.effectiveFontFamily,
                pixelSize: fontPixelSize,
                bold: false
            })
            readonly property font activeFont: Qt.font({
                family: root.effectiveFontFamily,
                pixelSize: fontPixelSize,
                bold: Plasmoid.configuration.boldActiveSymbol
            })
            readonly property real cellWidth: Math.ceil(Math.max(
                inactiveMetrics.width,
                inactiveMetrics.advanceWidth,
                activeMetrics.width,
                activeMetrics.advanceWidth
            )) + 2
            readonly property real cellHeight: Math.ceil(Math.max(inactiveMetrics.height, activeMetrics.height)) + 2

            implicitWidth: indicatorRow.implicitWidth + (horizontalPadding * 2)
            implicitHeight: Math.max(indicatorRow.implicitHeight + (verticalPadding * 2), cellHeight + 2)
            Layout.minimumWidth: implicitWidth
            Layout.minimumHeight: implicitHeight
            Layout.preferredWidth: implicitWidth
            Layout.preferredHeight: implicitHeight

            TextMetrics {
                id: inactiveMetrics
                font: representation.inactiveFont
                text: root.inactiveSymbolText
            }

            TextMetrics {
                id: activeMetrics
                font: representation.activeFont
                text: root.activeSymbolText
            }

            Grid {
                id: indicatorRow
                anchors.centerIn: parent
                spacing: Math.max(0, Plasmoid.configuration.spacing)
                columns: Plasmoid.formFactor === 3 ? 1 : Math.max(1, root.desktopEntries.length)

                Repeater {
                    model: root.desktopEntries

                    delegate: Item {
                        required property var modelData

                        readonly property bool isCurrent: modelData.id === root.currentDesktopId

                        width: representation.cellWidth
                        height: representation.cellHeight

                        Text {
                            id: glyphSource
                            anchors.centerIn: parent
                            anchors.verticalCenterOffset: -Math.round(representation.fontPixelSize * 0.04)
                            text: parent.isCurrent ? root.activeSymbolText : root.inactiveSymbolText
                            color: "white"
                            font.family: root.effectiveFontFamily
                            font.pixelSize: representation.fontPixelSize + (parent.isCurrent && Plasmoid.configuration.boldActiveSymbol ? 1 : 0)
                            font.bold: parent.isCurrent && Plasmoid.configuration.boldActiveSymbol
                            font.weight: parent.isCurrent && Plasmoid.configuration.boldActiveSymbol ? Font.Black : Font.Normal
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            scale: 1
                            renderType: Text.QtRendering
                            visible: false
                        }

                        GraphicalEffects.ColorOverlay {
                            x: glyphSource.x
                            y: glyphSource.y
                            width: glyphSource.width
                            height: glyphSource.height
                            source: glyphSource
                            color: root.indicatorColor(parent.isCurrent)
                            cached: true
                        }

                        MouseArea {
                            anchors.fill: parent
                            acceptedButtons: Qt.LeftButton | Qt.MiddleButton
                            cursorShape: Qt.PointingHandCursor

                            onClicked: mouse => {
                                if (mouse.button === Qt.LeftButton) {
                                    root.activateDesktop(parent.modelData.id);
                                }
                                mouse.accepted = true;
                            }

                            onWheel: wheel => {
                                wheel.accepted = root.handleWheelSwitch(wheel.angleDelta.y);
                            }
                        }
                    }
                }
            }
        }
    }
}
