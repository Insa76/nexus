import sounddevice as sd
import whisper
import numpy as np
import threading
import time

from brain.agent import ask_nexus
from actions.system_actions import execute_action
from voice.tts import speak


model = whisper.load_model("base")
samplerate = 16000


# -----------------------------
# 🔥 detectar mic dinámicamente
# -----------------------------
def get_input_device():

    try:
        devices = sd.query_devices()

        for i, d in enumerate(devices):
            if d["max_input_channels"] > 0:
                print(f"🎤 Mic detectado: {d['name']} (id {i})")
                return i

    except Exception:
        pass

    return None   # 👈 NUNCA romper backend


# -----------------------------
def record(seconds, device):

    audio = sd.rec(
        int(seconds * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="float32",
        device=device
    )

    sd.wait()
    return audio.flatten()


# -----------------------------
def process(text):

    print("🧠 Usuario:", text)

    result = ask_nexus(text)

    if result.get("action"):
        output = execute_action(result["action"], result.get("value"))
        speak(output)
    else:
        speak(result["response"])


# -----------------------------
def listen_loop():

    device = get_input_device()

    if device is None:
        print("🔇 No hay micrófono válido → voz desactivada")
        return

    print("🎤 Nexus escuchando... decí 'nexus'")

    while True:

        try:

            audio = record(3, device)

            result = model.transcribe(audio, fp16=False)
            text = result["text"].lower().strip()

            if not text:
                continue

            print("Oído:", text)

            if "nexus" in text:

                speak("Sí, te escucho")

                audio = record(5, device)
                result = model.transcribe(audio, fp16=False)

                command = result["text"].strip()

                process(command)

        except Exception as e:
            print("⚠️ Error mic:", e)
            print("🔇 Desactivando voz...")
            return   # 👈 sale del loop sin romper server


# -----------------------------
def start_listener():

    thread = threading.Thread(
        target=listen_loop,
        daemon=True
    )

    thread.start()
