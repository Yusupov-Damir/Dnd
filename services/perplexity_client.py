"""синхронно отправить запрос в Perplexity и вернуть сырой content (строку) или None"""
import json
import os

import httpx
from loguru import logger


class PerplexityClient:
    def __init__(self, model: str = "sonar", timeout_s: int = 10):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.model = model
        self.timeout_s = timeout_s
        self.base_url = "https://api.perplexity.ai/chat/completions"

        if not self.api_key:
            logger.warning("PERPLEXITY_API_KEY не найден в .env")

    def chat(self, message: list[dict], max_tokens: int = 300) -> str | None:
        """Отправляет запрос к LLM и возвращает ответ"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": message,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

        try:
            with httpx.Client(timeout=self.timeout_s) as client:
                # отправляем запрос и принимаем ответ - client.post()
                response = client.post(self.base_url, headers=headers, json=payload)

                # Вызовет исключение для 4XX/5XX ответов
                response.raise_for_status()

                # Десериализуем JSON и извлекаем текст ответа по пути: choices -> первый элемент -> message -> content
                content = response.json()["choices"][0]["message"]["content"]

                if not content:
                    logger.warning("Пустой ответ от API")
                    return None

                return content

        except httpx.TimeoutException:
            logger.error(f"Таймаут ({self.timeout_s} сек) при запросе к API")
            return None

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Ошибка парсинга ответа: {e}")
            return None

        except Exception as e:
            logger.error(f"Ошибка: {e}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    test_client = PerplexityClient()
    # Формат role + content - это требование Perplexity API
    test_message = [
        {
            "role": "system",
            "content": "Ты помощник. Ответь коротко."
        },
        {
            "role": "user",
            "content": "Привет! Как дела?"
        }
    ]
    test_client.chat(test_message)
