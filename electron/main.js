
const { app, BrowserWindow, ipcMain, screen } = require("electron");
const path = require("path");

let win;

const ORB_SIZE = 88;
const PANEL_WIDTH = 420;
const PANEL_HEIGHT = 320;
const EDGE_MARGIN = 24;

function createWindow() {
  const area = screen.getPrimaryDisplay().workArea;

  win = new BrowserWindow({
    x: area.x + area.width - ORB_SIZE - EDGE_MARGIN,
    y: area.y + area.height - ORB_SIZE - EDGE_MARGIN,
    width: ORB_SIZE,
    height: ORB_SIZE,
    frame: false,
    transparent: true,
    backgroundColor: "#00000000",
    alwaysOnTop: true,
    resizable: false,
    movable: false,
    skipTaskbar: true,
    hasShadow: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
    },
  });

  win.setAlwaysOnTop(true);
  win.loadURL("http://127.0.0.1:5173/assistant");

  win.on("closed", () => {
    win = null;
  });
}

/* =========================
   EXPANDIR / MINIMIZAR
========================= */

ipcMain.on("nexus-assistant:set-expanded", (event, expanded) => {
  const target = BrowserWindow.fromWebContents(event.sender);

  if (!target || target.isDestroyed()) return;

  const area = screen.getDisplayMatching(target.getBounds()).workArea;

  if (expanded) {
    target.setBounds({
      x: Math.max(
        area.x + EDGE_MARGIN,
        area.x + area.width - PANEL_WIDTH - EDGE_MARGIN
      ),
      y: Math.max(
        area.y + EDGE_MARGIN,
        area.y + area.height - PANEL_HEIGHT - EDGE_MARGIN
      ),
      width: PANEL_WIDTH,
      height: PANEL_HEIGHT,
    });
  } else {
    target.setBounds({
      x: area.x + area.width - ORB_SIZE - EDGE_MARGIN,
      y: area.y + area.height - ORB_SIZE - EDGE_MARGIN,
      width: ORB_SIZE,
      height: ORB_SIZE,
    });
  }
});

/* =========================
   AUTO START
========================= */

app.whenReady().then(() => {
  app.setLoginItemSettings({
    openAtLogin: true,
  });

  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  // Mantener NEXUS activo en segundo plano.
});
