"""Клиент для взаимодействия с GigaChat API"""

import logging
import uuid
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class GigaChatClient:
    """Клиент для работы с GigaChat API"""

    def __init__(self, auth_key: str):
        """
        Args:
            auth_key: Authorization key (Base64-закодированные credentials).
        """
        self.auth_key = auth_key
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.base_url = "https://api.giga.chat/v1"
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.timeout = 30

    def get_access_token(self) -> str:
        """Получение и кэширование access token (на ~29 минут)."""
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            logger.debug("Используем существующий access token")
            return self.access_token

        logger.info("Запрос нового access token")
        payload = {"scope": "GIGACHAT_API_PERS"}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {self.auth_key}",
        }

        try:
            response = requests.post(
                self.auth_url, headers=headers, data=payload,
                verify=False, timeout=self.timeout,
            )
            if response.status_code != 200:
                raise Exception(self._format_error("Ошибка получения токена", response))

            token_data = response.json()
            token = token_data.get("access_token")
            if not token:
                raise Exception("Access token не найден в ответе")

            self.access_token = token
            self.token_expiry = datetime.now() + timedelta(minutes=29)
            logger.info("Access token успешно получен")
            return token

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения: {e}")
            raise Exception(f"Ошибка соединения: {e}")

    def get_available_models(self) -> List[str]:
        """Получение списка доступных моделей."""
        token = self.access_token or self.get_access_token()
        url = f"{self.base_url}/models"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }

        try:
            response = requests.get(url, headers=headers, verify=False, timeout=self.timeout)
            if response.status_code != 200:
                raise Exception(self._format_error("Ошибка получения моделей", response))

            models = [m.get("id", "unknown") for m in response.json().get("data", [])]
            logger.info(f"Получены модели: {', '.join(models)}")
            return models
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения: {e}")
            raise Exception(f"Ошибка соединения: {e}")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 150,
        model: str = "GigaChat-2",
    ) -> str:
        """Отправка запроса на генерацию текста. Возвращает ответ модели."""
        token = self.access_token or self.get_access_token()
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.9,
        }

        try:
            response = requests.post(
                url, headers=headers, json=payload, verify=False, timeout=self.timeout,
            )
            if response.status_code != 200:
                raise Exception(self._format_error("Ошибка запроса к GigaChat", response))

            result = response.json()
            choices = result.get("choices", [])
            if not choices:
                raise Exception("Пустой ответ от модели")

            content = choices[0]["message"]["content"]
            logger.debug(f"Получен ответ от модели: {content[:100]}...")
            return content

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения: {e}")
            raise Exception(f"Ошибка соединения: {e}")

    def test_connection(self) -> bool:
        """Тестирование подключения к API."""
        try:
            self.get_access_token()
            models = self.get_available_models()
            logger.info(f"Подключение успешно. Доступны модели: {models}")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            return False

    def _format_error(self, message: str, response: requests.Response) -> str:
        """Форматирование сообщения об ошибке."""
        error_msg = f"{message}: {response.status_code}"
        try:
            error_msg += f"\nДетали: {response.json()}"
        except Exception:
            error_msg += f"\nОтвет: {response.text}"
        return error_msg