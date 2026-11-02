#!/usr/bin/env node
"use strict";

const path = require("path");
const layout = require(path.join(
  __dirname,
  "../themes/look-and-feel/com.genocorp.genotheme/contents/layouts/org.kde.plasma.desktop-layout.js"
));

const created = [];

function Widget(plugin) {
  this.plugin = plugin;
  this.currentConfigGroup = [];
  this.entries = [];
  this.writeConfig = (key, value) => {
    this.entries.push(this.currentConfigGroup.join("/") + ":" + key + "=" + value);
  };
}

global.Panel = function Panel() {
  this.location = "";
  this.screen = -1;
  this.height = 0;
  this.hiding = "";
  this.floating = false;
  this.opacity = "";
  this.lengthMode = "";
  this.alignment = "";
  this.floatingApplets = false;
  this.widgets = [];
  this.addWidget = (plugin) => {
    const widget = new Widget(plugin);
    this.widgets.push(widget);
    return widget;
  };
  created.push(this);
};

global.panelIds = [];
global.panelById = () => null;
global.desktops = () => [];
global.screenCount = 2;
global.screenGeometry = (index) => {
  if (index === 0) return { x: 0, y: 0, width: 800, height: 1280 };
  return { x: 10, y: 20, width: 2560, height: 1440 };
};
const wallpapers = [];
global.desktopForScreen = (index) => ({
  id: index,
  writeConfig(key, value) {
    wallpapers.push(index + ":" + key + "=" + value);
  },
});

const plan = {
  wallpaper: "file:///tmp/genotheme.png",
  fillMode: 2,
  panels: [
    {
      role: "primary-status",
      screen: { index: 0, x: 10, y: 20, width: 2560, height: 1440, primary: true },
      location: "bottom",
      height: 34,
      lengthMode: "fill",
      alignment: "center",
      floating: false,
      opacity: "translucent",
      hiding: "none",
      widgets: [
        { plugin: "org.kde.plasma.systemtray", config: { General: { extraItems: "org.kde.plasma.volume" } } },
        {
          plugin: "org.kde.plasma.systemmonitor.cpu",
          config: {
            _root: { CurrentPreset: "org.kde.plasma.systemmonitor" },
            Appearance: { title: "CPU", chartFace: "org.kde.ksysguard.piechart" },
            SensorColors: { "cpu/all/usage": "77,107,255" },
          },
        },
      ],
    },
    {
      role: "portrait-should-skip",
      screen: { index: 9, x: 1, y: 1, width: 10, height: 20, primary: false },
      location: "bottom",
      height: 46,
      lengthMode: "fit",
      alignment: "left",
      floating: true,
      opacity: "translucent",
      widgets: [{ plugin: "org.kde.plasma.pager", config: {} }],
    },
  ],
};

// Only one Plasma screen matches the non-primary spec's geometry, so it must be skipped.
global.screenCount = 1;
layout.genothemeApplyPlan(plan);
if (created.length !== 1) {
  throw new Error("expected 1 panel, got " + created.length);
}
const panel = created[0];
if (panel.location !== "bottom" || panel.height !== 34 || panel.opacity !== "translucent") {
  throw new Error("primary panel properties were not applied: " + JSON.stringify(panel));
}
if (panel.screen !== 0) {
  throw new Error("single primary screen should resolve to 0, got " + panel.screen);
}
if (panel.widgets.map((w) => w.plugin).join(",") !== "org.kde.plasma.systemtray,org.kde.plasma.systemmonitor.cpu") {
  throw new Error("widget order mismatch");
}
const cpu = panel.widgets[1];
const joined = cpu.entries.join("\n");
if (!joined.includes("Appearance:title=CPU")) throw new Error(joined);
if (!joined.includes("SensorColors:cpu/all/usage=77,107,255")) throw new Error(joined);
if (!joined.includes(":CurrentPreset=org.kde.plasma.systemmonitor")) throw new Error(joined);
if (!wallpapers.some((line) => line.includes("Image=file:///tmp/genotheme.png"))) {
  throw new Error("wallpaper was not written: " + wallpapers.join("|"));
}
if (!wallpapers.some((line) => line.includes("FillMode=2"))) {
  throw new Error("fill mode missing");
}

global.screenCount = 2;
const resolved = layout.genothemeResolveScreen({ index: 5, x: 10, y: 20, width: 2560, height: 1440, primary: true });
if (resolved !== 1) throw new Error("geometry should win over index, got " + resolved);

console.log("ok layout.js");
