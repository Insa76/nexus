from typing import Any


TYPE_MAP = {
    "string": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict
}


def validate_type(value: Any, declared_type: str):

    if not declared_type:
        return True

    py_type = TYPE_MAP.get(declared_type)

    if not py_type:
        return True  # tipo desconocido → no bloquea

    return isinstance(value, py_type)