from abc import ABC, abstractmethod
from core.models import AgentContext, AgentResult


class BaseAgent(ABC):
    name: str

    def __init__(self, llm):
        self.llm = llm

    @abstractmethod
    async def run(self, context: AgentContext) -> AgentResult:
        pass