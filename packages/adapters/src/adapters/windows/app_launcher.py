from __future__ import annotations

import os
import subprocess
import time
import threading
import psutil


class WindowsAppLauncher:
    """
    Abre aplicaciones conocidas de Windows y verifica que el proceso
    correspondiente haya quedado disponible antes de informar éxito.

    La resolución de aplicaciones se mantiene explícita para evitar
    ejecutar comandos arbitrarios recibidos desde lenguaje natural.
    """

    _APPLICATIONS = {
        # Browsers
        "chrome": (
            r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        ),

        # Media
        "spotify": "spotify",

        # Windows
        "notepad": "notepad",
        "bloc de notas": "notepad",

        "calculator": "calc",
        "calculadora": "calc",
        "calc": "calc",

        "paint": "mspaint",
        "mspaint": "mspaint",
    }

    _PROCESS_NAMES = {
        "spotify": {
            "spotify.exe",
            "spotify",
        },

        "chrome": {
            "chrome.exe",
            "chrome",
        },

        "notepad": {
            "notepad.exe",
            "notepad",
        },
        "bloc de notas": {
            "notepad.exe",
            "notepad",
        },

        "calculator": {
            "calculatorapp.exe",
            "calculator.exe",
            "calc.exe",
            "calc",
        },
        "calculadora": {
            "calculatorapp.exe",
            "calculator.exe",
            "calc.exe",
            "calc",
        },
        "calc": {
            "calculatorapp.exe",
            "calculator.exe",
            "calc.exe",
            "calc",
        },

        "paint": {
            "mspaint.exe",
            "mspaint",
        },
        "mspaint": {
            "mspaint.exe",
            "mspaint",
        },
    }

    _STARTUP_TIMEOUT = 5.0
    _POLL_INTERVAL = 0.1

    def open(self, application: str) -> bool:
        application = self._normalize_application(application)

        executable = self._APPLICATIONS.get(application)

        if executable is None:
            return False

        if not self._launch(executable):
            return False

        return self._wait_until_available(application)

    @staticmethod
    def _normalize_application(application: str) -> str:
        return application.strip().lower()

    @staticmethod
    def _launch(executable: str) -> bool:
        if os.path.isabs(executable):
            if not os.path.exists(executable):
                return False
            command = [executable]
        else:
            command = executable

        try:
            process = subprocess.Popen(command)
            threading.Thread(
                target=process.wait,
                daemon=True,
            ).start()
            return True
        except OSError:
            return False



    def _wait_until_available(self, application: str) -> bool:
        target_names = self._PROCESS_NAMES.get(application)

        if not target_names:
            return True

        deadline = time.monotonic() + self._STARTUP_TIMEOUT

        while time.monotonic() < deadline:
            if self._process_exists(target_names):
                return True

            time.sleep(self._POLL_INTERVAL)

        return False

    @staticmethod
    def _process_exists(target_names: set[str]) -> bool:
        normalized_targets = {
            name.lower()
            for name in target_names
        }

        for process in psutil.process_iter(["name"]):
            try:
                name = process.info.get("name")

                if not name:
                    continue

                if name.lower() in normalized_targets:
                    return True

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

            except Exception:
                continue

        return False
