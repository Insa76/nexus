
from __future__ import annotations

import json
import os
import queue
import shutil
import sys
import tempfile
import threading
import time
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath


MODEL_NAME = "vosk-model-small-es-0.42"
MODEL_URL = (
    "https://alphacephei.com/vosk/models/"
    "vosk-model-small-es-0.42.zip"
)
SAMPLE_RATE = 16000
MAX_MODEL_DOWNLOAD = 120 * 1024 * 1024

stop_event = threading.Event()


def emit(event: dict) -> None:
    print(
        json.dumps(event, ensure_ascii=False),
        flush=True,
    )


def get_model_path() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")

    if local_app_data:
        base = Path(local_app_data)
    else:
        base = Path.home() / "AppData" / "Local"

    configured = os.environ.get("NEXUS_VOSK_MODEL_DIR")

    if configured:
        return Path(configured)

    return base / "NEXUS" / "models" / MODEL_NAME


def model_is_valid(path: Path) -> bool:
    return (
        path.is_dir()
        and (path / "am" / "final.mdl").is_file()
        and (path / "conf" / "model.conf").is_file()
        and (path / "graph" / "HCLG.fst").is_file()
    )


def download_model(destination: Path) -> None:
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    emit({
        "type": "status",
        "state": "downloading_model",
        "message": "Descargando el modelo local de español...",
    })

    temporary_root = Path(
        tempfile.mkdtemp(prefix="nexus-vosk-")
    )

    archive_path = temporary_root / "model.zip"
    extract_path = temporary_root / "extracted"

    extract_path.mkdir(parents=True, exist_ok=True)

    try:
        request = urllib.request.Request(
            MODEL_URL,
            headers={
                "User-Agent": "NEXUS-Local-Assistant/1.0",
            },
        )

        downloaded = 0

        with urllib.request.urlopen(
            request,
            timeout=60,
        ) as response:
            with archive_path.open("wb") as archive_file:
                while True:
                    chunk = response.read(1024 * 1024)

                    if not chunk:
                        break

                    downloaded += len(chunk)

                    if downloaded > MAX_MODEL_DOWNLOAD:
                        raise RuntimeError(
                            "El archivo del modelo supera "
                            "el límite de descarga permitido."
                        )

                    archive_file.write(chunk)

        emit({
            "type": "status",
            "state": "installing_model",
            "message": "Preparando el modelo de reconocimiento...",
        })

        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.infolist():
                member_path = PurePosixPath(member.filename)

                if member_path.is_absolute() or ".." in member_path.parts:
                    raise RuntimeError(
                        "El archivo del modelo contiene una ruta inválida."
                    )

                target = (
                    extract_path / Path(*member_path.parts)
                ).resolve()

                if (
                    target != extract_path.resolve()
                    and extract_path.resolve() not in target.parents
                ):
                    raise RuntimeError(
                        "Se rechazó una ruta insegura del archivo."
                    )

            archive.extractall(extract_path)

        extracted_model = extract_path / MODEL_NAME

        if not model_is_valid(extracted_model):
            raise RuntimeError(
                "El modelo descargado no tiene la estructura esperada."
            )

        if destination.exists():
            shutil.rmtree(destination)

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.move(
            str(extracted_model),
            str(destination),
        )

        if not model_is_valid(destination):
            raise RuntimeError(
                "No se pudo verificar la instalación del modelo."
            )

    finally:
        shutil.rmtree(
            temporary_root,
            ignore_errors=True,
        )


def load_model():
    from vosk import Model, SetLogLevel

    SetLogLevel(-1)

    model_path = get_model_path()

    if not model_is_valid(model_path):
        download_model(model_path)

    emit({
        "type": "status",
        "state": "loading_model",
        "message": "Cargando reconocimiento de voz local...",
    })

    return Model(str(model_path))


def read_stop_command() -> None:
    """
    Recibe órdenes desde Electron por stdin.
    """

    try:
        for line in sys.stdin:
            if line.strip().lower() in {
                "stop",
                "salir",
                "exit",
            }:
                stop_event.set()
                return
    except Exception:
        stop_event.set()


def transcribe(model) -> None:
    import sounddevice as sd
    from vosk import KaldiRecognizer

    audio_queue: queue.Queue[bytes] = queue.Queue(
        maxsize=64
    )

    recognizer = KaldiRecognizer(
        model,
        SAMPLE_RATE,
    )

    recognizer.SetWords(False)

    final_parts: list[str] = []
    last_partial = ""

    def audio_callback(
        indata,
        frames,
        time_info,
        status,
    ) -> None:
        try:
            audio_queue.put_nowait(bytes(indata))
        except queue.Full:
            # No bloquear el callback de audio.
            pass

    command_thread = threading.Thread(
        target=read_stop_command,
        name="nexus-voice-command",
        daemon=True,
    )

    command_thread.start()

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=audio_callback,
    ):
        emit({
            "type": "status",
            "state": "listening",
            "message": "NEXUS está escuchando...",
        })

        while not stop_event.is_set():
            try:
                audio_data = audio_queue.get(
                    timeout=0.25
                )
            except queue.Empty:
                continue

            if recognizer.AcceptWaveform(audio_data):
                result = json.loads(
                    recognizer.Result()
                )

                recognized = result.get("text", "").strip()

                if recognized:
                    final_parts.append(recognized)
                    last_partial = ""

            else:
                result = json.loads(
                    recognizer.PartialResult()
                )

                partial = result.get("partial", "").strip()

                if partial != last_partial:
                    last_partial = partial

                    complete_text = " ".join(
                        final_parts + ([partial] if partial else [])
                    ).strip()

                    emit({
                        "type": "partial",
                        "text": complete_text,
                    })

    emit({
        "type": "status",
        "state": "finalizing",
        "message": "Finalizando la transcripción...",
    })

    final_result = json.loads(
        recognizer.FinalResult()
    )

    final_text = final_result.get("text", "").strip()

    if final_text:
        final_parts.append(final_text)

    transcript = " ".join(final_parts).strip()

    emit({
        "type": "final",
        "text": transcript,
    })


def main() -> int:
    stop_event.clear()

    try:
        emit({
            "type": "status",
            "state": "loading_model",
            "message": "Iniciando reconocimiento local...",
        })

        model = load_model()

        if stop_event.is_set():
            emit({
                "type": "final",
                "text": "",
            })
            return 0

        transcribe(model)

        return 0

    except Exception as exc:
        emit({
            "type": "error",
            "message": str(exc),
        })

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
