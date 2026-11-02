pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Dialogs as QtDialogs
import QtQuick.Layouts

import org.kde.kcmutils as KCM
import org.kde.kirigami as Kirigami
import org.kde.kquickcontrols as KQuickControls
import org.kde.plasma.plasmoid

KCM.SimpleKCM {
    id: configGeneral

    function parseStoredColor(value, fallback) {
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

    property string cfg_inactiveSymbol: Plasmoid.configuration.inactiveSymbol
    property string cfg_activeSymbol: Plasmoid.configuration.activeSymbol
    property string cfg_fontFamily: Plasmoid.configuration.fontFamily
    property int cfg_fontSize: Plasmoid.configuration.fontSize
    property int cfg_spacing: Plasmoid.configuration.spacing
    property bool cfg_useCustomColors: Plasmoid.configuration.useCustomColors
    property color cfg_inactiveColor: parseStoredColor(Plasmoid.configuration.inactiveColor, Kirigami.Theme.textColor)
    property color cfg_activeColor: parseStoredColor(Plasmoid.configuration.activeColor, Kirigami.Theme.textColor)
    property bool cfg_boldActiveSymbol: Plasmoid.configuration.boldActiveSymbol
    property bool cfg_dimInactiveSymbols: Plasmoid.configuration.dimInactiveSymbols
    property bool cfg_enableMouseWheelSwitching: Plasmoid.configuration.enableMouseWheelSwitching

    QtDialogs.FontDialog {
        id: fontDialog
        title: i18n("Select font")
        selectedFont.family: configGeneral.cfg_fontFamily.length > 0
            ? configGeneral.cfg_fontFamily
            : Kirigami.Theme.defaultFont.family

        onAccepted: configGeneral.cfg_fontFamily = selectedFont.family
    }

    Kirigami.FormLayout {
        QQC2.TextField {
            Layout.fillWidth: true
            text: configGeneral.cfg_inactiveSymbol
            placeholderText: "○"

            Kirigami.FormData.label: i18n("Inactive symbol:")

            onTextChanged: configGeneral.cfg_inactiveSymbol = text
        }

        QQC2.TextField {
            Layout.fillWidth: true
            text: configGeneral.cfg_activeSymbol
            placeholderText: "●"

            Kirigami.FormData.label: i18n("Active symbol:")

            onTextChanged: configGeneral.cfg_activeSymbol = text
        }

        RowLayout {
            Layout.fillWidth: true

            Kirigami.FormData.label: i18n("Font family:")

            QQC2.TextField {
                Layout.fillWidth: true
                text: configGeneral.cfg_fontFamily
                placeholderText: i18n("System default")

                onTextChanged: configGeneral.cfg_fontFamily = text
            }

            QQC2.Button {
                text: i18n("Choose")
                onClicked: fontDialog.open()
            }

            QQC2.Button {
                text: i18n("Clear")
                enabled: configGeneral.cfg_fontFamily.length > 0
                onClicked: configGeneral.cfg_fontFamily = ""
            }
        }

        QQC2.SpinBox {
            from: 6
            to: 48
            stepSize: 1
            editable: true
            value: configGeneral.cfg_fontSize

            Kirigami.FormData.label: i18n("Font size:")

            onValueModified: configGeneral.cfg_fontSize = value
            onValueChanged: configGeneral.cfg_fontSize = value
        }

        QQC2.SpinBox {
            from: 0
            to: 48
            stepSize: 1
            editable: true
            value: configGeneral.cfg_spacing

            Kirigami.FormData.label: i18n("Spacing:")

            onValueModified: configGeneral.cfg_spacing = value
            onValueChanged: configGeneral.cfg_spacing = value
        }

        QQC2.CheckBox {
            id: useThemeColorsCheck
            text: i18n("Use theme colors")
            checked: !configGeneral.cfg_useCustomColors
            onToggled: configGeneral.cfg_useCustomColors = !checked
        }

        RowLayout {
            visible: !useThemeColorsCheck.checked
            Layout.fillWidth: true

            Kirigami.FormData.label: i18n("Inactive color:")

            KQuickControls.ColorButton {
                id: inactiveColorButton
                color: configGeneral.cfg_inactiveColor
                dialogTitle: i18n("Select inactive color")
                onColorChanged: configGeneral.cfg_inactiveColor = color
            }

            QQC2.Label {
                Layout.fillWidth: true
                text: configGeneral.cfg_inactiveColor.toString()
                elide: Text.ElideRight
            }
        }

        RowLayout {
            visible: !useThemeColorsCheck.checked
            Layout.fillWidth: true

            Kirigami.FormData.label: i18n("Active color:")

            KQuickControls.ColorButton {
                id: activeColorButton
                color: configGeneral.cfg_activeColor
                dialogTitle: i18n("Select active color")
                onColorChanged: configGeneral.cfg_activeColor = color
            }

            QQC2.Label {
                Layout.fillWidth: true
                text: configGeneral.cfg_activeColor.toString()
                elide: Text.ElideRight
            }
        }

        QQC2.CheckBox {
            text: i18n("Bold active symbol")
            checked: configGeneral.cfg_boldActiveSymbol
            onToggled: configGeneral.cfg_boldActiveSymbol = checked
        }

        QQC2.CheckBox {
            text: i18n("Dim inactive symbols")
            checked: configGeneral.cfg_dimInactiveSymbols
            onToggled: configGeneral.cfg_dimInactiveSymbols = checked
        }

        QQC2.CheckBox {
            text: i18n("Enable mouse wheel switching")
            checked: configGeneral.cfg_enableMouseWheelSwitching
            onToggled: configGeneral.cfg_enableMouseWheelSwitching = checked
        }
    }
}
