from planner.episode_query_resolver import EpisodeQueryResolver
from memory.episode import Episode
from memory.episode_memory import EpisodeMemory
from memory.working_memory import WorkingMemory


def check(
    condition: bool,
    message: str,
) -> None:

    if not condition:
        raise AssertionError(message)


def main() -> None:

    memory = WorkingMemory()
    episodes = EpisodeMemory(memory)
    resolver = EpisodeQueryResolver()

    #
    # Episodios de prueba
    #

    episodes.add(
        Episode(
            action="system.open_app",
            parameters={
                "application": "chrome",
            },
            original_text="abrí Chrome",
            success=True,
            output={
                "status": "opened",
                "application": "chrome",
            },
        )
    )

    episodes.add(
        Episode(
            action="system.set_volume",
            parameters={
                "level": 30,
            },
            original_text="poné el volumen al 30%",
            success=True,
            output={
                "status": "set",
                "volume": 30,
            },
        )
    )

    episodes.add(
        Episode(
            action="system.close_app",
            parameters={
                "application": "chrome",
            },
            original_text="cerrá Chrome",
            success=True,
            output={
                "status": "closed",
                "application": "chrome",
            },
        )
    )

    #
    # Consulta semántica
    #

    query = resolver.resolve(
        "qué aplicación cerré"
    )

    check(
        query is not None,
        "La consulta debería resolverse.",
    )

    episode = episodes.find_latest_by_action(
        query.action
    )

    check(
        episode is not None,
        "No se encontró el episodio de cierre.",
    )

    application = episodes.find_parameter(
        query.action,
        query.field,
    )

    check(
        application == "chrome",
        "La aplicación recuperada debería ser chrome.",
    )

    #
    # Apertura
    #

    query = resolver.resolve(
        "qué aplicación abrí"
    )

    check(
        query is not None,
        "La consulta de apertura debería resolverse.",
    )

    application = episodes.find_parameter(
        query.action,
        query.field,
    )

    check(
        application == "chrome",
        "La aplicación abierta debería ser chrome.",
    )

    #
    # Volumen
    #

    query = resolver.resolve(
        "qué volumen puse"
    )

    check(
        query is not None,
        "La consulta de volumen debería resolverse.",
    )

    volume = episodes.find_parameter(
        query.action,
        query.field,
    )

    check(
        volume == 30,
        "El volumen recuperado debería ser 30.",
    )

    #
    # Acción inexistente
    #

    result = episodes.find_latest_by_action(
        "system.mute"
    )

    check(
        result is None,
        "No debería encontrar una acción inexistente.",
    )

    #
    # Solo episodios exitosos
    #

    episodes.add(
        Episode(
            action="system.close_app",
            parameters={
                "application": "notepad",
            },
            original_text="cerrá Notepad",
            success=False,
            output={},
        )
    )

    application = episodes.find_parameter(
        "system.close_app",
        "application",
    )

    check(
        application == "chrome",
        "Los episodios fallidos no deben reemplazar "
        "al último episodio exitoso.",
    )

    print("=" * 72)
    print("EPISODE MEMORY")
    print("=" * 72)
    print("PASSED : 6")
    print("FAILED : 0")
    print("=" * 72)


if __name__ == "__main__":
    main()
