"""Тесты для клиента GigaChat."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from src.client import GigaChatClient


class TestGigaChatClient:
    """Тесты клиента GigaChat API."""

    @pytest.fixture
    def client(self):
        return GigaChatClient("test_auth_key")

    def test_init(self, client):
        assert client.auth_key == "test_auth_key"
        assert client.access_token is None
        assert client.token_expiry is None

    @patch("src.client.requests.post")
    def test_get_access_token_success(self, mock_post, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = mock_response

        token = client.get_access_token()

        assert token == "test_token"
        assert client.access_token == "test_token"
        assert client.token_expiry is not None

    @patch("src.client.requests.post")
    def test_get_access_token_cached(self, mock_post, client):
        client.access_token = "cached"
        client.token_expiry = datetime.now() + timedelta(minutes=10)

        token = client.get_access_token()

        assert token == "cached"
        mock_post.assert_not_called()

    @patch("src.client.requests.post")
    def test_get_access_token_error(self, mock_post, client):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "unauthorized"
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="Ошибка получения токена"):
            client.get_access_token()

    @patch("src.client.requests.post")
    def test_get_access_token_no_token(self, mock_post, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="Access token не найден"):
            client.get_access_token()

    @patch("src.client.requests.get")
    def test_get_available_models(self, mock_get, client):
        client.access_token = "test_token"
        client.token_expiry = datetime.now()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"id": "GigaChat"}, {"id": "GigaChat-Pro"}]
        }
        mock_get.return_value = mock_response

        models = client.get_available_models()

        assert "GigaChat" in models
        assert "GigaChat-Pro" in models

    @patch("src.client.requests.post")
    def test_chat_completion_success(self, mock_post, client):
        client.access_token = "test_token"
        client.token_expiry = datetime.now()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response

        response = client.chat_completion(messages=[{"role": "user", "content": "Hello"}])

        assert response == "Test response"

    @patch("src.client.requests.post")
    def test_chat_completion_empty(self, mock_post, client):
        client.access_token = "test_token"
        client.token_expiry = datetime.now()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": []}
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="Пустой ответ"):
            client.chat_completion(messages=[{"role": "user", "content": "Hello"}])