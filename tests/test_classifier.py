"""Тесты для классификатора."""

from src.models import Category, Priority, Emotion


class TestRequestClassifier:
    """Тесты классификатора обращений."""

    def test_classify_success(self, classifier, mock_client):
        mock_client.chat_completion.return_value = (
            '{"category": "technical", "priority": "high", "emotion": "angry"}'
        )
        result = classifier.classify("Не работает приложение, я в ярости!")

        assert result.category == Category.TECHNICAL
        assert result.priority == Priority.HIGH
        assert result.emotion == Emotion.ANGRY
        mock_client.chat_completion.assert_called_once()

    def test_classify_with_error(self, classifier, mock_client):
        mock_client.chat_completion.side_effect = Exception("API Error")
        result = classifier.classify("Тестовое обращение")

        assert result.category == Category.GENERAL
        assert result.priority == Priority.LOW
        assert result.emotion == Emotion.NEUTRAL

    def test_priority_adjustment_for_angry(self, classifier, mock_client):
        mock_client.chat_completion.return_value = (
            '{"category": "general", "priority": "low", "emotion": "angry"}'
        )
        result = classifier.classify("Я очень зол на ваш сервис!")

        assert result.priority == Priority.MEDIUM
        assert result.emotion == Emotion.ANGRY

    def test_priority_adjustment_for_frustrated(self, classifier, mock_client):
        mock_client.chat_completion.return_value = (
            '{"category": "billing", "priority": "medium", "emotion": "frustrated"}'
        )
        result = classifier.classify("Я расстроен, что счет неправильный")

        assert result.priority == Priority.HIGH
        assert result.emotion == Emotion.FRUSTRATED

    def test_no_priority_adjustment_for_positive(self, classifier, mock_client):
        mock_client.chat_completion.return_value = (
            '{"category": "general", "priority": "low", "emotion": "positive"}'
        )
        result = classifier.classify("Спасибо за хороший сервис!")

        assert result.priority == Priority.LOW
        assert result.emotion == Emotion.POSITIVE

    def test_build_messages(self, classifier):
        messages = classifier._build_messages("Тестовое обращение")

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "Тестовое обращение" in messages[1]["content"]
        assert "эмоциональную" in messages[1]["content"].lower()

    def test_classify_with_realistic_response(self, classifier, mock_client):
        mock_client.chat_completion.return_value = (
            'Вот результат классификации: {"category": "technical", '
            '"priority": "high", "emotion": "frustrated"}'
        )
        result = classifier.classify("Не могу войти в систему уже час, я устал ждать!")

        assert result.category == Category.TECHNICAL
        assert result.priority == Priority.HIGH
        assert result.emotion == Emotion.FRUSTRATED

    def test_build_messages_includes_categories_and_priorities(self, classifier):
        messages = classifier._build_messages("test")
        content = messages[1]["content"].lower()

        for value in ("billing", "technical", "general"):
            assert value in content
        for value in ("low", "medium", "high"):
            assert value in content