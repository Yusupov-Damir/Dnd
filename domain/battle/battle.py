from domain.entities.character import Character
from domain.entities.enemy import Enemy
from domain.entities.grimoire import Grimoire
from config.settings import settings
from loguru import logger
from utils.input_utils import input_with_log


class Battle:
    def __init__(self, player: Character, enemy: Enemy, grimoire: Grimoire):
        self.player = player
        self.enemy = enemy
        self.grimoire = grimoire
        self.round_number = 0

    def run(self):
        while settings.MIN_HP < self.player.current_hp and settings.MIN_HP < self.enemy.current_hp:
            self.round_number += 1
            logger.info(f"\n--- РАУНД {self.round_number} ---\n")

            self._player_turn()  # ← Вызываем ход игрока

            if self.enemy.current_hp <= settings.MIN_HP:
                break

            # Проверяем: может ли кто-то кастовать?
            player_can_cast = any(s.mana_cost <= self.player.current_mana
                                  for s in self.grimoire.spell_list)
            enemy_can_cast = any(s.mana_cost <= self.enemy.current_mana
                                 for s in self.grimoire.spell_list)

            if not player_can_cast and not enemy_can_cast:
                print("\n⚠️  Обе стороны исчерпали ресурсы! Боевая ничья!")
                break

            self._enemy_turn()  # ← Вызываем ход врага

        self._show_result()

    def _get_target(self, spell_name: str, caster_is_player: bool):
        """Определить цель спелла"""
        spell = self.grimoire.get_spell_by_name(spell_name)

        if spell.spell_type.value == 'take_hp':  # Healing
            return self.player if caster_is_player else self.enemy
        else:
            return self.enemy if caster_is_player else self.player

    def _player_turn(self):
        logger.info(f"🧙 Ход {self.player.name}:\n")

        # Покажи доступные спеллы
        available = [s for s in self.grimoire.spell_list
                     if s.mana_cost <= self.player.current_mana]

        for i, spell in enumerate(available, 1):
            logger.info(f"  {i}. {spell.name} (мана: {spell.mana_cost}, сила: {spell.power})")

        # кастомный input()
        choice = input_with_log(f"\n{self.player.name}, выбери спелл (номер): ").strip()

        try:
            idx = int(choice) - 1
            spell_name = available[idx].name

            # Кастуй спелл
            target = self._get_target(spell_name, caster_is_player=True)
            self.grimoire.cast_spell(spell_name, self.player, target)
        except (ValueError, IndexError):
            logger.info("❌ Неверный выбор!")

    def _enemy_turn(self):
        logger.info(f"👹 Ход {self.enemy.name}:\n")

        # Враг выбирает спелл
        spell_name = self.enemy.choose_spell(self.player)

        if spell_name:
            logger.info(f"🤖 {self.enemy.name} кастует {spell_name}!\n")
            self.grimoire.cast_spell(spell_name, self.enemy, self.player)
        else:
            logger.info(f"⚠️  {self.enemy.name} не может кастовать (нет маны)!\n")

    def _show_result(self):
        logger.info("\n" + "=" * 50)

        if self.player.current_hp > 0 and self.enemy.current_hp > 0:
            # ← ДОБАВЬ ЭТО: если оба живы → ничья
            print(f"🤝 БОЕВАЯ НИЧЬЯ! Обе стороны исчерпали ресурсы!")
        elif self.player.current_hp > 0:
            print(f"💫 ПОБЕДА! {self.player.name} выиграл!")
            print(f"{self.enemy.name} повергнут!")
        else:
            print(f"💀 ПОРАЖЕНИЕ! {self.player.name} проиграл...")

        logger.info(f"\n{self.player.get_status()}")
        logger.info(f"{self.enemy.get_status()}")
        logger.info("=" * 50)
