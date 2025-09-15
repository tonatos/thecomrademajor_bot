"""GigaChat API client implementation."""

import base64
import logging
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger(__name__)


class GigaChatMessage(BaseModel):
    """GigaChat message model."""

    role: str
    content: str


class GigaChatRequest(BaseModel):
    """GigaChat API request model."""

    model: str = "GigaChat"
    messages: list[GigaChatMessage]
    temperature: float = 0.7
    max_tokens: int = 300


class GigaChatResponse(BaseModel):
    """GigaChat API response model."""

    choices: list[Dict[str, Any]]
    usage: Dict[str, Any]


class GigaChatClient:
    """Client for interacting with GigaChat API."""

    def __init__(self) -> None:
        """Initialize GigaChat client."""
        self.base_url = "https://gigachat.devices.sberbank.ru/api/v1"
        self.token_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.access_token: Optional[str] = None
        self.client = httpx.AsyncClient(
            verify=False
        )  # SSL verification disabled for GigaChat

    async def _get_access_token(self) -> str:
        """Get access token from GigaChat API."""
        if self.access_token:
            return self.access_token

        # Create authorization header
        credentials = f"{settings.gigachat_client_id}:{settings.gigachat_client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "RqUID": "6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e",  # Required UUID
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {"scope": settings.gigachat_scope}

        try:
            response = await self.client.post(
                self.token_url, headers=headers, data=data
            )
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data["access_token"]
            logger.info("Successfully obtained GigaChat access token")
            return self.access_token
        except Exception as e:
            logger.error(f"Failed to get GigaChat access token: {e}")
            raise

    async def generate_response(self, user_message: str) -> str:
        """Generate response using GigaChat API."""
        try:
            token = await self._get_access_token()

            # Create the prompt for the major character
            system_prompt = (
                "Представь, что ты майор полиции. Ты очень злой и суровый полицейский. "
                "Ты видишь в сообщениях угрозу законам РФ и должен предупредить автора "
                "об административной или уголовной ответственности. "
                "Даже если в сообщении "
                "нет явных признаков нарушения законов, придумай их! Пофантазируй - "
                "если не удается подобрать настоящие статьи, то можешь их придумать."
                "Сформулируй небольшой, но экспрессивный (в пределах 300 символов)."
            )

            # Prompt is not used directly in the request, removed unused variable

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            request_data = GigaChatRequest(
                messages=[
                    GigaChatMessage(role="system", content=system_prompt),
                    GigaChatMessage(
                        role="user",
                        content=f"Проанализируй это сообщение: {user_message}",
                    ),
                ]
            )

            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=request_data.model_dump(),
            )

            if response.status_code == 401:
                # Token expired, reset and retry
                self.access_token = None
                token = await self._get_access_token()
                headers["Authorization"] = f"Bearer {token}"
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=request_data.model_dump(),
                )

            response.raise_for_status()
            response_data = response.json()

            if response_data.get("choices") and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"]
                return (
                    str(content) if content else "🚔 ВНИМАНИЕ! Пустой ответ от системы!"
                )
            else:
                return (
                    "🚔 ВНИМАНИЕ! Не могу проанализировать ваше сообщение, "
                    "но подозреваю нарушение общественного порядка!"
                )

        except Exception as e:
            logger.error(f"Failed to generate GigaChat response: {e}")
            return (
                "🚔 ВНИМАНИЕ ГРАЖДАНЕ! Технические неполадки в системе, "
                "но это не отменяет вашу ответственность перед законом!"
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
