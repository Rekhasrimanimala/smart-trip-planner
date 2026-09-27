from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


class Settings(BaseSettings):
    tavily_api_key: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    chroma_path: str = str(ROOT_DIR / "backend" / "rag" / "chroma_db")
    mcp_transport: str = "stdio"

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
