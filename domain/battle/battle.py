import time
from typing import Any

from domain.entities.character import Character
from domain.entities.enemy import Enemy
from domain.entities.grimoire import Grimoire
from domain.enums.spell_type import SpellType
from config.settings import settings
from loguru import logger
from utils.input_utils import input_with_log
from utils.ascii_art import BattleVisuals
from services.dm_service import DungeonMasterService
from services.dm_events import apply_event


class Battle:
    def __init__(self, player: Character, enemy: Enemy, grimoire: Grimoire, dm: DungeonMasterService | None = None):
        self.player = player
        self.enemy = enemy
        self.grimoire = grimoire
        self.round_number = 0
        self.basic_attack_damage = 10
        self.dm = dm  # ← Новое: DM сервис (может быть None)

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

    def _get_battle_state(self, last_action: dict) -> dict:
        """
        Формирует состояние боя для LLM.

        Args:
            last_action: Последнее действие игрока {"type": "...", "spell_name": "..."}

        Returns:
            dict с состоянием боя
        """
        return {
            "round": self.round_number,
            "player": {
                "name": self.player.name,
                "current_hp": self.player.current_hp,
                "max_hp": self.player.max_hp,
                "current_mana": self.player.current_mana,
                "max_mana": self.player.max_mana,
            },
            "enemy": {
                "name": self.enemy.name,
                "current_hp": self.enemy.current_hp,
                "max_hp": self.enemy.max_hp,
                "current_mana": self.enemy.current_mana,
                "max_mana": self.enemy.max_mana,
            },
            "last_action": last_action,
        }

    def run(self):
        while settings.MIN_HP < self.player.current_hp and settings.MIN_HP < self.enemy.current_hp:
            self.round_number += 1

            logger.info(BattleVisuals.round_header(self.round_number))
            time.sleep(1)

            # PLAYER TURN
            last_action = self._player_turn()

            # ✨ DM REACT на ход игрока
            if self.dm is not None:
                battle_state = self._get_battle_state(last_action)
                dm_resp = self.dm.react_to_action(battle_state, actor="player")

                if dm_resp:
                    if dm_resp.get("narration"):
                        logger.info(f"💬 {dm_resp['narration']}")
                        time.sleep(1)

                    if dm_resp.get("event"):
                        apply_event(dm_resp["event"], self.player, self.enemy)
                        time.sleep(0.5)

            logger.info(BattleVisuals.creature_status_box(self.player))
            time.sleep(0.5)
            logger.info(BattleVisuals.creature_status_box(self.enemy))
            time.sleep(1)

            time.sleep(2)

            if self.enemy.current_hp <= settings.MIN_HP:
                break

            # ENEMY TURN
            self._enemy_turn()

            # ✨ DM REACT на ход врага
            if self.dm is not None:
                battle_state = self._get_battle_state({})
                dm_resp = self.dm.react_to_action(battle_state, actor="enemy")

                if dm_resp:
                    if dm_resp.get("narration"):
                        logger.info(f"💬 {dm_resp['narration']}")
                        time.sleep(1)

                    if dm_resp.get("event"):
                        apply_event(dm_resp["event"], self.player, self.enemy)
                        time.sleep(0.5)

            logger.info(BattleVisuals.creature_status_box(self.player))
            time.sleep(0.5)
            logger.info(BattleVisuals.creature_status_box(self.enemy))
            time.sleep(3)

            time.sleep(2)

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

    def _player_turn(self) -> dict:
        """
        Выполняет ход игрока.

        Returns:
            dict с информацией о действии {"type": "...", "spell_name": "..."} для DM
        """
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
                return {"type": "basic_attack"}

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
                    return {"type": "cast_spell", "spell_name": spell_name}
                except (ValueError, IndexError):
                    logger.info("❌ Неверный выбор!")
                    time.sleep(1)

    def _get_enemy_available_spells(self) -> list:
        """Возвращает список доступных для врага damage-спеллов"""
        return [
            s for s in self.grimoire.spell_list
            if s.spell_type == SpellType.DAMAGE and s.mana_cost <= self.enemy.current_mana
        ]

    def _get_allowed_actions_for_enemy(self, damage_spells: list) -> dict:
        """Формирует структуру доступных действий для DM"""
        allowed_actions = {"basic_attack": {}}
        if damage_spells:
            allowed_actions["cast_spell"] = {
                "available_spells": [
                    {"name": s.name, "damage": s.power, "mana_cost": s.mana_cost}
                    for s in damage_spells
                ]
            }
        return allowed_actions

    def _try_dm_enemy_action(self, damage_spells: list) -> bool:
        """
        Пытается получить действие врага от DM.

        Args:
            damage_spells: Список доступных damage-спеллов

        Returns:
            True если действие было выполнено, False если нужен fallback
        """
        if self.dm is None:
            return False

        allowed_actions = self._get_allowed_actions_for_enemy(damage_spells)
        battle_state = self._get_battle_state({})
        dm_resp = self.dm.choose_enemy_action(battle_state, allowed_actions)

        if not dm_resp or not dm_resp.get("action"):
            return False

        action = dm_resp["action"]
        narration = dm_resp.get("narration", "")

        # Выполняем выбранное действие
        if action.get("type") == "basic_attack":
            logger.info(f"💬 {narration}")
            time.sleep(0.5)
            self._basic_attack(self.enemy, self.player)
            return True

        elif action.get("type") == "cast_spell":
            spell_name = action.get("spell_name")
            # Валидируем что спелл доступен
            if spell_name in [s.name for s in damage_spells]:
                logger.info(f"💬 {narration}")
                time.sleep(0.5)
                logger.info(f"🤖 {self.enemy.name} кастует {spell_name}!\n")
                time.sleep(1)
                self._cast_spell_for(self.enemy, spell_name, caster_is_player=False)
                return True

        return False

    def _enemy_turn(self):
        """Выполняет ход врага с опциональной помощью DM"""
        logger.info(f"👹 Ход {self.enemy.name}:\n")
        time.sleep(1)

        damage_spells = self._get_enemy_available_spells()

        # Попытка получить действие от DM
        if self._try_dm_enemy_action(damage_spells):
            return

        # FALLBACK: стандартная логика если DM отключен или ошибка
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
