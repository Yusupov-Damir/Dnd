"""безопасно распарсить “строго JSON” в dict"""
import json
from loguru import logger


def parse_json_object(raw: str) -> dict | None:
    """
    Парсит JSON из строки, убирая markdown блоки если есть.

    Args:
        raw: Строка с JSON (может быть обернута в ```json ... ```)

    Returns:
        dict или None если ошибка парсинга
    """
    if raw is None or not isinstance(raw, str):
        logger.error("❌ Input is not a string")
        return None

    # Убираем markdown блоки ```json ... ```
    if raw.startswith("```"):
        # Находим первый перевод строки после ```
        first_newline = raw.find("\n")
        if first_newline != -1:
            raw = raw[first_newline + 1:]
            # Ищем закрывающие ```
            closing_fence = raw.rfind("```")
            if closing_fence != -1:
                raw = raw[:closing_fence]

            raw = raw.strip()

        # Пытаемся найти JSON объект в строке (на случай если LLM добавил текст после JSON)
        # Ищем первый { и последний }
        first_brace = raw.find("{")
        last_brace = raw.rfind("}")

        if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
            raw = raw[first_brace:last_brace + 1]

    try:
        parsed = json.loads(raw)

        if not isinstance(parsed, dict):
            logger.error("❌ Parsed JSON is not a dict")
            return None

        logger.debug(f"✅ Parsed JSON: {parsed}")
        return parsed

    except json.JSONDecodeError as e:
        logger.error(f"❌ parse_json_object: невалидный JSON - {e}")
        return None


def clamp_int(value: int, min_val: int, max_val: int) -> int:
    """
    Зажимает целое число в диапазон [min_val, max_val].

    Args:
        value: Значение
        min_val: Минимум
        max_val: Максимум

    Returns:
        Зажатое значение
    """
    return max(min_val, min(value, max_val))


if __name__ == "__main__":
    # Тест 1: валидный JSON
    test1 = parse_json_object('{"narration": "test", "event": null}')
    print(f"✅ Тест 1: {test1}")

    # Тест 2: невалидный JSON
    test2 = parse_json_object('not json')
    print(f"✅ Тест 2: {test2}")

    # Тест 3: clamp_int
    test3 = clamp_int(150, 0, 100)
    print(f"✅ Тест 3: clamp_int(150, 0, 100) = {test3}")

    # Тест 4: clamp_int с отрицательным
    test4 = clamp_int(-5, 0, 100)
    print(f"✅ Тест 4: clamp_int(-5, 0, 100) = {test4}")
