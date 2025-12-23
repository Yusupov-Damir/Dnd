"""бизнес-логика “мастера”: вызвать PerplexityClient → распарсить JSON → отдать нормализованный dict или None."""
from loguru import logger
from services.perplexity_client import PerplexityClient
from services.json_protocol import parse_json_object
from services.dm_prompts import (
    get_react_to_action_prompt,
    get_choose_enemy_action_prompt
)


class DungeonMasterService:
    """
    Сервис Dungeon Master'а — управляет реакциями LLM на боевые действия.
    """

    def __init__(self, client: PerplexityClient):
        self.client = client
        logger.info("DungeonMasterService инициализирован")

    def react_to_action(self, battle_state: dict, actor: str) -> dict | None:
        """
        Реагирует на действие игрока или врага.

        Args:
            battle_state: Состояние боя (round, player, enemy, last_action)
            actor: "player" или "enemy" — кто совершил действие

        Returns:
            {"narration": "...", "event": {...}} или None если ошибка
        """
        prompt = get_react_to_action_prompt(battle_state, actor)

        messages = [
            {
                "role": "system",
                "content": "Ты мастер подземелья в D&D. Реагируй на действия персонажей драматично и интересно."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.client.chat(messages, max_tokens=300)

        if not response:
            return None

        return parse_json_object(response)

    def choose_enemy_action(
            self,
            battle_state: dict,
            allowed_actions: dict
    ) -> dict | None:
        """
        Выбирает действие для врага.

        Args:
            battle_state: Состояние боя
            allowed_actions: Доступные действия {"basic_attack": {}, "cast_spell": {...}}

        Returns:
            {"action": {...}, "narration": "..."} или None если ошибка
        """
        prompt = get_choose_enemy_action_prompt(battle_state, allowed_actions)

        messages = [
            {
                "role": "system",
                "content": "Ты враг в D&D бою. Выбери лучшее действие из доступных."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.client.chat(messages, max_tokens=200)

        if not response:
            return None

        parsed = parse_json_object(response)

        if parsed:
            logger.info(
                f"Enemy action chosen: {parsed.get('action', {}).get('type')} | "
                f"Narration: {parsed.get('narration', '')}"
            )

        return parsed
