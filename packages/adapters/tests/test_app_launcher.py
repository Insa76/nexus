
from unittest.mock import Mock, patch

import pytest

from adapters.windows.app_launcher import WindowsAppLauncher


@pytest.mark.parametrize(
    "executable",
    [
        "notepad",
        "spotify",
        "calc",
        "mspaint",
    ],
)
def test_launch_starts_process_and_waiter(executable):
    process = Mock()

    with (
        patch(
            "adapters.windows.app_launcher.subprocess.Popen",
            return_value=process,
        ) as popen,
        patch(
            "adapters.windows.app_launcher.threading.Thread",
        ) as thread,
    ):
        assert WindowsAppLauncher._launch(executable) is True

    popen.assert_called_once_with(executable)
    thread.assert_called_once_with(
        target=process.wait,
        daemon=True,
    )
    thread.return_value.start.assert_called_once_with()


def test_launch_absolute_path():
    executable = r"C:\Apps\chrome.exe"
    process = Mock()

    with (
        patch(
            "adapters.windows.app_launcher.os.path.exists",
            return_value=True,
        ),
        patch(
            "adapters.windows.app_launcher.subprocess.Popen",
            return_value=process,
        ) as popen,
        patch(
            "adapters.windows.app_launcher.threading.Thread",
        ) as thread,
    ):
        assert WindowsAppLauncher._launch(executable) is True

    popen.assert_called_once_with([executable])
    thread.assert_called_once_with(
        target=process.wait,
        daemon=True,
    )
    thread.return_value.start.assert_called_once_with()


def test_launch_returns_false_when_process_creation_fails():
    with (
        patch(
            "adapters.windows.app_launcher.subprocess.Popen",
            side_effect=OSError("No se pudo iniciar"),
        ),
        patch(
            "adapters.windows.app_launcher.threading.Thread",
        ) as thread,
    ):
        assert WindowsAppLauncher._launch("notepad") is False

    thread.assert_not_called()


def test_launch_returns_false_when_absolute_path_does_not_exist():
    executable = r"C:\Apps\chrome.exe"

    with (
        patch(
            "adapters.windows.app_launcher.os.path.exists",
            return_value=False,
        ),
        patch(
            "adapters.windows.app_launcher.subprocess.Popen",
        ) as popen,
        patch(
            "adapters.windows.app_launcher.threading.Thread",
        ) as thread,
    ):
        assert WindowsAppLauncher._launch(executable) is False

    popen.assert_not_called()
    thread.assert_not_called()
