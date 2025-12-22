from enum import Enum

class SpellType(Enum):
    """Типы заклинаний"""
    # Атрибуты класса Enum нельзя менять или дополнять. Это стабильные константы
    DAMAGE = 'take_damage'
    HEAL = 'take_hp'
    MANA = 'take_mana'