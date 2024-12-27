from pydantic_settings import BaseSettings
from pathlib import Path

# Получаем путь к файлу .env, который находится в директории выше
ENV_PATH = Path(__file__).parent.parent / ".env"


class Config(BaseSettings):
    BOT_TOKEN: str = "YOUR TOKEN FROM @BOTFATHER"
    DATABASE_URL: str = "postgresql://ctf:ctf@localhost:5432/ctf"
    ADMIN_NICKNAMES: str = "tgadminnick1,tgadminnick2"

    class Config:
        env_file = ENV_PATH
        extra = "allow"  # Разрешить дополнительные параметры

# Instantiate the config
config = Config()

if __name__ == "__main__":
    print(f'Config as a dict:\n{config.__dict__}')
    print(config.ADMIN_NICKNAMES.split())