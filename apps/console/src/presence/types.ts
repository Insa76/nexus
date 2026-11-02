export type NexusPresenceState =
  | "idle"
  | "listening"
  | "understanding"
  | "thinking"
  | "deciding"
  | "executing"
  | "verifying"
  | "completed"
  | "needs_confirmation"
  | "failed"
  | "recovering";

export type NexusDecisionType =
  | "execute"
  | "confirm"
  | "reject"
  | "recover"
  | "none";

export type NexusExecutionStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed";

export type NexusVerificationStatus =
  | "pending"
  | "verified"
  | "verified_with_limited_evidence"
  | "failed";

export type NexusMemoryStatus =
  | "pending"
  | "not_required"
  | "stored"
  | "failed";

export type NexusLearningStatus =
  | "pending"
  | "not_required"
  | "learned"
  | "failed";

export type NexusPlanStepStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "skipped";

export interface NexusPresenceRequest {
  text: string;
  timestamp?: string;
}

export interface NexusPresenceContext {
  recent_interactions?: unknown[];
  recent_episodes?: unknown[];
  semantic_knowledge?: unknown[];
  last_request?: unknown;
  last_intent?: unknown;
  last_result?: unknown;
  [key: string]: unknown;
}

export interface NexusPresenceIntent {
  name: string;
  confidence: number;
}

export interface NexusPresenceDecision {
  type: NexusDecisionType;
  reason?: string;
}

export interface NexusPresenceObjective {
  description: string;
}

export interface NexusPresencePlanStep {
  id?: string;
  action: string;
  status: NexusPlanStepStatus;
  description?: string;
}

export interface NexusPresencePlan {
  steps: NexusPresencePlanStep[];
}

export interface NexusPresenceExecution {
  status: NexusExecutionStatus;
  action?: string;
  result?: unknown;
  error?: string | null;
}

export interface NexusPresenceVerification {
  status: NexusVerificationStatus;
  confidence?: number;
  message?: string;
}

export interface NexusPresenceMemory {
  status: NexusMemoryStatus;
  entries?: number;
  message?: string;
}

export interface NexusPresenceLearning {
  status: NexusLearningStatus;
  message?: string;
}

export interface NexusPresenceEvent {
  id: string;
  type: string;
  timestamp: string;
  message?: string;
  data?: unknown;
}

export interface NexusPresenceStateModel {
  state: NexusPresenceState;

  request: NexusPresenceRequest | null;

  context: NexusPresenceContext | null;

  intent: NexusPresenceIntent | null;

  decision: NexusPresenceDecision | null;

  objective: NexusPresenceObjective | null;

  plan: NexusPresencePlan | null;

  execution: NexusPresenceExecution | null;

  verification: NexusPresenceVerification | null;

  memory: NexusPresenceMemory | null;

  learning: NexusPresenceLearning | null;

  events: NexusPresenceEvent[];
}