from pydantic_settings import BaseSettings
from pathlib import Path


# Leer versión desde archivo VERSION
def get_version() -> str:
    try:
        version_file = Path(__file__).parent.parent / "VERSION"
        return version_file.read_text().strip()
    except Exception:
        return "0.0.0-dev"


class Settings(BaseSettings):
    app_name: str = "Antigravity Local LLM"
    app_version: str = get_version()
    debug: bool = True
    ollama_model: str = "llama3"
    ollama_base_url: str = "http://localhost:11434"
    max_iterations: int = 3
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()