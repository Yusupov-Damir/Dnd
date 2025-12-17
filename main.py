import sys

from loguru import logger

# Удалим стандартный вывод логов и настроим свой:
logger.remove()
logger.add(sys.stderr, format="<level>{level: <8}</level> | {message}")


class Character:
    def __init__(self):
        self.current_mana: int = 100


class Spell:
    def __init__(self, name: str, mana_cost: int, level: int, ):
        if not 1 <= level <= 10:
            raise ValueError('Уровень заклинания должен быть в диапазоне 0 - 10')
        self.name = name
        self.mana_cost = mana_cost
        self.level = level

    def __str__(self):
        return f'Спелл {self.name}'

    def __repr__(self):
        return f'Spell: (name={self.name}, mana_cost={self.mana_cost}, level={self.level})'

    def cast(self):
        logger.info(f'Каст спелла {self.name} ✨')


class Grimoire:
    def __init__(self, init_spell: list[Spell] | Spell | None = None):
        if init_spell is None:
            self.spell_list = []
        elif isinstance(init_spell, Spell):
            self.spell_list = [init_spell]
        else:
            self.spell_list = init_spell

    def add_spell(self, spell: Spell):
        self.spell_list.append(spell)

    def show_all_spells(self):
        logger.info('Все спеллы гримуара:')
        for spell in self.spell_list:
            logger.info(f'{spell.name}')

    def get_spell_by_name(self, spell_name: str) -> Spell | None:
        for spell in self.spell_list:
            if spell.name == spell_name:
                return spell
        return None

    def cast_spell(self, spell_name: str, character: Character) -> None:
        spell = self.get_spell_by_name(spell_name)
        if spell.mana_cost <= character.current_mana:
            character.current_mana -= spell.mana_cost
            spell.cast()
            return None
        raise ValueError(f'Текущий остаток манны:{character.current_mana}, стоимость спелла:{spell.mana_cost}')


if __name__ == "__main__":
    player = Character()
    fireball = Spell('Fireball', 30, 1)
    healing = Spell('Healing', 10, 1)
    teleport = Spell('Teleport', 20, 1)
    old_grimoire = Grimoire([fireball, healing, teleport])
    old_grimoire.show_all_spells()
    old_grimoire.cast_spell('Fireball', player)
    old_grimoire.cast_spell('Healing', player)
    old_grimoire.cast_spell('Teleport', player)
