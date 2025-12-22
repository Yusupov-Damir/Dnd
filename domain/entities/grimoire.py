from loguru import logger
from domain.entities.spell import Spell
from domain.entities.character import Character


class Grimoire:
    def __init__(self, init_spell: list[Spell] | Spell | None = None):
        """
        :param init_spell: Одиночное заклинание, список заклинаний или None
        """
        self.spell_list = self._normalize_spells(init_spell)

    @staticmethod
    def _normalize_spells(input_spells: list[Spell] | Spell | None) -> list[Spell]:
        """
        Нормализация: привести разные типы входа к единому списку

        :param input_spells: Входные данные (None, одно заклинание или список)
        :return: Список заклинаний
        """
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
