from loguru import logger

from domain.entities.creature import Creature


class Character(Creature):
    """Игровой персонаж"""

    def __init__(self, max_mana: int, max_hp: int, name: str):
        super().__init__(max_mana, max_hp, name)
        self.experience = 0

    def gain_experience(self, exp: int):
        self.experience += exp
        logger.info(f'Игрок {self.name} получил опыт {exp}, всего опыта: {self.experience}')
