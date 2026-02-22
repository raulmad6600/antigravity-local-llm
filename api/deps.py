from core.llm.ollama_adapter import OllamaAdapter
from core.orchestrator.engine import Orchestrator
from .config import settings
from typing import Optional

# Singleton instances
_orchestrator: Optional[Orchestrator] = None
_llm: Optional[OllamaAdapter] = None


def get_llm() -> OllamaAdapter:
    """Get or create the LLM adapter singleton."""
    global _llm
    if _llm is None:
        _llm = OllamaAdapter(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url
        )
    return _llm


def get_orchestrator() -> Orchestrator:
    """Get or create the Orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        llm = get_llm()
        _orchestrator = Orchestrator(llm)
    return _orchestrator


def reset_singletons() -> None:
    """Reset singleton instances (useful for testing)."""
    global _orchestrator, _llm
    _orchestrator = None
    _llm = None
