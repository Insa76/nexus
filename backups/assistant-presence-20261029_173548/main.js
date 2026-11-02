const { app, BrowserWindow } = require("electron")

let win

function createWindow() {

  win = new BrowserWindow({
    width: 320,
    height: 320,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  })

  win.loadURL("http://127.0.0.1:5173/assistant")
}

/* =========================
   AUTO START
========================= */

app.whenReady().then(() => {

  // 🔥 Auto iniciar al prender la PC
  app.setLoginItemSettings({
    openAtLogin: true
  })

  createWindow()
})