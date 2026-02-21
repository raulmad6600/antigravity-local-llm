from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any


class Task(BaseModel):
    prompt: str
    metadata: Optional[Dict[str, Any]] = None


class AgentContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    task: Task
    memory: Optional[Dict[str, Any]] = None
    intermediate: Optional[Dict[str, Any]] = None


class AgentResult(BaseModel):
    output: str
    status: str  # "PASS" | "FAIL" | "CONTINUE"
    metadata: Optional[Dict[str, Any]] = None