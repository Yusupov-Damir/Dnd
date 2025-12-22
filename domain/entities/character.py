from loguru import logger
from config.settings import settings


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
        if not settings.MIN_MANA <= max_mana <= settings.MAX_MANA:
            raise ValueError(f'Стартовая манна должна быть в диапазоне {settings.MIN_MANA} - {settings.MAX_MANA}')
        if not settings.MIN_HP <= max_hp <= settings.MAX_HP:
            raise ValueError(f'Стартовое здоровье должно быть в диапазоне {settings.MIN_HP} - {settings.MAX_HP}')

    @property
    # @property превращает метод в дескриптор. Теперь он вызывается без "()", и связан с setter
    # Геттер: вызывается, когда мы ЧИТАЕМ (print(hero.current_hp))
    def current_hp(self) -> int:
        return self._current_hp

    @current_hp.setter
    # Сеттер: вызывается, когда мы ПИШЕМ (hero.current_hp = ...)
    def current_hp(self, value):
        # Прием «зажим»/clamping - значение переменной не выйдет за установленные границы (0...max_hp)
        self._current_hp = max(settings.MIN_HP, min(value, self.max_hp))

    @property
    def current_mana(self) -> int:
        return self._current_mana

    @current_mana.setter
    def current_mana(self, value):
        self._current_mana = max(settings.MIN_MANA, min(value, self.max_mana))

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
        self.current_hp = settings.MAX_HP
        self.current_mana = settings.MIN_MANA
        logger.info('Персонаж отдохнул, здоровье и мана восстановлены')

    def get_status(self) -> str:
        return (
            f'Персонаж: {self.name}, '
            f'hp: {self.current_hp}, '
            f'мана: {self.current_mana}, '
            f'уровень: {self.level}, '
            f'опыт: {self.experience},'
        )
