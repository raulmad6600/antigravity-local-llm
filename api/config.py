from pydantic_settings import BaseSettings
from pathlib import Path
from pydantic import Field


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
    log_level: str = "INFO"
    ollama_model: str = Field(default="llama3", alias="OLLAMA_MODEL")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    max_iterations: int = 3
    api_host: str = Field(default="0.0.0.0", alias="HOST")
    api_port: int = Field(default=8000, alias="PORT")
    
    # Aliases for backward compatibility
    @property
    def host(self) -> str:
        return self.api_host
    
    @property
    def port(self) -> int:
        return self.api_port

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
