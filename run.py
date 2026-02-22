#!/usr/bin/env python
"""
Entry point for running the Antigravity Local LLM API server.

Usage:
    python run.py
    
The server will start on the configured HOST:PORT (default: 0.0.0.0:8000)
with hot-reload enabled in debug mode.
"""
import uvicorn
import logging
from api.config import settings

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Server will bind to {settings.host}:{settings.port}")
    logger.info(f"Ollama endpoint: {settings.ollama_base_url}")
    logger.info(f"Model: {settings.ollama_model}")
    
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
