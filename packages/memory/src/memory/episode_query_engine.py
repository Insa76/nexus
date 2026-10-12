from __future__ import annotations

from memory.episode import Episode
from memory.episode_memory import EpisodeMemory


class EpisodeQueryEngine:

    def __init__(
        self,
        episode_memory: EpisodeMemory,
    ) -> None:

        self._episode_memory = episode_memory

    def find_last_by_action(
        self,
        action: str,
    ) -> Episode | None:

        episodes = self._episode_memory.recent(
            limit=100
        )

        for episode in reversed(
            episodes
        ):
            if episode.action == action:
                return episode

        return None
