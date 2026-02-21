#!/usr/bin/env python3
"""Project verification script - checks imports and configuration"""
import sys

print("✅ Verifying imports...")

# Verify all modules import correctly
from api.config import settings
from api.main import app
from api.routes import router
from api.deps import get_orchestrator

from core.models import Task, AgentContext, AgentResult
from core.agents.base import BaseAgent
from core.agents.planner import PlannerAgent
from core.agents.coder import CoderAgent
from core.agents.reviewer import ReviewerAgent

from core.llm.base import BaseLLM
from core.llm.ollama_adapter import OllamaAdapter

from core.orchestrator.engine import Orchestrator

print("✅ All modules imported successfully!")
print(f"   - App name: {settings.app_name}")
print(f"   - Debug: {settings.debug}")
print(f"   - Ollama URL: {settings.ollama_base_url}")
print(f"   - Ollama Model: {settings.ollama_model}")
print(f"   - API Host: {settings.host}:{settings.port}")

# Verify FastAPI app is configured
print(f"\n✅ FastAPI app configured with {len(app.routes)} routes")
for route in app.routes:
    print(f"   - {route.path} ({route.methods if hasattr(route, 'methods') else 'N/A'})")
