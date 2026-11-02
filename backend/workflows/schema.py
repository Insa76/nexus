from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any


ALLOWED_ACTIONS = {
    "open_app",
    "open_url",
    "list_dir",
    "read_file",
    "write_file",
    "delete_file",
    "copy_file",
    "rename_file",
    "create_folder",
    "move_files",
    "list_processes",
    "kill_process",
    "get_time",
    "run_cmd",
    "sleep"
}


class StepModel(BaseModel):
    action: str
    value: Optional[Any] = None

    @validator("action")
    def validate_action(cls, v):
        if v not in ALLOWED_ACTIONS:
            raise ValueError(f"Acción no permitida: {v}")
        return v


class WorkflowModel(BaseModel):
    name: str
    trigger: str = Field(default="manual")
    fail_fast: bool = Field(default=False)  # 🔥 NUEVO
    steps: List[StepModel]

    @validator("steps")
    def validate_steps_not_empty(cls, v):
        if not v:
            raise ValueError("Workflow sin pasos")
        return v