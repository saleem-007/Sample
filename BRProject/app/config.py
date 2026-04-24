"""Centralised application configuration loaded from environment variables."""

from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Blood Cell Detection API"
    app_version: str = "0.1.0"

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    model_weights_path: Path = BASE_DIR / "models" / "weights" / "best.pt"
    confidence_threshold: float = 0.25
    iou_threshold: float = 0.45
    image_size: int = 640
    device: str = "cpu"

    upload_dir: Path = BASE_DIR / "data" / "samples"
    output_dir: Path = BASE_DIR / "data" / "outputs"
    max_upload_size_mb: int = 10

    cors_origins: list[str] = ["*"]

    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: float = 8.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.output_dir.mkdir(parents=True, exist_ok=True)
