import asyncio
import httpx
from config.settings import settings
from loguru import logger


class PerplexityService:
    """Perplexity API"""

    BASE_URL = "https://api.perplexity.ai/chat/completions"

    @staticmethod
    async def get_response(prompt: str, model: str = "sonar") -> str | None:
        """Получить ответ от Perplexity"""

        headers = {
            "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 200
        }

        logger.info(f"Отправляю запрос: {prompt}")
        logger.info(f"Модель: {model}")

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    PerplexityService.BASE_URL,
                    headers=headers,
                    json=payload
                )

                logger.info(f"Статус: {response.status_code}")
                logger.info(f"Ответ: {response.text}")

                if response.status_code != 200:
                    return None

                data = response.json()

                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]

                return None

        except Exception as e:
            logger.error(f"Ошибка: {e}")
            return None


async def main():
    logger.info("Тестирую Perplexity API...")

    # Пробуем разные модели
    models_to_try = [
        "sonar",
        "sonar-pro",
        "sonar-reasoning",
        "pplx-sonar",
        "pplx-sonar-pro"
    ]

    for model in models_to_try:
        logger.info(f"\nПопытка с моделью: {model}")
        response = await PerplexityService.get_response("Hello!", model=model)

        if response:
            logger.info(f"УСПЕХ с моделью {model}!")
            logger.info(f"Ответ: {response}")
            break
        else:
            logger.info(f"Не работает {model}, пробуем следующую...")


if __name__ == "__main__":
    asyncio.run(main())





