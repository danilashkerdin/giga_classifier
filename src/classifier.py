"""Классификатор обращений пользователей"""

import logging
from typing import Dict, List
from .client import GigaChatClient
from .parser import ResponseParser
from .models import ClassificationResult, Category, Priority, Emotion

logger = logging.getLogger(__name__)


class RequestClassifier:
    """Классификатор обращений."""

    def __init__(self, client: GigaChatClient, parser: type = ResponseParser):
        """
        Args:
            client: Клиент GigaChat API.
            parser: Класс парсера ответов.
        """
        self.client = client
        self.parser = parser

    def classify(self, user_text: str) -> ClassificationResult:
        """Классификация обращения пользователя."""
        logger.info(f"Классификация обращения: {user_text[:50]}...")
        messages = self._build_messages(user_text)

        try:
            model_response = self.client.chat_completion(
                messages=messages, temperature=0.1, max_tokens=150
            )
            logger.debug(f"Ответ модели: {model_response}")

            result = self.parser.parse(model_response)
            result = self._adjust_priority_by_emotion(result)

            logger.info(f"Результат: {result.to_dict()}")
            return result

        except Exception as e:
            logger.error(f"Ошибка классификации: {e}")
            return ClassificationResult(
                category=Category.GENERAL,
                priority=Priority.LOW,
                emotion=Emotion.NEUTRAL,
            )

    def _build_messages(self, user_text: str) -> List[Dict[str, str]]:
        """Формирование сообщений для модели."""
        system_prompt = (
            "Ты - классификатор обращений в службу поддержки. "
            "Отвечай только в формате JSON."
        )

        user_prompt = f"""
        Проанализируй обращение пользователя и определи:

        1. Категорию (строго одно из):
           - "billing" - оплата, счета, тарифы
           - "technical" - технические проблемы
           - "general" - общие вопросы

        2. Приоритет (строго одно из):
           - "low" - некритично
           - "medium" - умеренно
           - "high" - критично

        3. Эмоциональную окраску (строго одно из):
           - "positive" - позитивная
           - "neutral" - нейтральная
           - "negative" - негативная
           - "angry" - злость
           - "frustrated" - расстройство

        Важно: Если пользователь злится или расстроен (angry, frustrated),
        повышай приоритет обращения.

        Обращение: "{user_text}"

        Верни JSON: {{"category": "...", "priority": "...", "emotion": "..."}}
        """

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _adjust_priority_by_emotion(self, result: ClassificationResult) -> ClassificationResult:
        """Повышение приоритета при негативной эмоции."""
        if result.emotion in [Emotion.ANGRY, Emotion.FRUSTRATED]:
            if result.priority == Priority.LOW:
                logger.info("Повышение приоритета: low → medium (негативная эмоция)")
                result.priority = Priority.MEDIUM
            elif result.priority == Priority.MEDIUM:
                logger.info("Повышение приоритета: medium → high (негативная эмоция)")
                result.priority = Priority.HIGH
        return result