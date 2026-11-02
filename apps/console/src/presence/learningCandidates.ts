export type StoredLearningCandidate = {
  id: string;
  insightId: string;
  title: string;
  knowledge: string;
  sourceCycleIds: string[];
  evidenceKeys: string[];
  createdAt: string;
  status?: "staged" | "promoted";
  promotedAt?: string;
  memoryKey?: string;
};

const STORAGE_KEY = "nexus.learning-candidates.v1";

function isCandidate(value: unknown): value is StoredLearningCandidate {
  if (!value || typeof value !== "object") {
    return false;
  }

  const candidate = value as Record<string, unknown>;

  return (
    (typeof candidate.id === "string" || candidate.id === undefined) &&
    typeof candidate.insightId === "string" &&
    typeof candidate.title === "string" &&
    typeof candidate.knowledge === "string" &&
    Array.isArray(candidate.sourceCycleIds) &&
    candidate.sourceCycleIds.every((item) => typeof item === "string") &&
    Array.isArray(candidate.evidenceKeys) &&
    candidate.evidenceKeys.every((item) => typeof item === "string") &&
    typeof candidate.createdAt === "string"
  );
}

export function loadLearningCandidates(): StoredLearningCandidate[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);

    if (!raw) {
      return [];
    }

    const parsed: unknown = JSON.parse(raw);

    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed.filter(isCandidate).map((candidate) => ({
      ...candidate,
      id:
        typeof candidate.id === "string"
          ? candidate.id
          : `insight-${candidate.insightId}-${candidate.sourceCycleIds.slice().sort().join("--")}`,
      status: candidate.status ?? "staged",
    }));
  } catch {
    return [];
  }
}

function persist(candidates: StoredLearningCandidate[]): void {
  try {
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(candidates),
    );
  } catch {
    // Local storage is an optional UI persistence layer.
  }
}

export function saveLearningCandidate(
  candidate: StoredLearningCandidate,
): void {
  const current = loadLearningCandidates();

  const exists = current.some(
    (item) =>
      item.insightId === candidate.insightId &&
      item.sourceCycleIds.length === candidate.sourceCycleIds.length &&
      item.sourceCycleIds.every((id) => candidate.sourceCycleIds.includes(id)),
  );

  if (exists) {
    return;
  }

  persist([candidate, ...current]);
}

export function updateLearningCandidate(
  candidate: StoredLearningCandidate,
): void {
  const current = loadLearningCandidates();
  const index = current.findIndex((item) => item.id === candidate.id);

  if (index === -1) {
    return;
  }

  current[index] = candidate;
  persist(current);
}

export function removeLearningCandidate(
  candidate: StoredLearningCandidate,
): void {
  const current = loadLearningCandidates();

  persist(
    current.filter(
      (item) =>
        !(
          item.insightId === candidate.insightId &&
          item.createdAt === candidate.createdAt &&
          item.sourceCycleIds.length === candidate.sourceCycleIds.length &&
          item.sourceCycleIds.every((id) => candidate.sourceCycleIds.includes(id))
        ),
    ),
  );
}
