"""
Chatbot service: talks to the Google Gemini API.

This module does not know about Streamlit. It only:
- reads configuration from environment variables
- sends conversation history to the model
- returns the assistant's reply or a user-friendly error
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors

_ENV_FILE = Path(__file__).resolve().parent / ".env"


def _load_env() -> None:
    """Load GEMINI_* values from the project .env file."""
    load_dotenv(_ENV_FILE)

    if not os.getenv("GEMINI_API_KEY", "").strip():
        load_dotenv(_ENV_FILE, override=True)


class ChatbotError(Exception):
    """Raised when the chatbot cannot produce a response."""


def _get_api_key() -> str:
    """Return the Gemini API key or raise a configuration error."""
    _load_env()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key or api_key == "your_api_key_here":
        raise ChatbotError(
            "Gemini API key is missing. Add GEMINI_API_KEY to your .env file."
        )

    return api_key


def get_model_name() -> str:
    """Return the configured Gemini model name."""
    _load_env()
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"


def get_client():
    """Create a Gemini client using the configured API key."""
    return genai.Client(api_key=_get_api_key())


def get_response(messages: list[dict], model: str | None = None) -> str:
    """
    Send conversation history to Gemini and return the assistant reply.

    messages: list of {"role": "system"|"user"|"assistant", "content": "..."}
    model: optional model override from the UI.
    """
    if not messages:
        raise ChatbotError("No conversation history was provided.")

    selected_model = (model or get_model_name()).strip()

    if not selected_model:
        raise ChatbotError("No Gemini model is configured. Set GEMINI_MODEL in .env.")

    system_parts = []
    conversation = []

    for message in messages:
        role = message.get("role")
        content = str(message.get("content", ""))

        if role == "system":
            system_parts.append(content)
        elif role == "user":
            conversation.append({"role": "user", "parts": [{"text": content}]})
        elif role == "assistant":
            conversation.append({"role": "model", "parts": [{"text": content}]})

    if not conversation or conversation[-1]["role"] != "user":
        raise ChatbotError("The latest message must be from the user.")

    try:
        client = get_client()

        config = {}
        if system_parts:
            config["system_instruction"] = "\n\n".join(system_parts)

        response = client.models.generate_content(
            model=selected_model,
            contents=conversation,
            config=config or None,
        )

    except errors.APIError as exc:
        status = getattr(exc, "code", None)

        if status in (401, 403):
            raise ChatbotError(
                "The Gemini API key is invalid or does not have access. "
                "Check GEMINI_API_KEY."
            ) from None

        if status == 429:
            raise ChatbotError(
                "The Gemini API rate limit was reached. Please wait and try again."
            ) from None

        raise ChatbotError(
            "The Gemini service returned an error. Please try again."
        ) from None

    except ChatbotError:
        raise
    except Exception:
        raise ChatbotError(
            "Could not connect to Gemini or generate a response. "
            "Check your internet connection and API configuration."
        ) from None

    try:
        content = response.text
    except (AttributeError, TypeError):
        content = None

    if not content or not content.strip():
        raise ChatbotError(
            "Gemini returned an empty response. Please try again."
        )

    return content.strip()



