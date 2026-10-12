
from __future__ import annotations

from pycaw.utils import AudioUtilities


class WindowsVolumeControl:
    """
    Controla el volumen maestro de Windows.

    Conserva el dispositivo de audio y reutiliza su
    interfaz EndpointVolume.
    """

    def __init__(self) -> None:
        self._device = None
        self._volume = None

    def _get_volume_interface(self):
        """Obtiene y reutiliza la interfaz del dispositivo."""

        if self._volume is not None:
            return self._volume

        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume

        # Conservar ambas referencias COM durante su uso.
        self._device = device
        self._volume = volume

        return self._volume

    def _reset_interface(self) -> None:
        """Permite resolver nuevamente el dispositivo."""

        self._volume = None
        self._device = None

    def get(self) -> float:
        """Devuelve el volumen actual como porcentaje."""

        volume = self._get_volume_interface()

        try:
            level = volume.GetMasterVolumeLevelScalar()
        except Exception:
            self._reset_interface()
            volume = self._get_volume_interface()
            level = volume.GetMasterVolumeLevelScalar()

        return round(float(level) * 100, 1)

    def set(self, level: float) -> float:
        """Establece el volumen maestro entre 0 y 100."""

        level = max(0.0, min(100.0, float(level)))
        volume = self._get_volume_interface()

        try:
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        except Exception:
            self._reset_interface()
            volume = self._get_volume_interface()
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)

        return round(level, 1)

    def mute(self) -> None:
        """Silencia Windows."""

        volume = self._get_volume_interface()

        try:
            volume.SetMute(1, None)
        except Exception:
            self._reset_interface()
            volume = self._get_volume_interface()
            volume.SetMute(1, None)

    def unmute(self) -> None:
        """Quita el silencio de Windows."""

        volume = self._get_volume_interface()

        try:
            volume.SetMute(0, None)
        except Exception:
            self._reset_interface()
            volume = self._get_volume_interface()
            volume.SetMute(0, None)

    def is_muted(self) -> bool:
        """Indica si Windows está silenciado."""

        volume = self._get_volume_interface()

        try:
            muted = volume.GetMute()
        except Exception:
            self._reset_interface()
            volume = self._get_volume_interface()
            muted = volume.GetMute()

        return bool(muted)
