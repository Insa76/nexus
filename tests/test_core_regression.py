from __future__ import annotations

import asyncio
import sys
import traceback
from pathlib import Path
import pytest


# ---------------------------------------------------------------------------
# Bootstrap del proyecto
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from bootstrap.bootstrap import build_engine

# ---------------------------------------------------------------------------
# Fixture de regresión
# ---------------------------------------------------------------------------

@pytest.fixture
def engine():
    return build_engine()



# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

class RegressionFailure(Exception):
    pass


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RegressionFailure(message)


def output_of(result):
    output = result.output
    if output is None:
        return {}
    return output


async def execute(engine, text: str):
    return await engine.execute(text)


# ---------------------------------------------------------------------------
# Pruebas
# ---------------------------------------------------------------------------

async def test_open_app(engine):
    print("[1/13] Acción simple: abrir aplicación")

    result = await execute(engine, "abrí notepad")

    check(
        result.success,
        f"Falló abrir aplicación: {result.message}",
    )

    output = output_of(result)

    check(
        isinstance(output, dict),
        "El output de abrir aplicación no es un diccionario.",
    )

    check(
        output.get("status") == "opened",
        f"La aplicación no quedó marcada como abierta: {output}",
    )

    check(
        output.get("application") == "notepad",
        f"Aplicación inesperada en output: {output}",
    )

    print("      OK")


async def test_close_app(engine):
    print("[2/13] Acción simple: cerrar aplicación")

    result = await execute(engine, "cerrá notepad")

    check(
        result.success,
        f"Falló cerrar aplicación: {result.message}",
    )

    output = output_of(result)

    check(
        isinstance(output, dict),
        "El output de cerrar aplicación no es un diccionario.",
    )

    print("      OK")


async def test_process_list(engine):
    print("[3/13] Acción simple: listar procesos")

    result = await execute(engine, "mostrame los procesos")

    check(
        result.success,
        f"Falló listar procesos: {result.message}",
    )

    output = output_of(result)

    check(
        isinstance(output, dict),
        "El output de procesos no es un diccionario.",
    )

    print("      OK")


async def test_volume(engine):
    print("[4/13] Acción simple: consultar volumen")

    result = await execute(engine, "decime el volumen actual")

    check(
        result.success,
        f"Falló consultar volumen: {result.message}",
    )

    output = output_of(result)

    check(
        isinstance(output, dict),
        "El output de volumen no es un diccionario.",
    )

    print("      OK")


async def test_mute_state(engine):
    print("[5/13] Acción simple: consultar mute")

    result = await execute(engine, "decime si está silenciado")

    check(
        result.success,
        f"Falló consultar mute: {result.message}",
    )

    output = output_of(result)

    check(
        isinstance(output, dict),
        "El output de mute no es un diccionario.",
    )

    print("      OK")


async def test_screen_capture(engine):
    print("[6/13] Acción simple: captura de pantalla")

    result = await execute(engine, "capturá la pantalla")

    check(
        result.success,
        f"Falló captura de pantalla: {result.message}",
    )

    artifacts = result.artifacts or {}

    check(
        "image" in artifacts,
        "La captura no produjo el artifact 'image'.",
    )

    image = artifacts["image"]

    check(
        image is not None,
        "El artifact 'image' es None.",
    )

    check(
        hasattr(image, "size"),
        "El artifact 'image' no tiene dimensiones.",
    )

    width, height = image.size

    check(
        width > 0,
        "El ancho de la captura es inválido.",
    )

    check(
        height > 0,
        "El alto de la captura es inválido.",
    )

    print(f"      OK ({width} × {height})")


async def test_compound_capture_inspection(engine):
    print("[7/13] Acción compuesta: captura → inspección")

    result = await execute(
        engine,
        "capturá la pantalla e inspeccionala",
    )

    check(
        result.success,
        f"Falló acción compuesta: {result.message}",
    )

    output = output_of(result)

    check(
        output.get("status") == "inspected",
        "La acción compuesta no terminó con status='inspected'.",
    )

    inspection = output.get("capture_inspection")

    check(
        isinstance(inspection, dict),
        "No existe 'capture_inspection' como diccionario.",
    )

    width = inspection.get("width")
    height = inspection.get("height")

    check(
        isinstance(width, int) and width > 0,
        "Ancho de inspección inválido.",
    )

    check(
        isinstance(height, int) and height > 0,
        "Alto de inspección inválido.",
    )

    check(
        "image" in (result.artifacts or {}),
        "La acción compuesta perdió el artifact 'image'.",
    )

    metadata = result.metadata or {}

    response = metadata.get("response")

    check(
        isinstance(response, str),
        "La respuesta humana no está presente en metadata.",
    )

    check(
        "Inspeccioné la pantalla" in response,
        f"ResponseFormatter no produjo la respuesta esperada: {response}",
    )

    print(f"      OK ({width} × {height})")


async def test_recent_episodes(engine):
    print("[8/13] Memoria: episodios recientes")

    # Esta frase coincide explícitamente con IntentRecognizer.
    result = await execute(
        engine,
        "qué hice recientemente",
    )

    check(
        result.success,
        f"Falló recuperación de episodios: {result.message}",
    )

    output = output_of(result)

    check(
        isinstance(output, dict),
        "El output de episodios no es un diccionario.",
    )

    print("      OK")


async def test_last_episode(engine):
    print("[9/13] Memoria: último episodio")

    # Esta frase coincide explícitamente con IntentRecognizer.
    result = await execute(
        engine,
        "qué hice recién",
    )

    check(
        result.success,
        f"Falló recuperación del último episodio: {result.message}",
    )

    output = output_of(result)

    check(
        isinstance(output, dict),
        "El output del último episodio no es un diccionario.",
    )

    print("      OK")


async def test_result_serialization_contract(engine):
    print("[10/13] Contrato: resultado estructurado + respuesta humana")

    result = await execute(
        engine,
        "capturá la pantalla e inspeccionala",
    )

    check(
        result.success,
        f"Falló prueba de contrato: {result.message}",
    )

    output = output_of(result)

    # El resultado estructurado debe permanecer intacto.
    check(
        output.get("status") == "inspected",
        "El resultado estructurado fue alterado.",
    )

    check(
        "capture_inspection" in output,
        "Falta capture_inspection en el resultado.",
    )

    # La presentación humana debe vivir separadamente.
    metadata = result.metadata or {}

    response = metadata.get("response")

    check(
        isinstance(response, str) and response.strip(),
        "No existe respuesta humana válida.",
    )

    # El artifact de imagen debe seguir existiendo.
    artifacts = result.artifacts or {}

    check(
        "image" in artifacts,
        "El artifact image desapareció del resultado.",
    )

    print("      OK")


async def test_memory_growth(engine):
    print("[11/13] Memoria: persistencia entre ejecuciones")

    # WorkingMemory expone count(), no __len__().
    before = engine.memory.count()

    result = await execute(
        engine,
        "decime el volumen actual",
    )

    check(
        result.success,
        f"Falló ejecución para comprobar memoria: {result.message}",
    )

    after = engine.memory.count()

    check(
        after > before,
        (
            "La memoria no aumentó después de una ejecución. "
            f"Antes={before}, después={after}"
        ),
    )

    print(f"      OK ({before} → {after})")


async def test_contextual_volume_reference(engine):
    print("[12/13] Memoria contextual: referencia al volumen")

    """
    Verifica que NEXUS pueda interpretar una referencia
    contextual al volumen a partir de una interacción anterior.
    """

    first = await execute(
        engine,
        "poné el volumen al 30%",
    )

    check(
        first.success,
        "La primera modificación de volumen debería ser exitosa.",
    )

    second = await execute(
        engine,
        "ahora ponelo al 50%",
    )

    check(
        second.success,
        "La referencia contextual al volumen debería resolverse.",
    )

    intent_entries = engine.memory.find("intent")

    check(
        bool(intent_entries),
        "La intención contextual no quedó registrada en memoria.",
    )

    latest_intent = intent_entries[-1].data

    check(
        latest_intent.get("action") == "system.set_volume",
        "La segunda intención debería ser system.set_volume.",
    )

    parameters = latest_intent.get(
        "parameters",
        {},
    )

    check(
        parameters.get("level") == 50,
        "La referencia contextual debería conservar el nivel 50.",
    )

    print("      OK")


async def test_contextual_close_app(engine):
    print("[13/13] Memoria contextual: referencia a aplicación")

    """
    Verifica el flujo completo:

        abrir aplicación
            ↓
        memoria contextual
            ↓
        "cerralo"
            ↓
        system.close_app

    La aplicación se abre dentro de esta misma prueba para que
    la referencia contextual dependa de una interacción real
    inmediatamente anterior.
    """

    opened = await execute(
        engine,
        "abrí notepad",
    )

    check(
        opened.success,
        f"Falló la apertura previa de notepad: {opened.message}",
    )

    opened_output = output_of(opened)

    check(
        opened_output.get("status") == "opened",
        f"Notepad no quedó marcado como abierto: {opened_output}",
    )

    closed = await execute(
        engine,
        "cerralo",
    )

    check(
        closed.success,
        f"Falló el cierre contextual de notepad: {closed.message}",
    )

    closed_output = output_of(closed)

    check(
        isinstance(closed_output, dict),
        "El output del cierre contextual no es un diccionario.",
    )

    intent_entries = engine.memory.find("intent")

    check(
        bool(intent_entries),
        "El cierre contextual no dejó una intención registrada.",
    )

    latest_intent = intent_entries[-1].data

    check(
        latest_intent.get("action") == "system.close_app",
        (
            "La referencia 'cerralo' no se resolvió como "
            "system.close_app."
        ),
    )

    parameters = latest_intent.get(
        "parameters",
        {},
    )

    check(
        parameters.get("application") == "notepad",
        (
            "La referencia contextual no recuperó "
            f"notepad: {parameters}"
        ),
    )

    print("      OK")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

async def run_regression():
    print()
    print("=" * 72)
    print("NEXUS CORE REGRESSION TEST")
    print("=" * 72)
    print()

    engine = build_engine()

    tests = [
        test_open_app,
        test_close_app,
        test_process_list,
        test_volume,
        test_mute_state,
        test_screen_capture,
        test_compound_capture_inspection,
        test_recent_episodes,
        test_last_episode,
        test_result_serialization_contract,
        test_memory_growth,
        test_contextual_volume_reference,
        test_contextual_close_app,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            await test(engine)
            passed += 1

        except Exception as exc:
            failed += 1

            print("      FAILED")
            print(f"      {type(exc).__name__}: {exc}")
            print()

            traceback.print_exc()

    print()
    print("=" * 72)
    print("REGRESSION RESULT")
    print("=" * 72)
    print(f"PASSED : {passed}")
    print(f"FAILED : {failed}")
    print("=" * 72)
    print()

    if failed:
        raise SystemExit(1)

    print("NEXUS CORE REGRESSION: PASS")
    print()


def main():
    asyncio.run(run_regression())


if __name__ == "__main__":
    main()


async def test_process_list(engine):
    print("Regresión: listar procesos de Windows")

    result = await execute(
        engine,
        "Lista los procesos que están ejecutándose actualmente en Windows.",
    )

    check(
        result.success,
        f"Falló listar procesos: {result.message}",
    )

    output = output_of(result)

    check(
        isinstance(output, dict),
        f"El output de procesos no es un diccionario: {output}",
    )

    check(
        output.get("status") == "ok",
        f"La acción de listar procesos no terminó correctamente: {output}",
    )

    check(
        isinstance(output.get("processes"), list),
        f"No se recibió una lista de procesos: {output}",
    )

    check(
        output.get("count") == len(output["processes"]),
        f"El contador no coincide con la lista de procesos: {output}",
    )

    print("      OK")


async def test_unmute_windows(engine):
    print("Regresión: restaurar sonido de Windows")

    result = await execute(
        engine,
        "Activa nuevamente el sonido de Windows.",
    )

    check(
        result.success,
        f"Falló restaurar el sonido: {result.message}",
    )

    output = output_of(result)

    check(
        isinstance(output, dict),
        f"El output de restaurar sonido no es un diccionario: {output}",
    )

    check(
        output.get("status") == "unmuted",
        f"El sonido no quedó activado: {output}",
    )

    check(
        output.get("muted") is False,
        f"Windows continúa silenciado: {output}",
    )

    print("      OK")
