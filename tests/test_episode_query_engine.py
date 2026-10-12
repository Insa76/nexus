from memory.working_memory import WorkingMemory
from memory.episode import Episode
from memory.episode_memory import EpisodeMemory
from memory.episode_query_engine import (
    EpisodeQueryEngine,
)


def test_find_last_by_action():

    memory = WorkingMemory()

    episodes = EpisodeMemory(
        memory
    )

    episodes.add(
        Episode(
            action="system.open_app",
            original_text="abrí chrome",
            parameters={
                "application": "chrome"
            },
            output={},
            success=True,
        )
    )

    episodes.add(
        Episode(
            action="system.close_app",
            original_text="cerré chrome",
            parameters={
                "application": "chrome"
            },
            output={},
            success=True,
        )
    )

    query = EpisodeQueryEngine(
        episodes
    )

    result = query.find_last_by_action(
        "system.close_app"
    )

    assert result is not None
    assert result.action == "system.close_app"
