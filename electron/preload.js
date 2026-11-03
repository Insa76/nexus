
const {
  contextBridge,
  ipcRenderer,
} = require("electron");

contextBridge.exposeInMainWorld(
  "nexusDesktop",
  {
    setExpanded(expanded) {
      ipcRenderer.send(
        "nexus-assistant:set-expanded",
        Boolean(expanded)
      );
    },

    startVoice() {
      return ipcRenderer.invoke(
        "nexus-assistant:voice-start"
      );
    },

    stopVoice() {
      return ipcRenderer.invoke(
        "nexus-assistant:voice-stop"
      );
    },

    onVoiceEvent(callback) {
      if (typeof callback !== "function") {
        return () => {};
      }

      const listener = (_event, payload) => {
        callback(payload);
      };

      ipcRenderer.on(
        "nexus-assistant:voice-event",
        listener
      );

      return () => {
        ipcRenderer.removeListener(
          "nexus-assistant:voice-event",
          listener
        );
      };
    },
  }
);
