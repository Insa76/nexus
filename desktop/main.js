const { app, BrowserWindow, Tray, Menu, globalShortcut } = require("electron")
const path = require("path")
const { spawn } = require("child_process")

let win
let tray

// 🔹 rutas seguras
const frontendPath = path.join(__dirname, "../frontend/dist/index.html")
const splashPath = path.join(__dirname, "splash.html")
const backendPath = path.join(__dirname, "../backend/dist/nexus-backend.exe")


function createWindow() {

  win = new BrowserWindow({
    width: 800,
    height: 500,
    show: false,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    center: true,
    webPreferences: {
      nodeIntegration: false
    }
  })

  // 🔥 primero splash
  win.loadFile(splashPath)

  // 🔥 después carga app real (delay pequeño)
  setTimeout(() => {
    win.loadFile(frontendPath)
  }, 1200)
}


function toggle() {
  if (win.isVisible()) win.hide()
  else {
    win.show()
    win.focus()
  }
}


app.whenReady().then(() => {

  createWindow()

  // 🔥 backend exe (rutas seguras)
  spawn(backendPath, [], {
    detached: true,
    stdio: "ignore"
  })

  // 🔥 autostart windows
  app.setLoginItemSettings({
    openAtLogin: true
  })

  // 🔥 tray
  tray = new Tray(path.join(__dirname, "icon.ico"))

  const menu = Menu.buildFromTemplate([
    { label: "Abrir Nexus", click: toggle },
    { type: "separator" },
    { label: "Salir", click: () => app.quit() }
  ])

  tray.setToolTip("Nexus IA")
  tray.setContextMenu(menu)

  // 🔥 hotkey global
  globalShortcut.register("Control+Space", toggle)
})


// 🔥 limpieza correcta
app.on("will-quit", () => {
  globalShortcut.unregisterAll()
})
