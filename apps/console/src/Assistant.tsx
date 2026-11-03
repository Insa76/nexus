
import { useEffect, useRef, useState } from "react";

import "./assistant.css";

type VoiceEvent = {
  type:
    | "status"
    | "partial"
    | "final"
    | "error"
    | "stopped";

  state?: string;
  text?: string;
  message?: string;
};

type VoiceActionResult = {
  success: boolean;
  message?: string;
};

type DesktopBridge = {
  setExpanded: (expanded: boolean) => void;

  startVoice: () => Promise<VoiceActionResult>;

  stopVoice: () => Promise<VoiceActionResult>;

  onVoiceEvent: (
    callback: (event: VoiceEvent) => void
  ) => () => void;
};

declare global {
  interface Window {
    nexusDesktop?: DesktopBridge;
  }
}

function getResponseError(
  payload: unknown,
  status: number,
): string {
  if (
    payload &&
    typeof payload === "object"
  ) {
    const data = payload as Record<string, unknown>;

    if (
      typeof data.message === "string" &&
      data.message.trim()
    ) {
      return data.message;
    }

    if (
      typeof data.error === "string" &&
      data.error.trim()
    ) {
      return data.error;
    }
  }

  return `Error HTTP ${status}`;
}

export default function Assistant() {
  const [expanded, setExpanded] = useState(false);

  const [command, setCommand] = useState("");

  const [busy, setBusy] = useState(false);

  const [feedback, setFeedback] = useState("");

  const [voiceActive, setVoiceActive] = useState(false);

  const [voiceDraft, setVoiceDraft] = useState("");

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    document.body.classList.add("assistant-window");

    return () => {
      document.body.classList.remove("assistant-window");
    };
  }, []);

  useEffect(() => {
    const unsubscribe =
      window.nexusDesktop?.onVoiceEvent((event) => {
        if (event.type === "status") {
          if (event.state === "listening") {
            setFeedback("NEXUS está escuchando...");
          } else if (event.message) {
            setFeedback(event.message);
          }

          return;
        }

        if (event.type === "partial") {
          setVoiceDraft(event.text ?? "");
          return;
        }

        if (event.type === "final") {
          setVoiceActive(false);
          setVoiceDraft("");

          const transcript = event.text?.trim() ?? "";

          if (transcript) {
            setCommand((current) => {
              const separator = current.trim()
                ? " "
                : "";

              return `${current}${separator}${transcript}`;
            });

            setFeedback(
              "Transcripción lista. Revisá la instrucción y enviala."
            );
          } else {
            setFeedback(
              "No se reconoció ninguna instrucción. Podés volver a intentarlo."
            );
          }

          return;
        }

        if (event.type === "error") {
          setVoiceActive(false);
          setVoiceDraft("");

          setFeedback(
            event.message ??
              "No se pudo iniciar el reconocimiento de voz."
          );

          return;
        }

        if (event.type === "stopped") {
          setVoiceActive(false);
        }
      });

    return () => {
      unsubscribe?.();
    };
  }, []);

  useEffect(() => {
    return () => {
      void window.nexusDesktop?.stopVoice();
    };
  }, []);

  function togglePanel() {
    const next = !expanded;

    if (!next && voiceActive) {
      void stopVoice();
    }

    setExpanded(next);
    setFeedback("");

    window.nexusDesktop?.setExpanded(next);

    if (next) {
      window.setTimeout(
        () => inputRef.current?.focus(),
        120,
      );
    }
  }

  async function startVoice() {
    const desktop = window.nexusDesktop;

    if (!desktop) {
      setFeedback(
        "La entrada de voz local está disponible en la ventana de escritorio de NEXUS."
      );
      return;
    }

    setVoiceDraft("");
    setVoiceActive(true);

    setFeedback(
      "Preparando reconocimiento de voz local..."
    );

    try {
      const result = await desktop.startVoice();

      if (!result.success) {
        throw new Error(
          result.message ??
            "No se pudo iniciar el reconocimiento de voz."
        );
      }
    } catch (error) {
      setVoiceActive(false);

      setFeedback(
        error instanceof Error
          ? error.message
          : "No se pudo iniciar el reconocimiento de voz."
      );
    }
  }

  async function stopVoice() {
    const desktop = window.nexusDesktop;

    if (!desktop) {
      setVoiceActive(false);
      return;
    }

    setFeedback(
      "Finalizando la captura y preparando la transcripción..."
    );

    try {
      const result = await desktop.stopVoice();

      if (!result.success) {
        throw new Error(
          result.message ??
            "No se pudo detener la captura de voz."
        );
      }
    } catch (error) {
      setVoiceActive(false);

      setFeedback(
        error instanceof Error
          ? error.message
          : "No se pudo detener la captura de voz."
      );
    }
  }

  function toggleVoice() {
    if (voiceActive) {
      void stopVoice();
    } else {
      void startVoice();
    }
  }

  async function submitCommand(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const text = command.trim();

    if (!text || busy || voiceActive) {
      return;
    }

    setBusy(true);

    setFeedback(
      "NEXUS está procesando la instrucción..."
    );

    try {
      const response = await fetch(
        "http://127.0.0.1:8765/api/execute",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify({ text }),
        },
      );

      const payload: unknown =
        await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          getResponseError(
            payload,
            response.status,
          ),
        );
      }

      if (
        payload &&
        typeof payload === "object"
      ) {
        const data = payload as Record<string, unknown>;

        if (data.success === false) {
          throw new Error(
            getResponseError(
              payload,
              response.status,
            ),
          );
        }

        const message = [
          "message",
          "response",
          "result",
          "output",
          "text",
        ]
          .map((key) => data[key])
          .find(
            (value) =>
              typeof value === "string" &&
              value.length > 0,
          );

        setFeedback(
          typeof message === "string"
            ? message
            : JSON.stringify(payload, null, 2),
        );
      } else if (typeof payload === "string") {
        setFeedback(payload);
      } else {
        setFeedback(
          "Instrucción enviada. No se recibió contenido de respuesta."
        );
      }

      setCommand("");
    } catch (error) {
      setFeedback(
        error instanceof Error
          ? error.message
          : "No se pudo enviar la instrucción."
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main
      className={`presence ${
        expanded ? "presence-expanded" : ""
      }`}
    >
      {!expanded ? (
        <button
          className="presence-orb"
          type="button"
          aria-label="Activar NEXUS"
          title="Activar NEXUS"
          onClick={togglePanel}
        >
          <span className="orb-halo" />
          <span className="orb-core" />
        </button>
      ) : (
        <section className="assistant-panel">
          <header className="assistant-header">
            <span className="assistant-brand">
              <span className="mini-orb" />

              NEXUS

              <small>PRESENCE</small>
            </span>

            <button
              className="assistant-close"
              type="button"
              onClick={togglePanel}
              aria-label="Volver al modo discreto"
              title="Minimizar"
            >
              −
            </button>
          </header>

          <form
            className="assistant-form"
            onSubmit={submitCommand}
          >
            <input
              ref={inputRef}
              value={command}
              onChange={(event) =>
                setCommand(event.target.value)
              }
              placeholder="Escribí o dictá una instrucción..."
              aria-label="Instrucción para NEXUS"
              disabled={busy}
            />

            <button
              className="assistant-send"
              type="submit"
              disabled={
                busy ||
                voiceActive ||
                !command.trim()
              }
              aria-label="Enviar instrucción"
              title="Enviar"
            >
              ↑
            </button>
          </form>

          <div
            className="assistant-feedback"
            aria-live="polite"
          >
            {busy && (
              <span className="feedback-dot" />
            )}

            <pre>
              {voiceActive && voiceDraft
                ? `Escuchando: ${voiceDraft}`
                : feedback ||
                  "Disponible para recibir instrucciones."}
            </pre>
          </div>

          <footer className="assistant-footer">
            <span>
              {busy
                ? "PROCESANDO"
                : voiceActive
                  ? "ESCUCHANDO LOCALMENTE"
                  : "RUNTIME LOCAL"}
            </span>

            <button
              type="button"
              className={`assistant-mic ${
                voiceActive ? "is-listening" : ""
              }`}
              onClick={toggleVoice}
              disabled={busy}
              title={
                voiceActive
                  ? "Detener captura de voz"
                  : "Dar una instrucción hablada"
              }
              aria-label={
                voiceActive
                  ? "Detener captura de voz"
                  : "Iniciar captura de voz"
              }
            >
              {voiceActive ? "STOP" : "MIC"}
            </button>
          </footer>
        </section>
      )}
    </main>
  );
}
