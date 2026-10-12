from __future__ import annotations

import ctypes
import ctypes.wintypes

import psutil


class WindowsProcessManager:

    def list(self) -> list[dict]:

        visible_pids: set[int] = set()

        user32 = ctypes.windll.user32

        enum_windows = user32.EnumWindows
        get_window_thread_process_id = (
            user32.GetWindowThreadProcessId
        )
        is_window_visible = user32.IsWindowVisible

        EnumWindowsProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool,
            ctypes.wintypes.HWND,
            ctypes.wintypes.LPARAM,
        )

        @EnumWindowsProc
        def callback(hwnd, lparam):

            if is_window_visible(hwnd):

                pid = ctypes.wintypes.DWORD()

                get_window_thread_process_id(
                    hwnd,
                    ctypes.byref(pid),
                )

                if pid.value:
                    visible_pids.add(
                        pid.value
                    )

            return True

        enum_windows(
            callback,
            0,
        )

        #
        # Procesos que tienen una ventana visible.
        #

        processes = []

        for process in psutil.process_iter(
            ["pid", "name"]
        ):

            try:

                info = process.info

                if info["pid"] not in visible_pids:
                    continue

                name = info.get("name")

                if not name:
                    continue

                processes.append(info)

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
            ):

                continue

            except Exception:

                continue

        #
        # Nombres amigables.
        #

        friendly_names = {
            "chrome.exe": "Google Chrome",
            "code.exe": "Visual Studio Code",
            "msedge.exe": "Microsoft Edge",
            "explorer.exe": "Explorador de archivos",
            "winword.exe": "Microsoft Word",
            "excel.exe": "Microsoft Excel",
            "powerpnt.exe": "Microsoft PowerPoint",
            "notepad.exe": "Bloc de notas",
        }

        #
        # Componentes que no queremos mostrar
        # como aplicaciones abiertas.
        #

        ignored = {
            "textinputhost.exe",
        }

        #
        # Eliminamos duplicados por nombre.
        #

        unique = {}

        for process in processes:

            name = process.get("name")

            if not name:
                continue

            key = name.lower()

            if key in ignored:
                continue

            display_name = friendly_names.get(
                key,
                name.removesuffix(".exe"),
            )

            unique[key] = {
                "name": display_name,
                "pid": process["pid"],
            }

        return sorted(
            unique.values(),
            key=lambda p: p["name"].lower(),
        )

    def close(
        self,
        application: str,
    ) -> bool:

        application = application.strip().lower()

        #
        # Alias de aplicaciones.
        #
        # El valor representa el nombre real del proceso
        # o una familia de nombres de proceso.
        #

        aliases = {
            "chrome": {
                "chrome.exe",
                "chrome",
            },
            "google chrome": {
                "chrome.exe",
                "chrome",
            },
            "code": {
                "code.exe",
                "code",
            },
            "visual studio code": {
                "code.exe",
                "code",
            },
            "vs code": {
                "code.exe",
                "code",
            },
            "edge": {
                "msedge.exe",
                "msedge",
            },
            "microsoft edge": {
                "msedge.exe",
                "msedge",
            },
            "explorer": {
                "explorer.exe",
                "explorer",
            },
            "explorador de archivos": {
                "explorer.exe",
                "explorer",
            },
            "word": {
                "winword.exe",
                "winword",
            },
            "microsoft word": {
                "winword.exe",
                "winword",
            },
            "excel": {
                "excel.exe",
                "excel",
            },
            "microsoft excel": {
                "excel.exe",
                "excel",
            },
            "powerpoint": {
                "powerpnt.exe",
                "powerpnt",
            },
            "microsoft powerpoint": {
                "powerpnt.exe",
                "powerpnt",
            },
            "notepad": {
                "notepad.exe",
                "notepad",
            },
            "bloc de notas": {
                "notepad.exe",
                "notepad",
            },
        }

        target_names = aliases.get(
            application,
            {
                application,
                f"{application}.exe",
            },
        )

        #
        # No dependemos de list() para cerrar.
        #
        # Esto es importante porque list() representa únicamente
        # procesos con ventanas visibles. Una aplicación puede
        # estar ejecutándose mientras Windows todavía no expone
        # su ventana en EnumWindows.
        #

        for process in psutil.process_iter(
            ["pid", "name"]
        ):

            try:

                name = process.info.get("name")

                if not name:
                    continue

                normalized_name = name.lower()

                if normalized_name not in target_names:
                    continue

                process.terminate()

                try:
                    process.wait(timeout=3)

                except psutil.TimeoutExpired:

                    #
                    # Intentamos una terminación forzada.
                    #

                    try:
                        process.kill()
                        process.wait(timeout=2)
                    except (
                        psutil.NoSuchProcess,
                        psutil.AccessDenied,
                        psutil.TimeoutExpired,
                    ):
                        return False

                return True

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
            ):
                continue

            except Exception:
                continue

        return False
