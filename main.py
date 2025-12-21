import sys
from enum import Enum

from loguru import logger

# Удалим стандартный вывод логов и настроим свой:
logger.remove()
logger.add(sys.stderr, format="<level>{level: <8}</level> | {message}")

"""
Константы максимальных значений характеристик персонажей
"""
MAX_MANA: int = 100
MAX_HP: int = 100
MIN_MANA: int = 0
MIN_HP: int = 0


class SpellType(Enum):
    """Атрибуты класса Enum нельзя менять или дополнять. Это стабильные константы"""
    DAMAGE = 'take_damage'
    HEAL = 'take_hp'
    MANA = 'take_mana'


class Character:
    def __init__(self, max_mana: int, max_hp: int, name: str):
        self._validate_stats(max_mana, max_hp)

        self.max_hp = max_hp
        self.max_mana = max_mana
        self._current_mana = max_mana
        self._current_hp = max_hp
        self.level: int = 1
        self.experience = 0
        self.name = name

    def __repr__(self) -> str:
        return (
            f'Character(name={self.name!r}, '
            f'hp={self.current_hp}/{self.max_hp}, '
            f'mana={self.current_mana}/{self.max_mana}, '
            f'level={self.level})'
        )

    @staticmethod
    def _validate_stats(max_mana, max_hp):
        if not MIN_MANA <= max_mana <= MAX_MANA:
            raise ValueError(f'Стартовая манна должна быть в диапазоне {MIN_MANA} - {MAX_MANA}')
        if not MIN_HP <= max_hp <= MAX_HP:
            raise ValueError(f'Стартовое здоровье должно быть в диапазоне {MIN_HP} - {MAX_HP}')

    @property
    # @property превращает метод в дескриптор. Теперь он вызывается без "()", и связан с setter
    # Геттер: вызывается, когда мы ЧИТАЕМ (print(hero.current_hp))
    def current_hp(self) -> int:
        return self._current_hp

    @current_hp.setter
    # Сеттер: вызывается, когда мы ПИШЕМ (hero.current_hp = ...)
    def current_hp(self, value):
        # Прием «зажим»/clamping - значение переменной не выйдет за установленные границы (0...max_hp)
        self._current_hp = max(MIN_HP, min(value, self.max_hp))

    @property
    def current_mana(self) -> int:
        return self._current_mana

    @current_mana.setter
    def current_mana(self, value):
        self._current_mana = max(MIN_MANA, min(value, self.max_mana))

    def take_damage(self, damage: int):
        """Получить урон"""
        self.current_hp -= damage
        logger.info(f'Персонаж {self.name} получил урон {damage}, осталось hp: {self.current_hp}')

    def take_hp(self, amount: int):
        """Получить лечение"""
        self.current_hp += amount
        logger.info(f'Персонаж {self.name} получил hp {amount}, осталось hp: {self.current_hp}')

    def take_mana(self, amount: int):
        """Получить ману"""
        self.current_mana += amount
        logger.info(f'Персонаж {self.name} получил ману {amount}, осталось hp: {self.current_mana}')

    def gain_experience(self, exp: int):
        self.experience += exp
        logger.info(f'Персонаж {self.name} получил опыт {exp}, всего опыта: {self.experience}')

    def rest(self):
        self.current_hp = MAX_HP
        self.current_mana = MIN_MANA
        logger.info('Персонаж отдохнул, здоровье и мана восстановлены')

    def get_status(self) -> str:
        return (
            f'Персонаж: {self.name}, '
            f'hp: {self.current_hp}, '
            f'мана: {self.current_mana}, '
            f'уровень: {self.level}, '
            f'опыт: {self.experience},'
        )


class Spell:
    def __init__(self, name: str, mana_cost: int, level: int, spell_type: SpellType, power: int):
        """
        :param power: сила эффекта (урон, восстановление, бонус)
        """
        if not 1 <= level <= 10:
            raise ValueError('Уровень заклинания должен быть в диапазоне 0 - 10')
        self.name = name
        self.mana_cost = mana_cost
        self.level = level
        self.spell_type = spell_type
        self.power = power

    def __str__(self):
        return f'Спелл {self.name}'

    def __repr__(self):
        return f'Spell: (name={self.name}, mana_cost={self.mana_cost}, level={self.level})'

    def cast(self):
        logger.info(f'Каст спелла {self.name} ✨')

    def apply_effect(self, target: Character):
        """Применить эффект спелла к цели"""
        spell_type_object = self.spell_type  # берем из атрибута Spell экземпляр объекта SpellType.attribute_name
        effect_name = spell_type_object.value  # достаем из объекта SpellType.attribute_name значение переменной
        if effect_name:
            method = getattr(target, effect_name)  # получаем obj.attr
            method(self.power)  # вызываем obj.attr()


class Grimoire:
    def __init__(self, init_spell: list[Spell] | Spell | None = None):
        self.spell_list = self._normalize_spells(init_spell)

    @staticmethod
    # Нормализация: привести разные типы входа к единому списку
    def _normalize_spells(input_spells: list[Spell] | Spell | None) -> list[Spell]:
        if input_spells is None:
            return []
        elif isinstance(input_spells, Spell):
            return [input_spells]
        else:
            return input_spells

    def __str__(self):
        return f'Гримуар {self.__class__.__name__}'

    def __repr__(self):
        return f'Grimoire: (spell_list={self.spell_list})'

    def add_spell(self, spell: Spell):
        self.spell_list.append(spell)

    def show_all_spells(self):
        logger.info('Все спеллы гримуара:')
        for spell in self.spell_list:
            logger.info(f'{spell.name}')

    def get_spell_by_name(self, spell_name: str) -> Spell | None:
        """Найти спелл по атрибуту 'имя' """
        for spell in self.spell_list:
            if spell.name == spell_name:
                return spell
        return None

    def cast_spell(self, spell_name: str, character: Character, target: Character) -> None:
        spell = self.get_spell_by_name(spell_name)
        if spell is None:
            raise ValueError(f'Спелл {spell_name} отсутствует в гримуаре!')
        if spell.mana_cost <= character.current_mana:
            logger.info(
                f'Подготовка спелла {spell.name} (сейчас маны:{character.current_mana},'
                f'останется:{character.current_mana - spell.mana_cost})'
            )
            character.current_mana -= spell.mana_cost
            spell.cast()
            spell.apply_effect(target)
            character.gain_experience(10)
            return None
        raise ValueError(f'Текущий остаток маны:{character.current_mana}, стоимость спелла:{spell.mana_cost}')


if __name__ == "__main__":
    # Создай героев
    player = Character(max_mana=100, max_hp=100, name="Артур")

    enemy = Character(max_mana=30, max_hp=20, name="Голем")
    logger.info(enemy.current_hp)

    # Создай спеллы с типами
    fireball = Spell("Fireball", 30, 3, SpellType.DAMAGE, power=15)
    healing = Spell("Healing", 20, 2, SpellType.HEAL, power=20)

    grimoire = Grimoire([fireball, healing])

    # БОЙ!
    logger.info("=== НАЧАЛО БОЕВОГО ПОЕДИНКА ===")

    grimoire.cast_spell("Fireball", player, enemy)  # Артур атакует голема
    grimoire.cast_spell("Healing", player, player)  # Артур лечится
    grimoire.cast_spell("Fireball", player, enemy)  # Артур атакует ещё раз

    logger.info("=== КОНЕЦ ПОЕДИНКА ===")
    logger.info(f"{player.name}: HP={player.current_hp}, Опыт={player.experience}")
    logger.info(f"{enemy.name}: HP={enemy.current_hp}")
