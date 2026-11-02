// GenoTheme panel layout (Balthasar: bottom status bar + left dock on the primary
// screen, a floating mini panel on other landscape screens, nothing on portrait
// screens). install.sh stamps GENOTHEME_PLAN for this machine. Without that
// plan, a conservative built-in layout is used.

function genothemeLog(message) {
    if (typeof print === "function") {
        print(message);
    }
}

function genothemeResolveScreen(spec) {
    if (!spec) {
        return 0;
    }
    if (typeof screenCount === "number" && typeof screenGeometry === "function") {
        var i;
        for (i = 0; i < screenCount; i++) {
            var geo = screenGeometry(i);
            if (!geo) {
                continue;
            }
            if (Math.round(geo.width) === spec.width && Math.round(geo.height) === spec.height &&
                Math.round(geo.x) === spec.x && Math.round(geo.y) === spec.y) {
                return i;
            }
        }
        if (screenCount === 1 && spec.primary) {
            return 0;
        }
        if (screenCount === 1 && !spec.primary) {
            return -1;
        }
    }
    return typeof spec.index === "number" ? spec.index : 0;
}

function genothemeApplyConfig(widget, config) {
    if (!widget || !config) {
        return;
    }
    var groups = Object.keys(config);
    var g;
    for (g = 0; g < groups.length; g++) {
        var group = groups[g];
        var entries = config[group];
        if (group === "_root" || group === "") {
            widget.currentConfigGroup = [];
        } else {
            widget.currentConfigGroup = group.split("/");
        }
        var keys = Object.keys(entries);
        var k;
        for (k = 0; k < keys.length; k++) {
            widget.writeConfig(keys[k], entries[keys[k]]);
        }
    }
}

function genothemeRemovePanels() {
    if (typeof panelIds === "undefined" || !panelIds || !panelIds.forEach) {
        return;
    }
    var ids = [];
    panelIds.forEach(function (id) { ids.push(id); });
    var i;
    for (i = 0; i < ids.length; i++) {
        var panel = panelById(ids[i]);
        if (panel) {
            panel.remove();
        }
    }
}

function genothemeApplyWallpaper(image, fillMode) {
    var list = [];
    if (typeof desktops === "function") {
        desktops().forEach(function (desktop) { list.push(desktop); });
    }
    if (typeof screenCount === "number" && typeof desktopForScreen === "function") {
        var i;
        for (i = 0; i < screenCount; i++) {
            var desktop = desktopForScreen(i);
            if (desktop) {
                list.push(desktop);
            }
        }
    }
    var seen = {};
    var j;
    for (j = 0; j < list.length; j++) {
        var desktop = list[j];
        var id = desktop.id;
        if (id !== undefined && seen[id]) {
            continue;
        }
        if (id !== undefined) {
            seen[id] = true;
        }
        desktop.wallpaperPlugin = "org.kde.image";
        desktop.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
        desktop.writeConfig("Image", image);
        desktop.writeConfig("FillMode", fillMode);
    }
}

function genothemeApplyPlan(plan) {
    genothemeRemovePanels();
    var image = plan.wallpaper || "GenoTheme";
    var fillMode = plan.fillMode === undefined ? 2 : plan.fillMode;
    genothemeApplyWallpaper(image, fillMode);
    var panels = plan.panels || [];
    var p;
    for (p = 0; p < panels.length; p++) {
        var spec = panels[p];
        var screen = genothemeResolveScreen(spec.screen);
        if (screen < 0) {
            continue;
        }
        var panel = new Panel();
        panel.location = spec.location;
        panel.screen = screen;
        panel.height = spec.height;
        panel.hiding = spec.hiding || "none";
        panel.floating = !!spec.floating;
        if (spec.opacity) {
            panel.opacity = spec.opacity;
        }
        if (spec.lengthMode) {
            panel.lengthMode = spec.lengthMode;
        }
        if (spec.alignment) {
            panel.alignment = spec.alignment;
        }
        if (spec.floatingApplets) {
            try {
                panel.floatingApplets = true;
            } catch (error) {
                genothemeLog("GenoTheme: floatingApplets is not available on this Plasma");
            }
        }
        var widgets = spec.widgets || [];
        var w;
        for (w = 0; w < widgets.length; w++) {
            var created = panel.addWidget(widgets[w].plugin);
            if (!created) {
                genothemeLog("GenoTheme: could not add " + widgets[w].plugin);
                continue;
            }
            genothemeApplyConfig(created, widgets[w].config);
        }
    }
    genothemeLog("GenoTheme layout applied (" + panels.length + " panels)");
}

function genothemeBuiltinPlan() {
    var launchers = "preferred://filemanager,preferred://browser,applications:org.kde.konsole.desktop,applications:org.kde.kate.desktop,applications:systemsettings.desktop";
    return {
        wallpaper: "GenoTheme",
        fillMode: 2,
        panels: [
            {
                role: "primary-status",
                screen: { index: 0, x: 0, y: 0, width: 0, height: 0, primary: true },
                location: "bottom",
                height: 34,
                lengthMode: "fill",
                alignment: "center",
                floating: false,
                opacity: "translucent",
                hiding: "none",
                widgets: [
                    { plugin: "org.kde.plasma.kickoff", config: { General: { icon: "genotheme-logo" } } },
                    { plugin: "org.kde.plasma.digitalclock", config: { Appearance: { dateFormat: "isoDate", dateDisplayFormat: "BesideTime", showSeconds: "0", use24hFormat: "2" } } }
                ]
            },
            {
                role: "primary-dock",
                screen: { index: 0, x: 0, y: 0, width: 0, height: 0, primary: true },
                location: "left",
                height: 46,
                lengthMode: "fit",
                alignment: "left",
                floating: false,
                floatingApplets: true,
                opacity: "translucent",
                hiding: "none",
                widgets: [
                    { plugin: "org.kde.plasma.kickoff", config: { General: { icon: "genotheme-logo", favoritesPortedToKAstats: "true" } } },
                    { plugin: "org.kde.plasma.icontasks", config: { General: { launchers: launchers, fill: "false", iconSpacing: "0" } } },
                    { plugin: "org.kde.plasma.pager", config: { General: { displayedText: "Number", showOnlyCurrentScreen: "false" } } }
                ]
            }
        ]
    };
}

function genothemeRun() {
    var plan = (typeof GENOTHEME_PLAN !== "undefined" && GENOTHEME_PLAN) ? GENOTHEME_PLAN : genothemeBuiltinPlan();
    genothemeApplyPlan(plan);
}

if (typeof GENOTHEME_TEST === "undefined" && typeof Panel === "function") {
    genothemeRun();
}

if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        genothemeApplyPlan: genothemeApplyPlan,
        genothemeBuiltinPlan: genothemeBuiltinPlan,
        genothemeResolveScreen: genothemeResolveScreen
    };
}
