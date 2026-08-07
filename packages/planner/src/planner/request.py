from __future__ import annotations

from pydantic import BaseModel


class Request(BaseModel):
    """
    Solicitud original realizada por el usuario.
    """

    text: str