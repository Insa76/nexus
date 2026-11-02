const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("nexusDesktop", {
  setExpanded(expanded) {
    ipcRenderer.send("nexus-assistant:set-expanded", Boolean(expanded));
  },
});