"""ASCII-арт для визуализации боевой системы"""


class BattleVisuals:
    """Визуальные эффекты для боя"""

    @staticmethod
    def health_bar(current_hp: int, max_hp: int, width: int = 20) -> str:
        """Полоска здоровья"""
        filled = int((current_hp / max_hp) * width)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        return f"❤️  HP: [{bar}] {current_hp}/{max_hp}"

    @staticmethod
    def mana_bar(current_mana: int, max_mana: int, width: int = 20) -> str:
        """Полоска маны"""
        filled = int((current_mana / max_mana) * width)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        return f"💙 Мана: [{bar}] {current_mana}/{max_mana}"

    @staticmethod
    def creature_status_box(creature) -> str:
        """Красивый блок статуса существа"""
        hp_bar = BattleVisuals.health_bar(creature.current_hp, creature.max_hp)
        mana_bar = BattleVisuals.mana_bar(creature.current_mana, creature.max_mana)

        return (
            f"\n{'─' * 40}\n"
            f"🧙 {creature.name}\n"
            f"{hp_bar}\n"
            f"{mana_bar}\n"
            f"{'─' * 40}"
        )

    @staticmethod
    def round_header(round_number: int) -> str:
        """Заголовок раунда"""
        return (
            f"\n╔{'═' * 38}╗\n"
            f"║ {'⚔️  РАУНД ' + str(round_number):^36} ║\n"
            f"╚{'═' * 38}╝\n"
        )

    @staticmethod
    def victory_banner() -> str:
        """Баннер победы"""
        return (
            f"\n{'═' * 40}\n"
            f"{'💫 ПОБЕДА! 💫':^40}\n"
            f"{'═' * 40}\n"
        )

    @staticmethod
    def defeat_banner() -> str:
        """Баннер поражения"""
        return (
            f"\n{'═' * 40}\n"
            f"{'💀 ПОРАЖЕНИЕ! 💀':^40}\n"
            f"{'═' * 40}\n"
        )

    @staticmethod
    def attack_animation(attacker: str, defender: str, damage: int) -> str:
        """Анимация обычной атаки"""
        return (
            f"\n🗡️  {attacker} атакует!\n"
            f"   ⚡ ⚡ ⚡\n"
            f"     ↓\n"
            f"🛡️  {defender} получил {damage} урона!\n"
        )
