from pydantic import BaseModel
from typing import Optional

class AIRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None