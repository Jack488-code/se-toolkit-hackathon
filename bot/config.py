from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str = ""
    API_URL: str = "http://backend:8000/api"
    DEBUG: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
