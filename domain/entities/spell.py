from loguru import logger

from domain.entities.creature import Creature
from domain.enums.spell_type import SpellType


class Spell:
    def __init__(self, name: str, mana_cost: int, level: int, spell_type: SpellType, power: int):
        """
        :param name: Название заклинания
        :param mana_cost: Стоимость маны
        :param level: Уровень заклинания (1-10)
        :param spell_type: Тип заклинания (из перечисления SpellType)
        :param power: Сила эффекта (урон/лечение/бонус)
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
        """Активировать заклинание"""
        logger.info(f'Каст спелла {self.name} ✨')

    def apply_effect(self, target: Creature):
        """Применить эффект заклинания к цели"""
        if not isinstance(target, Creature):
            raise TypeError('Цель должна быть экземпляром класса Character')

        effect_method_name = self.spell_type.value
        """
        # Берем из атрибута spell_type экземпляр объекта SpellType.attribute_name, затем
        # достаем из объекта SpellType.attribute_name значение переменной - SpellType.attribute_name.value
        """
        if hasattr(target, effect_method_name):  # if у объекта "target" есть метод "effect_method_name"
            effect_method = getattr(target, effect_method_name)  # получаем obj.attr
            effect_method(self.power)  # вызываем obj.attr()
        else:
            logger.error(f'Метод {effect_method_name} не найден у цели')
