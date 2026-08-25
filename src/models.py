"""Модели данных для классификатора обращений"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum
import json


class Category(str, Enum):
    """Категории обращений"""
    BILLING = "billing"
    TECHNICAL = "technical"
    GENERAL = "general"


class Priority(str, Enum):
    """Приоритеты обращений"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Emotion(str, Enum):
    """Эмоциональная окраска обращения"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    ANGRY = "angry"
    FRUSTRATED = "frustrated"


@dataclass
class ClassificationResult:
    """Результат классификации обращения"""
    category: Category
    priority: Priority
    emotion: Optional[Emotion] = None

    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        result = {
            "category": self.category.value,
            "priority": self.priority.value,
        }
        if self.emotion:
            result["emotion"] = self.emotion.value
        return result

    def to_json(self) -> str:
        """Преобразование в JSON строку"""
        return json.dumps(self.to_dict(), ensure_ascii=False)