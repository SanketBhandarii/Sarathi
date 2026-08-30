from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    model_provider: str = "groq"

    groq_api_key: str = ""
    groq_fast_model: str = "groq/openai/gpt-oss-20b"
    groq_smart_model: str = "groq/openai/gpt-oss-120b"

    bedrock_region: str = "ap-south-1"
    bedrock_fast_model: str = "amazon.nova-lite-v1:0"
    bedrock_smart_model: str = "anthropic.claude-sonnet-4-5-20250929-v1:0"

    database_url: str = ""

    imagekit_private_key: str = ""
    imagekit_public_key: str = ""
    imagekit_url_endpoint: str = ""
    imagekit_folder: str = "/Sarathi"

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""

    session_secret: str = "change-me-in-production"
    session_hours: int = 720

    notification_cache_dir: Path = BACKEND_ROOT / ".." / "data" / "notifications"
    exam_data_dir: Path = BACKEND_ROOT / ".." / "data" / "exams"

    @property
    def notifications_path(self) -> Path:
        return self.notification_cache_dir.resolve()

    @property
    def exams_path(self) -> Path:
        return self.exam_data_dir.resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
