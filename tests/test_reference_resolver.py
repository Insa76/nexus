from planner.reference_resolver import ReferenceResolver


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:

    resolver = ReferenceResolver()

    context = {
        "references": {
            "last_action": "system.open_app",
            "last_application": "chrome",
            "last_executed_application": "chrome",
            "last_volume": 50,
            "previous_volume": 30,
            "last_capture_available": True,
        }
    }

    #
    # APPLICATION
    #

    reference = resolver.resolve(
        "esa aplicación",
        context,
    )

    check(
        reference is not None,
        "No resolvió la aplicación contextual.",
    )

    check(
        reference.kind == "application",
        "La referencia debería ser de tipo application.",
    )

    check(
        reference.value == "chrome",
        "La aplicación contextual debería ser chrome.",
    )

    #
    # CAPTURE
    #

    reference = resolver.resolve(
        "esa captura",
        context,
    )

    check(
        reference is not None,
        "No resolvió la captura contextual.",
    )

    check(
        reference.kind == "capture",
        "La referencia debería ser de tipo capture.",
    )

    #
    # VOLUME
    #

    reference = resolver.resolve(
        "el volumen",
        context,
    )

    check(
        reference is not None,
        "No resolvió el volumen contextual.",
    )

    check(
        reference.kind == "volume",
        "La referencia debería ser de tipo volume.",
    )

    check(
        reference.value == 50.0,
        "El volumen contextual debería ser 50.",
    )

    #
    # PREVIOUS ACTION
    #

    reference = resolver.resolve(
        "eso",
        context,
    )

    check(
        reference is not None,
        "No resolvió la acción contextual.",
    )

    check(
        reference.kind == "action",
        "La referencia debería ser de tipo action.",
    )

    check(
        reference.value == "system.open_app",
        "La acción contextual debería ser system.open_app.",
    )

    #
    # SAFETY: NO CONTEXT
    #

    reference = resolver.resolve(
        "esa aplicación",
        {},
    )

    check(
        reference is None,
        "No debería resolver sin contexto.",
    )

    #
    # SAFETY: CAPTURE UNAVAILABLE
    #

    context_without_capture = {
        "references": {
            "last_capture_available": False,
        }
    }

    reference = resolver.resolve(
        "esa captura",
        context_without_capture,
    )

    check(
        reference is None,
        "No debería resolver una captura inexistente.",
    )

    #
    # SAFETY: UNKNOWN REFERENCE
    #

    reference = resolver.resolve(
        "algo completamente distinto",
        context,
    )

    check(
        reference is None,
        "Una expresión desconocida no debería resolverse.",
    )

    print("=" * 72)
    print("REFERENCE RESOLVER")
    print("=" * 72)
    print("PASSED : 7")
    print("FAILED : 0")
    print("=" * 72)


if __name__ == "__main__":
    main()
