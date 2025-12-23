"""
Что делает: Применяет событие боя (модифицирует HP/Mana персонажей).
Это бонусные события, не заменяющие основную механику боя, а дополняющие
"""
from typing import Any
from loguru import logger
from services.json_protocol import clamp_int
from config.settings import settings


def apply_event(
        event: dict,
        player: Any,
        enemy: Any
) -> str | None:
    """
    Применяет событие боя к персонажам (модифицирует HP/Mana).

    Args:
        event: {"type": "modify_stats", "target": "player"|"enemy", "hp_delta": int, "mana_delta": int}
        player: Персонаж игрока (должен иметь current_hp, max_hp, current_mana, max_mana)
        enemy: Враг (должен иметь current_hp, max_hp, current_mana, max_mana)

    Returns:
        Строка с описанием произошедшего или None если ошибка
    """
    if event is None:
        return None

    try:
        event_type = event.get("type")

        # Проверяем что это событие модификации статов
        if event_type != "modify_stats":
            logger.warning(f"⚠️  Unknown event type: {event_type}")
            return None

        target = event.get("target")
        hp_delta = event.get("hp_delta", 0)
        mana_delta = event.get("mana_delta", 0)

        # Валидируем дельты
        if not isinstance(hp_delta, int) or not isinstance(mana_delta, int):
            logger.error("❌ hp_delta and mana_delta must be integers")
            return None

        # 🔥 Clamping экстремальных значений для баланса
        hp_delta = clamp_int(hp_delta, -settings.MAX_HP_DELTA, settings.MAX_HP_DELTA)
        mana_delta = clamp_int(mana_delta, -settings.MAX_MANA_DELTA, settings.MAX_MANA_DELTA)

        # Выбираем целевого персонажа
        if target == "player":
            target_entity = player
            target_name = player.name
        elif target == "enemy":
            target_entity = enemy
            target_name = enemy.name
        else:
            logger.error(f"❌ Unknown target: {target}")
            return None

        # Проверяем что у персонажа есть необходимые атрибуты
        if not hasattr(target_entity, 'current_hp') or not hasattr(target_entity, 'max_hp'):
            logger.error(f"❌ Target {target_name} missing HP attributes")
            return None

        if not hasattr(target_entity, 'current_mana') or not hasattr(target_entity, 'max_mana'):
            logger.error(f"❌ Target {target_name} missing Mana attributes")
            return None

        # Запоминаем старые значения
        old_hp = target_entity.current_hp
        old_mana = target_entity.current_mana

        # Применяем дельты с clamping (зажим в диапазон [0, max])
        new_hp = clamp_int(
            target_entity.current_hp + hp_delta,
            0,
            target_entity.max_hp
        )
        new_mana = clamp_int(
            target_entity.current_mana + mana_delta,
            0,
            target_entity.max_mana
        )

        # Обновляем атрибуты
        target_entity.current_hp = new_hp
        target_entity.current_mana = new_mana

        # Логируем изменения
        hp_change_str = f"HP: {old_hp} → {new_hp}"
        mana_change_str = f"Mana: {old_mana} → {new_mana}"

        result = f"📊 {target_name}: {hp_change_str}, {mana_change_str}"
        logger.info(result)

        return result

    except Exception as e:
        logger.error(f"❌ Error applying event: {e}")
        return None
