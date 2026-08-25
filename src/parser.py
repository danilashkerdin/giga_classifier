"""Парсер ответов модели"""

import json
import re
import logging
from typing import Dict
from .models import Category, Priority, Emotion, ClassificationResult

logger = logging.getLogger(__name__)


class ResponseParser:
    """Парсер ответов модели GigaChat."""

    CATEGORY_MAPPING = {
        "биллинг": Category.BILLING,
        "оплата": Category.BILLING,
        "платежи": Category.BILLING,
        "счет": Category.BILLING,
        "тариф": Category.BILLING,
        "технический": Category.TECHNICAL,
        "техническая": Category.TECHNICAL,
        "ошибка": Category.TECHNICAL,
        "сбой": Category.TECHNICAL,
        "общий": Category.GENERAL,
        "общая": Category.GENERAL,
        "информация": Category.GENERAL,
    }

    PRIORITY_MAPPING = {
        "высокий": Priority.HIGH,
        "критичный": Priority.HIGH,
        "срочный": Priority.HIGH,
        "немедленно": Priority.HIGH,
        "средний": Priority.MEDIUM,
        "умеренный": Priority.MEDIUM,
        "низкий": Priority.LOW,
        "некритичный": Priority.LOW,
        "плановый": Priority.LOW,
    }

    EMOTION_MAPPING = {
        "позитивная": Emotion.POSITIVE,
        "положительная": Emotion.POSITIVE,
        "довольный": Emotion.POSITIVE,
        "спокойный": Emotion.NEUTRAL,
        "нейтральная": Emotion.NEUTRAL,
        "негативная": Emotion.NEGATIVE,
        "отрицательная": Emotion.NEGATIVE,
        "злой": Emotion.ANGRY,
        "раздраженный": Emotion.ANGRY,
        "расстроенный": Emotion.FRUSTRATED,
        "недовольный": Emotion.FRUSTRATED,
    }

    @classmethod
    def parse(cls, response_text: str) -> ClassificationResult:
        """Парсинг ответа модели в ClassificationResult."""
        response_text = (response_text or "").strip()

        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                logger.debug(f"Распарсен JSON: {result}")
                return cls._normalize_result(result)
            except json.JSONDecodeError as e:
                logger.warning(f"Ошибка парсинга JSON: {e}")

        return cls._normalize_result(cls._extract_from_text(response_text))

    @classmethod
    def _normalize_result(cls, result: Dict) -> ClassificationResult:
        """Нормализация словаря в ClassificationResult."""
        return ClassificationResult(
            category=cls._normalize_category(str(result.get("category", "")).lower().strip()),
            priority=cls._normalize_priority(str(result.get("priority", "")).lower().strip()),
            emotion=cls._normalize_emotion(str(result.get("emotion", "")).lower().strip()),
        )

    @classmethod
    def _normalize_category(cls, value: str) -> Category:
        if value in cls.CATEGORY_MAPPING:
            return cls.CATEGORY_MAPPING[value]
        try:
            return Category(value)
        except ValueError:
            logger.warning(f"Неизвестная категория: {value}, использую general")
            return Category.GENERAL

    @classmethod
    def _normalize_priority(cls, value: str) -> Priority:
        if value in cls.PRIORITY_MAPPING:
            return cls.PRIORITY_MAPPING[value]
        try:
            return Priority(value)
        except ValueError:
            logger.warning(f"Неизвестный приоритет: {value}, использую low")
            return Priority.LOW

    @classmethod
    def _normalize_emotion(cls, value: str) -> Emotion:
        if value in cls.EMOTION_MAPPING:
            return cls.EMOTION_MAPPING[value]
        try:
            return Emotion(value)
        except ValueError:
            return Emotion.NEUTRAL

    @classmethod
    def _extract_from_text(cls, text: str) -> Dict:
        """Извлечение значений из текстового ответа."""
        text_lower = text.lower()

        category = "general"
        for key, value in cls.CATEGORY_MAPPING.items():
            if key in text_lower:
                category = value.value
                break

        priority = "low"
        for key, value in cls.PRIORITY_MAPPING.items():
            if key in text_lower:
                priority = value.value
                break

        emotion = "neutral"
        for key, value in cls.EMOTION_MAPPING.items():
            if key in text_lower:
                emotion = value.value
                break

        return {"category": category, "priority": priority, "emotion": emotion}