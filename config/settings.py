import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Максимальные и минимальные значения характеристик игрока
    MAX_MANA: int = 100
    MAX_HP: int = 100
    MIN_MANA: int = 0
    MIN_HP: int = 0
    # Секреты
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
    # Максимальные отклонения урона/хила генерируемые LLM
    MAX_HP_DELTA = 10
    MAX_MANA_DELTA = 10

# Создаем экземпляр для импорта
settings = Settings()