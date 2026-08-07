from __future__ import annotations

import subprocess


class WindowsAppLauncher:
    """
    Abre aplicaciones de Windows.
    """

    _APPLICATIONS = {

        "spotify": "spotify",

        "chrome": "chrome",

        "notepad": "notepad",

        "bloc de notas": "notepad",

        "calculator": "calc",

        "calculadora": "calc",

    }

    def open(
        self,
        application: str,
    ) -> bool:

        executable = self._APPLICATIONS.get(
            application.lower()
        )

        if executable is None:
            return False

        subprocess.Popen(executable)

        return True