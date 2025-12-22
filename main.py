import sys
from loguru import logger
from domain.entities.character import Character
from domain.entities.spell import Spell
from domain.enums.spell_type import SpellType
from domain.entities.grimoire import Grimoire


def setup_logging() -> None:
    """Настройка логирования"""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<level>{level: <8}</level> | {message}",
        level="INFO"
    )


def create_sample_spells() -> list[Spell]:
    """Создание тестовых заклинаний"""
    return [
        Spell("Огненный шар", 30, 3, SpellType.DAMAGE, power=25),
        Spell("Лечение", 20, 2, SpellType.HEAL, power=20),
        Spell("Восстановление маны", 0, 1, SpellType.MANA, power=30)
    ]


def main() -> int:
    """Основная функция приложения"""
    setup_logging()
    logger.info("Инициализация игры...")

    try:
        # Создаем персонажей
        player = Character(max_mana=100, max_hp=100, name="Игрок")
        enemy = Character(max_mana=50, max_hp=80, name="Гоблин")

        # Создаем гримуар и добавляем заклинания
        grimoire = Grimoire(create_sample_spells())
        logger.info("Гримуар создан с заклинаниями:")
        grimoire.show_all_spells()

        # Пример боя
        logger.info("\n=== Начало боя ===")
        fireball = grimoire.get_spell_by_name("Огненный шар")
        if fireball:
            grimoire.cast_spell("Огненный шар", player, enemy)

        heal = grimoire.get_spell_by_name("Лечение")
        if heal:
            grimoire.cast_spell("Лечение", player, player)

        # Выводим статус персонажей
        logger.info("\n=== Статус персонажей ===")
        logger.info(f"Игрок: {player}")
        logger.info(f"Противник: {enemy}")

        return 0

    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
