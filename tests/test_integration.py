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


def test_get_access_token_from_real_api(client):
    token = client.get_access_token()
    assert token
    assert client.access_token == token


def test_get_available_models_real_api(client):
    models = client.get_available_models()
    assert models
    assert any("GigaChat" in m for m in models)


CATEGORY_CASES = [
    # (текст обращения, ожидаемая категория)
    ("Не могу войти в мобильное приложение после обновления, выдает ошибку 500 при вводе пароля",
     Category.TECHNICAL),
    ("Приложение падает при каждом запуске, это критично для моей работы",
     Category.TECHNICAL),
    ("Забыл пароль и не могу восстановить доступ, помогите пожалуйста",
     Category.TECHNICAL),
    ("Я в бешенстве! Третий раз списываете деньги с карты без моего согласия!",
     Category.BILLING),
    ("У меня по ошибке списали деньги за подписку, которую я отменил месяц назад",
     Category.BILLING),
    ("Подскажите, как изменить тарифный план? Хочу перейти на более дешевый тариф",
     Category.BILLING),
    ("Расскажите подробнее о ваших услугах и как начать пользоваться сервисом",
     Category.GENERAL),
    ("Хочу узнать график работы вашего офиса",
     Category.GENERAL),
]


@pytest.mark.parametrize("text,expected_category", CATEGORY_CASES)
def test_category_real_api(classifier, text, expected_category):
    result = classifier.classify(text)
    assert result.category == expected_category


PRIORITY_CASES = [
    # (текст обращения, ожидаемый приоритет)
    ("Срочно! Вся система лежит, ничего не работает уже несколько часов!",
     Priority.HIGH),
    ("Я в бешенстве! Третий раз списываете деньги с карты без моего согласия!",
     Priority.HIGH),
    ("Не могу войти в мобильное приложение после обновления, выдает ошибку 500 при вводе пароля",
     Priority.HIGH),
    ("Приложение падает при каждом запуске, это критично для моей работы",
     Priority.HIGH),
    ("Забыл пароль и не могу восстановить доступ, помогите пожалуйста",
     Priority.HIGH),
    ("Хочу отменить платную подписку, расскажите как это сделать",
     Priority.MEDIUM),
    ("Мне нужна помощь с настройкой двухфакторной аутентификации",
     Priority.MEDIUM),
    ("Расскажите подробнее о ваших услугах и как начать пользоваться сервисом",
     Priority.LOW),
    ("Хочу узнать график работы вашего офиса",
     Priority.LOW),
    ("Подскажите, как изменить тарифный план? Хочу перейти на более дешевый тариф",
     Priority.LOW),
]


@pytest.mark.parametrize("text,expected_priority", PRIORITY_CASES)
def test_priority_real_api(classifier, text, expected_priority):
    result = classifier.classify(text)
    assert result.priority == expected_priority