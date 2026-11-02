
import type {
  NexusPresenceEvent,
  NexusPresenceState,
  NexusPresenceStateModel,
} from "./types";

export interface PresenceAdapter {
  getCurrentState(): NexusPresenceStateModel;

  subscribe(
    listener: (state: NexusPresenceStateModel) => void,
  ): () => void;
}

const PRESENCE_API_URL =
  "http://127.0.0.1:8765/api/presence";

const PRESENCE_EVENTS_URL =
  "http://127.0.0.1:8765/api/presence/events";

const POLL_INTERVAL_MS = 1000;

const initialPresence: NexusPresenceStateModel = {
  state: "idle",
  request: null,
  context: null,
  intent: null,
  decision: null,
  objective: null,
  plan: null,
  execution: null,
  verification: null,
  memory: null,
  learning: null,
  events: [],
};

class HttpPresenceAdapter implements PresenceAdapter {
  private state: NexusPresenceStateModel = initialPresence;

  private listeners = new Set<
    (state: NexusPresenceStateModel) => void
  >();

  private pollTimer: ReturnType<typeof setInterval> | null =
    null;

  private eventSource: EventSource | null = null;

  private refreshing = false;

  private sseConnected = false;

  private currentCycleStartedAt: string | null = null;

  private currentCycleEvents: NexusPresenceEvent[] = [];

  getCurrentState(): NexusPresenceStateModel {
    return this.state;
  }

  subscribe(
    listener: (state: NexusPresenceStateModel) => void,
  ): () => void {
    this.listeners.add(listener);

    listener(this.state);

    void this.refresh();

    this.startSSE();

    this.startPolling();

    return () => {
      this.listeners.delete(listener);

      if (this.listeners.size === 0) {
        this.stopSSE();
        this.stopPolling();
      }
    };
  }

  private startSSE(): void {
    if (this.eventSource !== null) {
      return;
    }

    if (typeof EventSource === "undefined") {
      return;
    }

    try {
      const eventSource = new EventSource(
        PRESENCE_EVENTS_URL,
      );

      this.eventSource = eventSource;

      eventSource.onopen = () => {
        this.sseConnected = true;
      };

      eventSource.addEventListener(
        "presence",
        (event) => {
          this.handlePresenceEvent(
            event as MessageEvent<string>,
          );
        },
      );

      eventSource.onerror = () => {
        this.sseConnected = false;
      };
    } catch {
      this.sseConnected = false;
      this.eventSource = null;
    }
  }

  private stopSSE(): void {
    if (this.eventSource === null) {
      return;
    }

    this.eventSource.close();

    this.eventSource = null;
    this.sseConnected = false;
  }

  private handlePresenceEvent(
    event: MessageEvent<string>,
  ): void {
    try {
      const payload = JSON.parse(
        event.data,
      ) as {
        state?: string;
        timestamp?: string;
        message?: string | null;
        data?: unknown;
      };

      if (!payload.state) {
        return;
      }

      const state = this.normalizeState(
        payload.state,
      );

      if (state === null) {
        return;
      }

      const timestamp =
        payload.timestamp ??
        new Date().toISOString();

      if (state === "listening") {
        this.startNewCycle(timestamp);
      }

      const presenceEvent: NexusPresenceEvent = {
        id: `sse-${Date.now()}-${Math.random()
          .toString(36)
          .slice(2, 8)}`,
        type: state,
        timestamp,
        message: payload.message ?? undefined,
        data: payload.data,
      };

      this.addCurrentCycleEvent(presenceEvent);

      this.state = {
        ...this.state,
        state,
        events: this.currentCycleEvents,
      };

      this.emit();

      if (
        state === "completed" ||
        state === "failed"
      ) {
        void this.refresh();
      }
    } catch {
      // Un evento SSE inválido no debe interrumpir el adapter.
    }
  }

  private startNewCycle(timestamp: string): void {
    this.currentCycleStartedAt = timestamp;
    this.currentCycleEvents = [];
  }

  private addCurrentCycleEvent(
    event: NexusPresenceEvent,
  ): void {
    const exists = this.currentCycleEvents.some(
      (existing) =>
        existing.timestamp === event.timestamp &&
        existing.type === event.type &&
        existing.message === event.message,
    );

    if (exists) {
      return;
    }

    this.currentCycleEvents = [
      ...this.currentCycleEvents,
      event,
    ];
  }

  private normalizeState(
    value: string,
  ): NexusPresenceState | null {
    const states: NexusPresenceState[] = [
      "idle",
      "listening",
      "understanding",
      "thinking",
      "deciding",
      "executing",
      "verifying",
      "completed",
      "needs_confirmation",
      "failed",
      "recovering",
    ];

    if (states.includes(value as NexusPresenceState)) {
      return value as NexusPresenceState;
    }

    return null;
  }

  private startPolling(): void {
    if (this.pollTimer !== null) {
      return;
    }

    this.pollTimer = setInterval(() => {
      void this.refresh();
    }, POLL_INTERVAL_MS);
  }

  private stopPolling(): void {
    if (this.pollTimer === null) {
      return;
    }

    clearInterval(this.pollTimer);

    this.pollTimer = null;
  }

  private async refresh(): Promise<void> {
    if (this.refreshing) {
      return;
    }

    this.refreshing = true;

    try {
      const response = await fetch(
        PRESENCE_API_URL,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
          },
        },
      );

      if (!response.ok) {
        throw new Error(
          `Presence API returned HTTP ${response.status}`,
        );
      }

      const nextState =
        (await response.json()) as NexusPresenceStateModel;

      if (
        !this.isValidSnapshot(nextState) ||
        !this.shouldAcceptSnapshot(nextState)
      ) {
        return;
      }

      const events = this.resolveSnapshotEvents(
        nextState,
      );

      this.state = {
        ...nextState,
        events,
      };

      this.emit();
    } catch {
      // Conservamos el último estado real recibido.
      // Nunca inventamos una ejecución exitosa.
    } finally {
      this.refreshing = false;
    }
  }

  private isValidSnapshot(
    value: unknown,
  ): value is NexusPresenceStateModel {
    if (!value || typeof value !== "object") {
      return false;
    }

    const snapshot = value as Record<string, unknown>;

    return (
      typeof snapshot.state === "string" &&
      Array.isArray(snapshot.events)
    );
  }

  private resolveSnapshotEvents(
    nextState: NexusPresenceStateModel,
  ): NexusPresenceEvent[] {
    if (this.currentCycleStartedAt !== null) {
      return this.currentCycleEvents;
    }

    return this.filterToLatestSnapshotCycle(nextState);
  }

  private filterToLatestSnapshotCycle(
    presence: NexusPresenceStateModel,
  ): NexusPresenceEvent[] {
    if (presence.events.length === 0) {
      return [];
    }

    const requestTimestamp =
      presence.request?.timestamp;

    if (requestTimestamp) {
      const requestTime = Date.parse(requestTimestamp);

      if (!Number.isNaN(requestTime)) {
        return presence.events.filter((event) => {
          const eventTime = Date.parse(event.timestamp);

          if (Number.isNaN(eventTime)) {
            return true;
          }

          return eventTime >= requestTime;
        });
      }
    }

    let latestRequestIndex = -1;

    for (
      let index = 0;
      index < presence.events.length;
      index += 1
    ) {
      if (presence.events[index].type === "request") {
        latestRequestIndex = index;
      }
    }

    if (latestRequestIndex >= 0) {
      return presence.events.slice(latestRequestIndex);
    }

    return presence.events;
  }

  private shouldAcceptSnapshot(
    nextState: NexusPresenceStateModel,
  ): boolean {
    if (!this.sseConnected) {
      return true;
    }

    if (
      nextState.state === "completed" ||
      nextState.state === "failed"
    ) {
      return true;
    }

    return this.isSnapshotNewer(
      nextState,
      this.state,
    );
  }

  private isSnapshotNewer(
    nextState: NexusPresenceStateModel,
    currentState: NexusPresenceStateModel,
  ): boolean {
    const nextTimestamp =
      this.getLatestTimestamp(nextState);

    const currentTimestamp =
      this.getLatestTimestamp(currentState);

    if (
      nextTimestamp === null ||
      currentTimestamp === null
    ) {
      return true;
    }

    return nextTimestamp >= currentTimestamp;
  }

  private getLatestTimestamp(
    state: NexusPresenceStateModel,
  ): number | null {
    const timestamps: number[] = [];

    if (state.request?.timestamp) {
      const value = Date.parse(
        state.request.timestamp,
      );

      if (!Number.isNaN(value)) {
        timestamps.push(value);
      }
    }

    for (const event of state.events) {
      const value = Date.parse(event.timestamp);

      if (!Number.isNaN(value)) {
        timestamps.push(value);
      }
    }

    if (timestamps.length === 0) {
      return null;
    }

    return Math.max(...timestamps);
  }

  private emit(): void {
    for (const listener of this.listeners) {
      listener(this.state);
    }
  }
}

export const presenceAdapter =
  new HttpPresenceAdapter();
