"""Главный файл приложения."""

import logging
import os

from dotenv import load_dotenv

from src.client import GigaChatClient
from src.classifier import RequestClassifier
from config.logging_config import setup_logging

logger = logging.getLogger(__name__)

load_dotenv()

AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY", "")

TEST_CASES = [
    "Не могу войти в мобильное приложение после обновления, выдает ошибку 500 при вводе пароля",
    "Подскажите, как изменить тарифный план? Хочу перейти на более дешевый тариф",
    "Расскажите подробнее о ваших услугах и как начать пользоваться сервисом",
    "Я очень зол! Ваш сервис не работает уже второй день, я требую немедленного решения проблемы!",
]


def main():
    """Точка входа приложения."""
    setup_logging(log_level="INFO", log_file="logs/classifier.log")

    if not AUTH_KEY:
        logger.error("Не задан GIGACHAT_AUTH_KEY. Укажите его в переменной окружения.")
        return

    client = GigaChatClient(AUTH_KEY)
    classifier = RequestClassifier(client)

    if not client.test_connection():
        logger.error("Не удалось подключиться к API")
        return

    logger.info("Прогон тестовых обращений")
    for i, case in enumerate(TEST_CASES, 1):
        result = classifier.classify(case)
        logger.info(f"Тест {i}: {case[:50]}... -> {result.to_json()}")

    logger.info("Запуск интерактивного режима")
    print("\n" + "=" * 60)
    print("Классификатор обращений готов к работе")
    print("Введите 'exit' для выхода")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nВведите обращение: ").strip()
            if user_input.lower() == "exit":
                logger.info("Завершение работы")
                break
            if user_input:
                result = classifier.classify(user_input)
                print(f"\nРезультат: {result.to_json()}")
        except KeyboardInterrupt:
            logger.info("Прерывание пользователем")
            break
        except Exception as e:
            logger.error(f"Ошибка: {e}")


if __name__ == "__main__":
    main()