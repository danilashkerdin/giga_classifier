# Умный классификатор обращений

Скрипт на Python, который принимает текст обращения пользователя в поддержку и возвращает категорию (`billing`, `technical`, `general`) и приоритет (`low`, `medium`, `high»), оценивая их с помощью GigaChat API.

## Возможности

- Получение и кэширование access token (~29 минут).
- Формирование промпта с анализом эмоциональной окраски.
- Повышение приоритета при негативной эмоции (`angry`/`frustrated`):
  - `low` → `medium`, `medium` → `high`.
- Устойчивый парсинг ответов модели (JSON и/или текст, русские термины, fallback на значения по умолчанию).
- 23 теста с моками (без реального API).

## Структура

```
giga_classifier/
├── src/
│   ├── models.py      # Enum-модели (Category, Priority, Emotion)
│   ├── client.py      # GigaChatClient — работа с API
│   ├── parser.py      # ResponseParser — разбор ответов
│   └── classifier.py  # RequestClassifier — бизнес-логика
├── tests/
│   ├── conftest.py         # Фикстуры и моки
│   ├── test_parser.py      # 7 тестов парсера
│   ├── test_classifier.py  # 8 тестов классификатора
│   └── test_client.py      # 8 тестов клиента
├── config/
│   └── logging_config.py   # Настройка логирования
├── main.py                 # Точка входа
└── requirements.txt        # Зависимости
```

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

Получите Authorization key (Base64-креды) на [developers.sber.ru](https://developers.sber.ru/studio/login) и задайте переменную окружения:

```bash
export GIGACHAT_AUTH_KEY="<ваш_auth_key>"
```

## Запуск

```bash
python main.py
```

При запуске прогоняются тестовые обращения, затем запускается интерактивный режим (введите `exit` для выхода).

## Запуск тестов

```bash
pytest tests/ -v
```

## Пример

```
Вход:  "Я в бешенстве! Третий раз списываете деньги!"
Выход: {"category": "billing", "priority": "high", "emotion": "angry"}

Вход:  "Как изменить тариф?"
Выход: {"category": "billing", "priority": "medium", "emotion": "neutral"}
```