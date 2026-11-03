
const {
  app,
  BrowserWindow,
  ipcMain,
  screen,
  Tray,
  Menu,
  nativeImage,
  globalShortcut,
} = require("electron");

const path = require("path");
const { spawn, spawnSync } = require("child_process");

const ROOT_DIR = path.resolve(__dirname, "..");
const CONSOLE_DIR = path.join(ROOT_DIR, "apps", "console");

const API_URL = "http://127.0.0.1:8765/api/status";
const CONSOLE_URL = "http://127.0.0.1:5173/assistant";

const ORB_SIZE = 88;
const PANEL_WIDTH = 420;
const PANEL_HEIGHT = 320;
const EDGE_MARGIN = 24;

const STARTUP_TIMEOUT_MS = 90000;

let win = null;
let tray = null;
let quitting = false;
let startupPromise = null;

let runtimeProcess = null;
let consoleProcess = null;
let voiceProcess = null;
let voiceBuffer = "";

const ownedProcesses = new Set();

function log(message) {
  console.log(`[NEXUS DESKTOP] ${message}`);
}

function sendVoiceEvent(payload) {
  if (!win || win.isDestroyed()) return;

  win.webContents.send(
    "nexus-assistant:voice-event",
    payload
  );
}

function isProcessAlive(child) {
  return Boolean(
    child &&
    child.pid &&
    child.exitCode === null &&
    !child.killed
  );
}

function trackProcess(child) {
  if (!child || !child.pid) return;

  ownedProcesses.add(child);

  child.once("close", () => {
    ownedProcesses.delete(child);
  });
}

async function isEndpointReady(url) {
  try {
    const controller = new AbortController();

    const timeout = setTimeout(
      () => controller.abort(),
      2500
    );

    const response = await fetch(url, {
      method: "GET",
      signal: controller.signal,
    });

    clearTimeout(timeout);

    return response.ok;
  } catch {
    return false;
  }
}

async function waitForEndpoint(
  url,
  name,
  child,
  timeoutMs = STARTUP_TIMEOUT_MS
) {
  const deadline = Date.now() + timeoutMs;

  while (Date.now() < deadline) {
    if (quitting) {
      throw new Error(
        "El inicio de NEXUS fue cancelado."
      );
    }

    if (child && !isProcessAlive(child)) {
      throw new Error(
        `${name} terminó antes de estar disponible.`
      );
    }

    if (await isEndpointReady(url)) {
      log(`${name} disponible.`);
      return;
    }

    await new Promise((resolve) =>
      setTimeout(resolve, 750)
    );
  }

  throw new Error(
    `Tiempo agotado esperando ${name}: ${url}`
  );
}

function spawnRuntime() {
  log("Iniciando runtime Python...");

  const child = spawn(
    "uv",
    [
      "run",
      "python",
      "-u",
      "server.py",
    ],
    {
      cwd: ROOT_DIR,
      windowsHide: true,
      stdio: "ignore",
    }
  );

  runtimeProcess = child;
  trackProcess(child);

  child.on("error", (error) => {
    log(`Error iniciando runtime: ${error.message}`);
  });

  child.on("close", (code) => {
    if (runtimeProcess === child) {
      runtimeProcess = null;
    }

    if (!quitting) {
      log(`Runtime finalizó con código ${code}.`);
    }
  });

  return child;
}

function spawnConsole() {
  log("Iniciando consola React...");

  const child = spawn(
    "npm.cmd",
    [
      "run",
      "dev",
      "--",
      "--host",
      "127.0.0.1",
      "--port",
      "5173",
      "--strictPort",
    ],
    {
      cwd: CONSOLE_DIR,
      windowsHide: true,
      shell: true,
      stdio: "ignore",
    }
  );

  consoleProcess = child;
  trackProcess(child);

  child.on("error", (error) => {
    log(`Error iniciando consola: ${error.message}`);
  });

  child.on("close", (code) => {
    if (consoleProcess === child) {
      consoleProcess = null;
    }

    if (!quitting) {
      log(`Consola finalizó con código ${code}.`);
    }
  });

  return child;
}

async function ensureServices() {
  let apiReady = await isEndpointReady(API_URL);

  if (!apiReady) {
    const child = spawnRuntime();

    await waitForEndpoint(
      API_URL,
      "Runtime NEXUS",
      child
    );
  } else {
    log("Runtime existente detectado. No se inicia otro.");
  }

  let consoleReady = await isEndpointReady(
    "http://127.0.0.1:5173/"
  );

  if (!consoleReady) {
    const child = spawnConsole();

    await waitForEndpoint(
      "http://127.0.0.1:5173/",
      "Consola React",
      child
    );
  } else {
    log("Consola existente detectada. No se inicia otra.");
  }
}

function getTrayImage() {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg"
         width="32" height="32" viewBox="0 0 32 32">
      <circle cx="16" cy="16" r="13"
              fill="#071725"
              stroke="#7ad8ff"
              stroke-width="1.5"/>
      <circle cx="16" cy="16" r="7"
              fill="#247eb1"
              stroke="#b4eaff"
              stroke-width="1"/>
      <circle cx="13" cy="12" r="2"
              fill="#ffffff"/>
    </svg>
  `;

  return nativeImage.createFromDataURL(
    `data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}`
  );
}

function positionWindow(expanded) {
  if (!win || win.isDestroyed()) return;

  const area = screen
    .getDisplayMatching(win.getBounds())
    .workArea;

  if (expanded) {
    win.setBounds({
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
    win.setBounds({
      x: area.x + area.width - ORB_SIZE - EDGE_MARGIN,
      y: area.y + area.height - ORB_SIZE - EDGE_MARGIN,
      width: ORB_SIZE,
      height: ORB_SIZE,
    });
  }
}

function showWindow() {
  if (!win || win.isDestroyed()) return;

  win.show();
  win.focus();
}

function toggleWindow() {
  if (!win || win.isDestroyed()) return;

  if (win.isVisible()) {
    win.hide();
  } else {
    showWindow();
  }
}

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
    show: false,

    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
    },
  });

  win.setAlwaysOnTop(true);

  win.loadURL(CONSOLE_URL);

  win.once("ready-to-show", () => {
    if (!quitting) {
      win.show();
    }
  });

  win.on("close", (event) => {
    if (!quitting) {
      event.preventDefault();
      win.hide();
    }
  });

  win.on("closed", () => {
    win = null;
  });
}

function createTray() {
  tray = new Tray(getTrayImage());

  tray.setToolTip("NEXUS - Asistente local");

  const menu = Menu.buildFromTemplate([
    {
      label: "Abrir NEXUS",
      click: showWindow,
    },
    {
      label: "Ocultar NEXUS",
      click: () => win?.hide(),
    },
    {
      type: "separator",
    },
    {
      label: "Salir de NEXUS",
      click: () => app.quit(),
    },
  ]);

  tray.setContextMenu(menu);

  tray.on("double-click", showWindow);
}

function startVoiceProcess() {
  if (voiceProcess) {
    return {
      success: false,
      message: "El reconocimiento de voz ya está activo.",
    };
  }

  const scriptPath = path.join(
    __dirname,
    "voice_listener.py"
  );

  sendVoiceEvent({
    type: "status",
    state: "starting",
    message: "Iniciando reconocimiento de voz local...",
  });

  const child = spawn(
    "uv",
    [
      "run",
      "--with",
      "vosk",
      "--with",
      "sounddevice",
      "python",
      "-u",
      scriptPath,
    ],
    {
      cwd: ROOT_DIR,
      windowsHide: true,
      stdio: [
        "pipe",
        "pipe",
        "pipe",
      ],
    }
  );

  voiceProcess = child;
  voiceBuffer = "";

  trackProcess(child);

  child.stdout.on("data", (chunk) => {
    voiceBuffer += chunk.toString("utf8");

    const lines = voiceBuffer.split(/\r?\n/);

    voiceBuffer = lines.pop() || "";

    for (const line of lines) {
      if (!line.trim()) continue;

      try {
        sendVoiceEvent(JSON.parse(line));
      } catch {
        log("Se recibió una línea de voz no válida.");
      }
    }
  });

  child.stderr.on("data", (chunk) => {
    const message = chunk.toString("utf8").trim();

    if (message) {
      log(`[VOICE] ${message}`);
    }
  });

  child.on("error", (error) => {
    sendVoiceEvent({
      type: "error",
      message:
        error.code === "ENOENT"
          ? "No se encontró uv en PATH."
          : error.message,
    });

    if (voiceProcess === child) {
      voiceProcess = null;
      voiceBuffer = "";
    }
  });

  child.on("close", (code) => {
    if (voiceBuffer.trim()) {
      try {
        sendVoiceEvent(
          JSON.parse(voiceBuffer)
        );
      } catch {
        // No existe un evento final válido.
      }
    }

    if (
      code !== 0 &&
      voiceProcess === child
    ) {
      sendVoiceEvent({
        type: "error",
        message: `El proceso de voz terminó con código ${code}.`,
      });
    }

    if (voiceProcess === child) {
      voiceProcess = null;
      voiceBuffer = "";
    }

    sendVoiceEvent({
      type: "stopped",
    });
  });

  return {
    success: true,
  };
}

function stopVoiceProcess() {
  if (!voiceProcess) {
    return {
      success: false,
      message: "No hay una captura de voz activa.",
    };
  }

  try {
    voiceProcess.stdin.write("stop\n");

    return {
      success: true,
    };
  } catch (error) {
    return {
      success: false,
      message: error.message,
    };
  }
}

function registerIpc() {
  ipcMain.on(
    "nexus-assistant:set-expanded",
    (event, expanded) => {
      if (
        !win ||
        event.sender !== win.webContents
      ) {
        return;
      }

      positionWindow(Boolean(expanded));
    }
  );

  ipcMain.handle(
    "nexus-assistant:voice-start",
    (event) => {
      if (
        !win ||
        event.sender !== win.webContents
      ) {
        return {
          success: false,
          message: "Origen de solicitud no permitido.",
        };
      }

      return startVoiceProcess();
    }
  );

  ipcMain.handle(
    "nexus-assistant:voice-stop",
    (event) => {
      if (
        !win ||
        event.sender !== win.webContents
      ) {
        return {
          success: false,
          message: "Origen de solicitud no permitido.",
        };
      }

      return stopVoiceProcess();
    }
  );
}

function terminateChild(child) {
  if (!child || !child.pid) return;

  if (process.platform === "win32") {
    spawnSync(
      "taskkill",
      [
        "/PID",
        String(child.pid),
        "/T",
        "/F",
      ],
      {
        windowsHide: true,
        stdio: "ignore",
      }
    );
  } else {
    try {
      child.kill("SIGTERM");
    } catch {
      // El proceso puede haber finalizado.
    }
  }
}

function stopOwnedProcesses() {
  if (voiceProcess) {
    try {
      voiceProcess.stdin.write("stop\n");
    } catch {
      // El proceso puede estar cerrándose.
    }
  }

  for (const child of ownedProcesses) {
    terminateChild(child);
  }

  ownedProcesses.clear();

  voiceProcess = null;
  runtimeProcess = null;
  consoleProcess = null;
}

async function initialize() {
  if (startupPromise) {
    return startupPromise;
  }

  startupPromise = (async () => {
    try {
      log("Comprobando servicios...");

      await ensureServices();

      if (quitting) return;

      createWindow();
      createTray();

      globalShortcut.register(
        "Control+Space",
        toggleWindow
      );

      // El inicio automático queda desactivado
      // hasta que exista un instalador de producción.
      app.setLoginItemSettings({
        openAtLogin: false,
      });

      log("NEXUS Desktop está disponible.");
    } catch (error) {
      log(error.message);

      const { dialog } = require("electron");

      dialog.showErrorBox(
        "No se pudo iniciar NEXUS",
        `${error.message}\n\nRevisá que uv, Node.js y las dependencias del proyecto estén instalados.`
      );

      app.quit();
    }
  })();

  return startupPromise;
}

app.whenReady().then(() => {
  registerIpc();
  return initialize();
});

app.on("activate", () => {
  if (win && !win.isDestroyed()) {
    showWindow();
  }
});

app.on("before-quit", () => {
  quitting = true;

  globalShortcut.unregisterAll();

  if (tray) {
    tray.destroy();
    tray = null;
  }

  stopOwnedProcesses();
});

app.on("window-all-closed", () => {
  // NEXUS permanece en la bandeja del sistema.
});
