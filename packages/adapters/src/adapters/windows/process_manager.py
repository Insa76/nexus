from __future__ import annotations

import psutil


class WindowsProcessManager:

    def list(self) -> list[dict]:

        processes = []

        for process in psutil.process_iter(

            ["pid", "name"]

        ):

            try:

                processes.append(process.info)

            except Exception:

                continue

        return sorted(

            processes,

            key=lambda p: p["name"] or "",

        )

    def close(
        self,
        application: str,
    ) -> bool:

        application = application.lower()

        for process in psutil.process_iter(

            ["name"]

        ):

            try:

                name = process.info["name"]

                if not name:
                    continue

                if application in name.lower():

                    process.terminate()

                    return True

            except Exception:

                continue

        return False