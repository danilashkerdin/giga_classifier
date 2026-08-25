"""Фикстуры для тестов"""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.client import GigaChatClient  # noqa: E402
from src.classifier import RequestClassifier  # noqa: E402
from src.models import Category, Priority, Emotion, ClassificationResult  # noqa: E402


@pytest.fixture
def mock_client():
    """Мок клиента GigaChat."""
    return Mock(spec=GigaChatClient)


@pytest.fixture
def classifier(mock_client):
    """Классификатор с мок-клиентом."""
    return RequestClassifier(mock_client)


@pytest.fixture
def sample_classification():
    """Пример результата классификации."""
    return ClassificationResult(
        category=Category.TECHNICAL,
        priority=Priority.HIGH,
        emotion=Emotion.FRUSTRATED,
    )