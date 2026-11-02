from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SemanticMemory(BaseModel):
    user_id: str
    key: str
    value: str
    confidence: float = 0.5
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()