from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str | None = None
    db_url: str = "sqlite:///insuretech.sqlite3"
    env: str = "local"

settings = Settings()
