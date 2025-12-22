from domain.entities.creature import Creature
from domain.entities.grimoire import Grimoire


class Enemy(Creature):
    def __init__(self, max_mana: int, max_hp: int, name: str, grimoire: Grimoire | None = None):
        super().__init__(max_mana, max_hp, name)
        self.grimoire = grimoire

    def choose_spell(self, target: 'Creature') -> str | None:
        """ИИ враг выбирает спелл для кастования"""

        # Ищем спелл урона который можем позволить
        damage_spells = [
            s for s in self.grimoire.spell_list
            if s.spell_type.value == 'take_damage' and s.mana_cost <= self.current_mana
        ]

        if damage_spells:
            return damage_spells[0].name  # Берём первый доступный

        # Если нет урона, ищем любой спелл
        available = [s for s in self.grimoire.spell_list
                     if s.mana_cost <= self.current_mana]

        if available:
            return available[0].name

        return None  # Нет доступных спеллов
