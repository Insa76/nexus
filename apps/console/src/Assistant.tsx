
import { useEffect, useRef, useState } from "react";

import "./assistant.css";

type DesktopBridge = {
  setExpanded: (expanded: boolean) => void;
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

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    document.body.classList.add("assistant-window");

    return () => {
      document.body.classList.remove("assistant-window");
    };
  }, []);

  function togglePanel() {
    const next = !expanded;

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

  async function submitCommand(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const text = command.trim();

    if (!text || busy) {
      return;
    }

    setBusy(true);
    setFeedback("NEXUS está procesando la instrucción…");

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
          getResponseError(payload, response.status),
        );
      }

      if (
        payload &&
        typeof payload === "object"
      ) {
        const data = payload as Record<string, unknown>;

        if (data.success === false) {
          throw new Error(
            getResponseError(payload, response.status),
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
          "Instrucción enviada. No se recibió contenido de respuesta.",
        );
      }

      setCommand("");
    } catch (error) {
      setFeedback(
        error instanceof Error
          ? error.message
          : "No se pudo enviar la instrucción.",
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
              placeholder="Escribí una instrucción…"
              aria-label="Instrucción para NEXUS"
              disabled={busy}
            />

            <button
              className="assistant-send"
              type="submit"
              disabled={busy || !command.trim()}
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
            {busy && <span className="feedback-dot" />}

            <pre>
              {feedback ||
                "Disponible para recibir instrucciones."}
            </pre>
          </div>

          <footer className="assistant-footer">
            <span>
              {busy ? "PROCESANDO" : "RUNTIME LOCAL"}
            </span>

            <button
              type="button"
              className="assistant-mic"
              onClick={() =>
                setFeedback(
                  "La entrada por voz se integrará en la siguiente etapa.",
                )
              }
              title="Entrada por voz: próxima etapa"
              aria-label="Entrada por voz"
            >
              MIC
            </button>
          </footer>
        </section>
      )}
    </main>
  );
}
