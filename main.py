import sys
from loguru import logger
from domain import Spell, Grimoire, SpellType, Enemy
from domain.battle.battle import Battle
from domain.entities.character import Character


def setup_logging() -> None:
    """Настройка логирования"""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<level>{level: <8}</level> | {message}",
        level="INFO"
    )


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

    # Бой!
    battle = Battle(player, enemy, grimoire)
    battle.run()


if __name__ == "__main__":
    main()
