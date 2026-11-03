
import { useEffect, useRef, useState } from "react";

import "./assistant.css";

type DesktopBridge = {
  setExpanded: (expanded: boolean) => void;
};

type ContextProject = {
  id: string;
  name: string;
  description?: string | null;
};

type ContextState = {
  user?: { name?: string; role?: string | null } | null;
  organization?: { name?: string; industry?: string | null } | null;
  projects?: ContextProject[];
  active_project_id?: string | null;
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
  const [contextOpen, setContextOpen] = useState(false);
  const [contextSaving, setContextSaving] = useState(false);
  const [contextMessage, setContextMessage] = useState("");
  const [profileName, setProfileName] = useState("");
  const [profileRole, setProfileRole] = useState("");
  const [organizationName, setOrganizationName] = useState("");
  const [organizationIndustry, setOrganizationIndustry] = useState("");
  const [projects, setProjects] = useState<ContextProject[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    document.body.classList.add("assistant-window");

    return () => {
      document.body.classList.remove("assistant-window");
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadContext() {
      try {
        const response = await fetch("http://127.0.0.1:8765/api/context", {
          headers: { Accept: "application/json" },
        });
        const payload = await response.json();
        if (!response.ok || payload?.success !== true || cancelled) return;

        const context = payload.context as ContextState;
        setProfileName(context.user?.name ?? "");
        setProfileRole(context.user?.role ?? "");
        setOrganizationName(context.organization?.name ?? "");
        setOrganizationIndustry(context.organization?.industry ?? "");
        const availableProjects = Array.isArray(context.projects)
          ? context.projects
          : [];
        setProjects(availableProjects);
        const activeId = context.active_project_id ?? "";
        setSelectedProjectId(activeId);
        const activeProject = availableProjects.find(
          (project) => project.id === activeId,
        );
        setProjectName(activeProject?.name ?? "");
        setProjectDescription(activeProject?.description ?? "");
      } catch {
        // El runtime puede iniciar después de la ventana Electron.
      }
    }

    void loadContext();
    return () => {
      cancelled = true;
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

  async function saveContext(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();
    if (contextSaving) return;

    if (!organizationName.trim() && projectName.trim()) {
      setContextMessage("Para asignar un proyecto primero completá la organización.");
      return;
    }

    const body: Record<string, unknown> = {};
    if (profileName.trim()) {
      body.user = {
        name: profileName.trim(),
        role: profileRole.trim() || null,
      };
    }
    body.organization = organizationName.trim()
      ? {
          name: organizationName.trim(),
          industry: organizationIndustry.trim() || null,
        }
      : null;
    body.project = projectName.trim()
      ? {
          ...(selectedProjectId ? { id: selectedProjectId } : {}),
          name: projectName.trim(),
          description: projectDescription.trim() || null,
        }
      : null;

    setContextSaving(true);
    setContextMessage("Guardando contexto local…");
    try {
      const response = await fetch("http://127.0.0.1:8765/api/context", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(body),
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok || payload?.success !== true) {
        throw new Error(
          getResponseError(payload, response.status),
        );
      }

      const context = payload.context as ContextState;
      const availableProjects = Array.isArray(context.projects)
        ? context.projects
        : [];
      setProjects(availableProjects);
      setSelectedProjectId(context.active_project_id ?? "");
      setContextMessage("Contexto guardado. NEXUS ya lo utiliza.");
    } catch (error) {
      setContextMessage(
        error instanceof Error
          ? error.message
          : "No se pudo guardar el contexto.",
      );
    } finally {
      setContextSaving(false);
    }
  }

  function selectProject(projectId: string) {
    setSelectedProjectId(projectId);
    const project = projects.find((item) => item.id === projectId);
    setProjectName(project?.name ?? "");
    setProjectDescription(project?.description ?? "");
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

          <div className="assistant-toolbar">
            <span className="assistant-context-label">
              {organizationName || profileName
                ? [organizationName, projectName].filter(Boolean).join(" · ")
                : "Contexto sin configurar"}
            </span>
            <button
              type="button"
              className="assistant-context-toggle"
              onClick={() => {
                setContextOpen((value) => !value);
                setContextMessage("");
              }}
            >
              {contextOpen ? "VOLVER" : "CONTEXTO"}
            </button>
          </div>

          {contextOpen ? (
            <form className="context-editor" onSubmit={saveContext}>
              <div className="context-fields">
                <input
                  value={profileName}
                  onChange={(event) => setProfileName(event.target.value)}
                  placeholder="Tu nombre"
                  aria-label="Nombre del usuario"
                  maxLength={160}
                />
                <input
                  value={profileRole}
                  onChange={(event) => setProfileRole(event.target.value)}
                  placeholder="Rol / función"
                  aria-label="Rol del usuario"
                  maxLength={160}
                />
                <input
                  value={organizationName}
                  onChange={(event) => setOrganizationName(event.target.value)}
                  placeholder="Organización"
                  aria-label="Nombre de la organización"
                  maxLength={160}
                />
                <input
                  value={organizationIndustry}
                  onChange={(event) => setOrganizationIndustry(event.target.value)}
                  placeholder="Actividad / sector"
                  aria-label="Actividad de la organización"
                  maxLength={160}
                />
                <select
                  value={selectedProjectId}
                  onChange={(event) => selectProject(event.target.value)}
                  aria-label="Proyecto existente"
                >
                  <option value="">Nuevo proyecto / sin proyecto activo</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </select>
                <input
                  value={projectName}
                  onChange={(event) => setProjectName(event.target.value)}
                  placeholder="Proyecto activo"
                  aria-label="Nombre del proyecto"
                  maxLength={160}
                />
                <input
                  value={projectDescription}
                  onChange={(event) => setProjectDescription(event.target.value)}
                  placeholder="Descripción breve del proyecto"
                  aria-label="Descripción del proyecto"
                  maxLength={2000}
                />
              </div>
              <button
                className="context-save"
                type="submit"
                disabled={contextSaving}
              >
                {contextSaving ? "GUARDANDO…" : "GUARDAR CONTEXTO"}
              </button>
              <div className="context-status" aria-live="polite">
                {contextMessage}
              </div>
            </form>
          ) : (
          <>
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

          </>
          )}

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
