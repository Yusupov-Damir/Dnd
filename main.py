import sys
import os
from dotenv import load_dotenv
from loguru import logger
from domain import Spell, Grimoire, SpellType, Enemy
from domain.battle.battle import Battle
from domain.entities.character import Character
from services.perplexity_client import PerplexityClient
from services.dm_service import DungeonMasterService

# Загружаем переменные окружения из .env в самом начале
load_dotenv()


def setup_logging() -> None:
    """Настройка логирования"""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<level>{level: <8}</level> | {message}",
        level="INFO"
    )


def init_dm_service() -> DungeonMasterService | None:
    """
    Инициализирует DM сервис если доступен API ключ.

    Returns:
        DungeonMasterService или None если ключ отсутствует
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")

    if not api_key:
        logger.warning("⚠️  PERPLEXITY_API_KEY не установлен. DM отключен.")
        return None

    try:
        client = PerplexityClient()
        dm = DungeonMasterService(client)
        logger.info("✨ Dungeon Master активирован!")
        return dm
    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации DM: {e}")
        return None


def main():
    """Основная функция приложения"""
    setup_logging()
    logger.info("Инициализация игры...")

    # Спеллы
    fireball = Spell("Fireball", 30, 3, SpellType.DAMAGE, 20)
    healing = Spell("Healing", 20, 2, SpellType.HEAL, 25)

    # Гримуар
    grimoire = Grimoire([fireball, healing])

    # Персонажи
    player = Character(60, 100, "Артур")
    enemy = Enemy(50, 80, "Темный маг1", grimoire)

    # Инициализируем DM (опционально)
    dm = init_dm_service()

    # Бой с опциональным DM!
    battle = Battle(player, enemy, grimoire, dm=dm)
    battle.run()


if __name__ == "__main__":
    main()
