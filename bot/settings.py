from pathlib import Path

from pydantic_settings import BaseSettings

# Получаем путь к файлу .env, который находится в директории выше
ENV_PATH = Path(__file__).parent.parent / ".env"


class Config(BaseSettings):
    BOT_TOKEN: str = (
        "8121070643:AAHfGqB0JoE9Pe8MwTCN5jGppY71ZMrFsvQ"  # your tg bot token from botfather
    )
    DATABASE_URL: str = "postgresql://ctf:ctf@localhost:5432/ctf"
    ADMIN_NICKNAMES: str = "tgadminnick1,tgadminnick2"

    SENTRY_DSN: str = "https://1ec97a8cca639cde4c69d8b8597dca04@o4507197457432576.ingest.us.sentry.io/4508985176555520"
    ENV: str = "dev"

    class Config:
        env_file = ENV_PATH
        extra = "allow"  # Разрешить дополнительные параметры


# Instantiate the config
config = Config()

if __name__ == "__main__":
    print(f"Config as a dict:\n{config.__dict__}")
    print(config.ADMIN_NICKNAMES.split())
