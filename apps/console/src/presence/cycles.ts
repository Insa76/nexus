import type {
  NexusPresenceStateModel,
} from "./types";

export type CognitiveCycleStatus =
  | "active"
  | "completed"
  | "failed";

export type CognitiveCycleEvent = {
  id: string;
  type: string;
  timestamp: string;
  message?: string;
  data?: unknown;
};

export type CognitiveCycle = {
  id: string;
  startedAt: string;
  endedAt?: string;
  request?: CognitiveCycleEvent;
  events: CognitiveCycleEvent[];
  status: CognitiveCycleStatus;
  eventCount: number;
};

function getCycleStatus(
  events: CognitiveCycleEvent[],
): CognitiveCycleStatus {
  const lastEvent = events[events.length - 1];

  if (!lastEvent) {
    return "active";
  }

  if (
    lastEvent.type === "verification_failure" ||
    lastEvent.type === "failed"
  ) {
    return "failed";
  }

  if (
    lastEvent.type === "episode" ||
    lastEvent.type === "completed"
  ) {
    return "completed";
  }

  return "active";
}

function createCycle(
  events: CognitiveCycleEvent[],
): CognitiveCycle | null {
  if (events.length === 0) {
    return null;
  }

  const request = events.find(
    (event) => event.type === "user_request",
  );

  const startedAt =
    request?.timestamp ??
    events[0].timestamp;

  const lastEvent =
    events[events.length - 1];

  const status = getCycleStatus(events);

  return {
    id: request?.id ?? events[0].id,
    startedAt,
    endedAt:
      status === "active"
        ? undefined
        : lastEvent.timestamp,
    request,
    events,
    status,
    eventCount: events.length,
  };
}

export function buildCycleHistory(
  presence: NexusPresenceStateModel,
): CognitiveCycle[] {
  const sourceEvents = presence.events;

  if (sourceEvents.length === 0) {
    return [];
  }

  const cycles: CognitiveCycle[] = [];
  let currentEvents: CognitiveCycleEvent[] = [];

  for (const event of sourceEvents) {
    const normalizedEvent: CognitiveCycleEvent = {
      id: event.id,
      type: event.type,
      timestamp: event.timestamp,
      message: event.message,
      data: event.data,
    };

    if (
      normalizedEvent.type === "user_request" &&
      currentEvents.length > 0
    ) {
      const previousCycle = createCycle(
        currentEvents,
      );

      if (previousCycle) {
        cycles.push(previousCycle);
      }

      currentEvents = [];
    }

    currentEvents.push(normalizedEvent);
  }

  const lastCycle = createCycle(
    currentEvents,
  );

  if (lastCycle) {
    cycles.push(lastCycle);
  }

  return cycles;
}

export function getCurrentCycle(
  presence: NexusPresenceStateModel,
): CognitiveCycle | null {
  const cycles = buildCycleHistory(presence);

  return cycles.length > 0
    ? cycles[cycles.length - 1]
    : null;
}

export function getHistoricalCycles(
  presence: NexusPresenceStateModel,
): CognitiveCycle[] {
  const cycles = buildCycleHistory(presence);

  if (cycles.length <= 1) {
    return [];
  }

  return cycles.slice(0, -1);
}