import time

from domain.entities.character import Character
from domain.entities.enemy import Enemy
from domain.entities.grimoire import Grimoire
from domain.enums.spell_type import SpellType
from config.settings import settings
from loguru import logger
from utils.input_utils import input_with_log
from utils.ascii_art import BattleVisuals


class Battle:
    def __init__(self, player: Character, enemy: Enemy, grimoire: Grimoire):
        self.player = player
        self.enemy = enemy
        self.grimoire = grimoire
        self.round_number = 0
        self.basic_attack_damage = 10

    def _available_spells(self, caster):
        """возвращает список заклинаний, которые кастер может применить (по мане)"""
        return [s for s in self.grimoire.spell_list if s.mana_cost <= caster.current_mana]

    def _can_cast(self, caster) -> bool:
        """проверяет, может ли кастер применить хотя бы одно заклинание"""
        return any(s.mana_cost <= caster.current_mana for s in self.grimoire.spell_list)

    def _cast_spell_for(self, caster, spell_name: str, caster_is_player: bool):
        """применяет заклинание от имени кастера к выбранной цели"""
        target = self._get_target(spell_name, caster_is_player=caster_is_player)
        self.grimoire.cast_spell(spell_name, caster, target)

    def _basic_attack(self, attacker, defender):
        """выполняет базовую атаку атакующего по защищающемуся"""
        logger.info(BattleVisuals.attack_animation(attacker.name, defender.name, self.basic_attack_damage))
        time.sleep(0.5)
        defender.take_damage(self.basic_attack_damage)

    def run(self):
        while settings.MIN_HP < self.player.current_hp and settings.MIN_HP < self.enemy.current_hp:
            self.round_number += 1

            logger.info(BattleVisuals.round_header(self.round_number))
            time.sleep(1)

            self._player_turn()  # ← Вызываем ход игрока

            logger.info(BattleVisuals.creature_status_box(self.player))
            time.sleep(0.5)
            logger.info(BattleVisuals.creature_status_box(self.enemy))
            time.sleep(3)

            if self.enemy.current_hp <= settings.MIN_HP:
                break

            self._enemy_turn()  # ← Вызываем ход врага

            logger.info(BattleVisuals.creature_status_box(self.player))
            time.sleep(0.5)
            logger.info(BattleVisuals.creature_status_box(self.enemy))
            time.sleep(3)

        self._show_result()

    def _get_target(self, spell_name: str, caster_is_player: bool):
        """Определить цель спелла"""
        spell = self.grimoire.get_spell_by_name(spell_name)

        if spell is None:
            raise ValueError(f"Спелл {spell_name} отсутствует в гримуаре!")

        if spell.spell_type == SpellType.HEAL:  # Healing
            return self.player if caster_is_player else self.enemy
        else:
            return self.enemy if caster_is_player else self.player

    def _player_turn(self):
        logger.info(f"🧙 Ход {self.player.name}:\n")
        time.sleep(1)

        while True:
            available = self._available_spells(self.player)
            # input_with_log - кастомный input()
            action_choice = input_with_log(
                f"\n{self.player.name}, выбери действие:\n"
                f"  1. Базовая атака ({self.basic_attack_damage} урона)\n"
                f"  2. Заклинание\n"
                f"Ввод: "
            ).strip()
            time.sleep(0.5)

            if action_choice == '1':
                self._basic_attack(self.player, self.enemy)
                return

            if action_choice != '2':
                logger.info("❌ Неверный выбор!")
                time.sleep(0.5)
                continue

            if not available:
                logger.info(f"⚠️  {self.player.name} не может кастовать (нет маны)!\n")
                time.sleep(0.5)
                continue

            for i, spell in enumerate(available, 1):
                logger.info(f"  {i}. {spell.name} (мана: {spell.mana_cost}, сила: {spell.power})")
                time.sleep(0.5)

            while True:
                # кастомный input()
                choice = input_with_log(f"\n{self.player.name}, выбери спелл (номер): ").strip()

                try:
                    idx = int(choice) - 1
                    spell_name = available[idx].name

                    # Кастуй спелл
                    self._cast_spell_for(self.player, spell_name, caster_is_player=True)
                    return
                except (ValueError, IndexError):
                    logger.info("❌ Неверный выбор!")
                    time.sleep(1)

    def _enemy_turn(self):
        logger.info(f"👹 Ход {self.enemy.name}:\n")
        time.sleep(1)

        damage_spells = [
            s for s in self.grimoire.spell_list
            if s.spell_type == SpellType.DAMAGE and s.mana_cost <= self.enemy.current_mana
        ]

        if damage_spells:
            spell_name = damage_spells[0].name
            logger.info(f"🤖 {self.enemy.name} кастует {spell_name}!\n")
            time.sleep(1)
            self._cast_spell_for(self.enemy, spell_name, caster_is_player=False)
            return

        self._basic_attack(self.enemy, self.player)

    def _show_result(self):
        if self.player.current_hp > 0:
            logger.info(BattleVisuals.victory_banner())
        else:
            logger.info(BattleVisuals.defeat_banner())

        logger.info(BattleVisuals.creature_status_box(self.player))
        logger.info(BattleVisuals.creature_status_box(self.enemy))
