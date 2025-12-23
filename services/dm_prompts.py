"""Задача: хранить system prompt и собирать messages для Perplexity."""
import json
from config.settings import settings


def get_react_to_action_prompt(battle_state: dict, actor: str) -> str:
    """
    Формирует промпт для реакции на действие игрока или врага.

    Args:
        battle_state: Состояние боя
        actor: "player" или "enemy"

    Returns:
        Промпт для LLM
    """
    actor_name = battle_state["player"]["name"] if actor == "player" else battle_state["enemy"]["name"]
    spell_name = battle_state.get("last_action", {}).get("spell_name", "")

    action_desc = f"{actor_name} использует {spell_name}" if spell_name else f"{actor_name} атакует базовой атакой"

    prompt = f"""
Раунд боя #{battle_state['round']}

Состояние:
- {battle_state['player']['name']}: HP {battle_state['player']['current_hp']}/{battle_state['player']['max_hp']}, Мана {battle_state['player']['current_mana']}/{battle_state['player']['max_mana']}
- {battle_state['enemy']['name']}: HP {battle_state['enemy']['current_hp']}/{battle_state['enemy']['max_hp']}, Мана {battle_state['enemy']['current_mana']}/{battle_state['enemy']['max_mana']}

Действие: {action_desc}

Реагируй драматично на это действие от третьего лица! Описи эффект атаки/заклинания.

Если действие заслуживает дополнительного эффекта (урон, лечение, урон маны), добавь event.

Ответь JSON:
{{
    "narration": "драматичное описание (2-3 предложения)",
    "event": {{
        "type": "modify_stats",
        "target": "{('enemy' if actor == 'player' else 'player')}",
        "hp_delta": <число от -{settings.MAX_HP_DELTA} до +{settings.MAX_HP_DELTA}, 0 если нет эффекта>,
        "mana_delta": <число от -{settings.MAX_MANA_DELTA} до +{settings.MAX_MANA_DELTA}, 0 если нет эффекта>
    }}
}}

Только JSON, без лишнего текста.
"""
    return prompt.strip()


def get_choose_enemy_action_prompt(battle_state: dict, allowed_actions: dict) -> str:
    """
    Формирует промпт для выбора действия врага.

    Args:
        battle_state: Состояние боя
        allowed_actions: Доступные действия

    Returns:
        Промпт для LLM
    """
    enemy_name = battle_state['enemy']['name']
    player_name = battle_state['player']['name']

    prompt = f"""
Ты мастер подземелья. Выбери лучшее действие для {enemy_name} в этом раунде боя.

Раунд: #{battle_state['round']}

Состояние:
- {enemy_name}: HP {battle_state['enemy']['current_hp']}/{battle_state['enemy']['max_hp']}, Мана {battle_state['enemy']['current_mana']}/{battle_state['enemy']['max_mana']}
- {player_name}: HP {battle_state['player']['current_hp']}/{battle_state['player']['max_hp']}, Мана {battle_state['player']['current_mana']}/{battle_state['player']['max_mana']}

Доступные действия:
{json.dumps(allowed_actions, indent=2, ensure_ascii=False)}

Выбери лучшую тактику для {enemy_name}! Если враг ранен, рассмотри healing (если доступен).
Если враг в хорошей форме, атакуй с заклинаниями!

Ответь JSON (описание от третьего лица):
{{
    "action": {{
        "type": "basic_attack" или "cast_spell",
        "spell_name": "<имя заклинания если cast_spell>"
    }},
    "narration": "драматичное описание действия {enemy_name} от третьего лица (1-2 предложения)"
}}

Только JSON, без лишнего текста.
"""
    return prompt.strip()
