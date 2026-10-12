from planner.episode_query_resolver import (
    EpisodeQueryResolver,
)


def check(
    condition: bool,
    message: str,
) -> None:

    if not condition:
        raise AssertionError(message)


def main() -> None:

    resolver = EpisodeQueryResolver()

    #
    # CLOSE APP
    #

    query = resolver.resolve(
        "qué aplicación cerré"
    )

    check(
        query is not None,
        "No resolvió la consulta de cierre.",
    )

    check(
        query.action == "system.close_app",
        "La acción debería ser system.close_app.",
    )

    check(
        query.field == "application",
        "El campo debería ser application.",
    )

    #
    # OPEN APP
    #

    query = resolver.resolve(
        "qué aplicación abrí"
    )

    check(
        query is not None,
        "No resolvió la consulta de apertura.",
    )

    check(
        query.action == "system.open_app",
        "La acción debería ser system.open_app.",
    )

    check(
        query.field == "application",
        "El campo debería ser application.",
    )

    #
    # VOLUME
    #

    query = resolver.resolve(
        "qué volumen puse"
    )

    check(
        query is not None,
        "No resolvió la consulta de volumen.",
    )

    check(
        query.action == "system.set_volume",
        "La acción debería ser system.set_volume.",
    )

    check(
        query.field == "level",
        "El campo debería ser level.",
    )

    #
    # CAPTURE
    #

    query = resolver.resolve(
        "qué capturé"
    )

    check(
        query is not None,
        "No resolvió la consulta de captura.",
    )

    check(
        query.action == "system.screen_capture",
        "La acción debería ser system.screen_capture.",
    )

    check(
        query.field == "status",
        "El campo debería ser status.",
    )

    #
    # UNKNOWN
    #

    query = resolver.resolve(
        "qué desayuné"
    )

    check(
        query is None,
        "Una consulta desconocida no debería resolverse.",
    )

    print("=" * 72)
    print("EPISODE QUERY RESOLVER")
    print("=" * 72)
    print("PASSED : 5")
    print("FAILED : 0")
    print("=" * 72)


if __name__ == "__main__":
    main()
