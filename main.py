class Spell:
    def __init__(self, name: str, mana_cost: int, level: int, ):
        if not 1 <= level <= 10:
            raise ValueError("Уровень заклинания должен быть в диапазоне 0 - 10")
        self.name = name
        self.level = level
        self.mana_cost = mana_cost

    def cast(self):
        print(f'Каст спелла {self.name}')


class Grimoire:
    def __init__(self, init_spell: Spell, mana: int = 100):
        self.spell_list: list[Spell] = [init_spell] if init_spell else []
        self.mana = mana

    def add_spell(self):
        pass


if __name__ == "__main__":
    healing = Spell("heal", 10, 0)
