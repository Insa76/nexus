import type { NexusPresenceStateModel } from "./types";

export const mockPresence: NexusPresenceStateModel = {
  state: "completed",

  request: {
    text: "Cerrá Chrome",
    timestamp: new Date().toISOString(),
  },

  context: null,

  intent: {
    name: "close_application",
    confidence: 0.97,
  },

  decision: {
    type: "execute",
    reason:
      "The requested action is clear and executable.",
  },

  objective: {
    description: "Close Chrome",
  },

  plan: {
    steps: [
      {
        id: "step-1",
        action: "system.close_app",
        status: "completed",
        description:
          "Close the requested application.",
      },
    ],
  },

  execution: {
    status: "completed",
    action: "system.close_app",
    result: {
      success: true,
    },
  },

  verification: {
    status: "verified",
    confidence: 1,
    message:
      "The requested application was closed successfully.",
  },

  memory: {
    status: "stored",
    entries: 1,
  },

  learning: {
    status: "learned",
    message:
      "Execution experience available for future reuse.",
  },

  events: [
    {
      id: "event-1",
      type: "request",
      timestamp: new Date().toISOString(),
      message: "Request received.",
    },
    {
      id: "event-2",
      type: "intent",
      timestamp: new Date().toISOString(),
      message: "Intent resolved.",
    },
    {
      id: "event-3",
      type: "decision",
      timestamp: new Date().toISOString(),
      message: "Decision: execute.",
    },
    {
      id: "event-4",
      type: "execution",
      timestamp: new Date().toISOString(),
      message: "Action executed.",
    },
    {
      id: "event-5",
      type: "verification",
      timestamp: new Date().toISOString(),
      message: "Execution verified.",
    },
  ],
};