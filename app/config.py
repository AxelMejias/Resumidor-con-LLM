from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-20b"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    request_timeout: float = 30.0
    max_text_chars: int = 10_000
    rate_limit_requests: int = 10
    rate_limit_window_seconds: float = 60.0


settings = Settings()
