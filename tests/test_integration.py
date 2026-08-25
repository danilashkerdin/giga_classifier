"""Интеграционные тесты с реальным GigaChat API.

Запускаются только при наличии переменной окружения GIGACHAT_AUTH_KEY.
Иначе тесты пропускаются (pytest.mark.skip).
"""

import os

import pytest

from src.client import GigaChatClient
from src.classifier import RequestClassifier
from src.models import Category, Priority

AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")

pytestmark = pytest.mark.skipif(
    not AUTH_KEY,
    reason="Задайте GIGACHAT_AUTH_KEY для запуска тестов с реальным API",
)


@pytest.fixture(scope="module")
def client():
    return GigaChatClient(AUTH_KEY)


@pytest.fixture(scope="module")
def classifier(client):
    return RequestClassifier(client)


CASES = [
    # (текст обращения, ожидаемая категория)
    ("Не могу войти в мобильное приложение после обновления, выдает ошибку 500 при вводе пароля",
     Category.TECHNICAL),
    ("Подскажите, как изменить тарифный план? Хочу перейти на более дешевый тариф",
     Category.BILLING),
    ("Расскажите подробнее о ваших услугах и как начать пользоваться сервисом",
     Category.GENERAL),
]


def test_get_access_token_from_real_api(client):
    token = client.get_access_token()
    assert token
    assert client.access_token == token


def test_get_available_models_real_api(client):
    models = client.get_available_models()
    assert models
    assert any("GigaChat" in m for m in models)


@pytest.mark.parametrize("text,expected_category", CASES)
def test_classify_real_api(classifier, text, expected_category):
    result = classifier.classify(text)
    assert result.category == expected_category
    assert result.priority in (Priority.LOW, Priority.MEDIUM, Priority.HIGH)