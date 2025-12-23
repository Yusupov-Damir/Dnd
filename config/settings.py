import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Максимальные и минимальные значения характеристик
    MAX_MANA: int = 100
    MAX_HP: int = 100
    MIN_MANA: int = 0
    MIN_HP: int = 0
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# Создаем экземпляр для импорта
settings = Settings()