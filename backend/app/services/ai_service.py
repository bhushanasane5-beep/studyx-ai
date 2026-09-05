"""Single integration boundary for NVIDIA NIM AI requests."""

from __future__ import annotations

import httpx

from app.core.config import Settings, get_settings


class AIServiceError(Exception):
    """A safe, user-facing failure from the configured AI provider."""


class AIService:
    """Owns all NVIDIA NIM communication for the backend."""

    _chat_url = "https://integrate.api.nvidia.com/v1/chat/completions"

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    @property
    def model(self) -> str:
        """Return the configured NVIDIA model identifier."""
        return self._settings.nvidia_model

    async def chat(self, message: str) -> str:
        """Send one student message to NVIDIA NIM and return its reply."""
        return await self._create_response(
            [
                {
                    "role": "system",
                    "content": (
                        "You are StudyX AI, a helpful student learning assistant. "
                        "Reply in the same language as the student. Support English, "
                        "Hindi, and natural Hinglish. Be clear, accurate, and concise."
                    ),
                },
                {"role": "user", "content": message},
            ],
            max_tokens=700,
        )

    async def summarize(self, document_text: str) -> str:
        """Create clear study notes from extracted PDF text."""
        return await self._create_response(
            [
                {
                    "role": "system",
                    "content": (
                        "You are StudyX AI, a helpful student learning assistant. "
                        "Create a clear study summary from the supplied PDF text. "
                        "Preserve important definitions, concepts, formulas, and examples. "
                        "Use helpful headings and short bullet points. Reply in the main "
                        "language used by the document; use natural Hindi or Hinglish when appropriate."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Summarize these study notes:\n\n{document_text}",
                },
            ],
            max_tokens=1_200,
        )

    async def _create_response(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        """Make a validated chat-completion request to NVIDIA NIM."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self._settings.nvidia_api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(self._chat_url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
            content = data["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("The response did not include message content.")
            return content.strip()
        except httpx.TimeoutException as error:
            raise AIServiceError("The AI service took too long to respond. Please try again.") from error
        except httpx.HTTPStatusError as error:
            raise AIServiceError("The AI service is unavailable right now. Please try again.") from error
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as error:
            raise AIServiceError("Unable to get an AI response right now. Please try again.") from error


ai_service = AIService()
