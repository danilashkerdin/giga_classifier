"""Тесты для парсера ответов."""

from src.parser import ResponseParser
from src.models import Category, Priority, Emotion


class TestResponseParser:
    """Тесты парсера ответов."""

    def test_parse_valid_json(self):
        response = '{"category": "technical", "priority": "high", "emotion": "angry"}'
        result = ResponseParser.parse(response)
        assert result.category == Category.TECHNICAL
        assert result.priority == Priority.HIGH
        assert result.emotion == Emotion.ANGRY

    def test_parse_json_with_extra_text(self):
        response = 'Вот результат: {"category": "billing", "priority": "medium", "emotion": "neutral"}'
        result = ResponseParser.parse(response)
        assert result.category == Category.BILLING
        assert result.priority == Priority.MEDIUM
        assert result.emotion == Emotion.NEUTRAL

    def test_parse_text_response(self):
        response = "Категория: техническая проблема, Приоритет: высокий, Эмоция: злой"
        result = ResponseParser.parse(response)
        assert result.category == Category.TECHNICAL
        assert result.priority == Priority.HIGH
        assert result.emotion == Emotion.ANGRY

    def test_parse_invalid_category(self):
        response = '{"category": "unknown", "priority": "high", "emotion": "neutral"}'
        result = ResponseParser.parse(response)
        assert result.category == Category.GENERAL
        assert result.priority == Priority.HIGH

    def test_parse_empty_response(self):
        result = ResponseParser.parse("")
        assert result.category == Category.GENERAL
        assert result.priority == Priority.LOW
        assert result.emotion == Emotion.NEUTRAL

    def test_parse_russian_values(self):
        response = '{"category": "оплата", "priority": "срочный", "emotion": "раздраженный"}'
        result = ResponseParser.parse(response)
        assert result.category == Category.BILLING
        assert result.priority == Priority.HIGH
        assert result.emotion == Emotion.ANGRY

    def test_parse_missing_emotion(self):
        response = '{"category": "general", "priority": "low"}'
        result = ResponseParser.parse(response)
        assert result.category == Category.GENERAL
        assert result.priority == Priority.LOW
        assert result.emotion == Emotion.NEUTRAL