from pydantic import BaseModel
from typing import List, Optional, Union


class StepModel(BaseModel):
    action: Optional[str] = None
    value: Optional[dict] = None
    type: Optional[str] = "action"

    # condición
    if_action: Optional[str] = None
    operator: Optional[str] = None
    compare: Optional[str] = None

    then: Optional[List[dict]] = None
    else_: Optional[List[dict]] = None


class WorkflowModel(BaseModel):
    name: str
    trigger: str
    steps: List[dict]