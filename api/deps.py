from core.llm.ollama_adapter import OllamaAdapter
from core.orchestrator.engine import Orchestrator
from .config import settings


def get_orchestrator():
    llm = OllamaAdapter(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url
    )
    return Orchestrator(llm)