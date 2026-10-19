"""
Chatbot service: talks to the Google Gemini API.

This module:
- Loads configuration from environment variables
- Sends conversation history to Gemini
- Returns the assistant's reply
- Provides useful error messages without exposing the API key
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors


_ENV_FILE = Path(__file__).resolve().parent / ".env"


class ChatbotError(Exception):
    """Raised when the chatbot cannot produce a response."""


def _load_env() -> None:
    """Load Gemini configuration from the project .env file."""
    load_dotenv(_ENV_FILE)

    if not os.getenv("GEMINI_API_KEY", "").strip():
        load_dotenv(_ENV_FILE, override=True)


def _get_api_key() -> str:
    """Get the Gemini API key."""
    _load_env()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key or api_key == "your_api_key_here":
        raise ChatbotError(
            "Gemini API key is missing. Add GEMINI_API_KEY "
            "to Streamlit Secrets or your local .env file."
        )

    return api_key


def get_model_name() -> str:
    """Return the configured Gemini model."""
    _load_env()
    return (
        os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        or "gemini-2.5-flash"
    )


def get_client():
    """Create a Gemini API client."""
    return genai.Client(api_key=_get_api_key())


def get_response(messages: list[dict], model: str | None = None) -> str:
    """
    Send conversation history to Gemini.

    Expected messages:
    [{"role": "system"|"user"|"assistant", "content": "..."}]
    """
    if not messages:
        raise ChatbotError("No conversation history was provided.")

    selected_model = (model or get_model_name()).strip()

    if not selected_model:
        raise ChatbotError("No Gemini model is configured.")

    system_parts = []
    conversation = []

    for message in messages:
        role = message.get("role")
        content = str(message.get("content", ""))

        if role == "system":
            if content.strip():
                system_parts.append(content)

        elif role == "user":
            conversation.append({
                "role": "user",
                "parts": [{"text": content}],
            })

        elif role == "assistant":
            conversation.append({
                "role": "model",
                "parts": [{"text": content}],
            })

    if not conversation or conversation[-1]["role"] != "user":
        raise ChatbotError("The latest message must be from the user.")

    config = {}
    if system_parts:
        config["system_instruction"] = "\n\n".join(system_parts)

    try:
        client = get_client()

        response = client.models.generate_content(
            model=selected_model,
            contents=conversation,
            config=config or None,
        )

    except ChatbotError:
        raise

    except errors.APIError as exc:
        status = getattr(exc, "code", None)
        details = str(exc)

        # Avoid accidentally exposing credentials in an error message.
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if api_key:
            details = details.replace(api_key, "[REDACTED]")

        if status in (401, 403):
            message = (
                "Gemini authentication or permission error. "
                "Check your API key and API access."
            )
        elif status == 429:
            message = (
                "Gemini quota or rate limit error. "
                "Check your Google AI Studio usage and limits."
            )
        elif status == 404:
            message = (
                f"Gemini model '{selected_model}' was not found "
                "or is unavailable to this API key."
            )
        elif status == 400:
            message = "Gemini rejected the request. Check the model and request configuration."
        else:
            message = f"Gemini API error (HTTP {status})."

        # Diagnostic details help identify the cause.
        # The API key itself is never intentionally displayed.
        if details:
            message += f"\nDetails: {details[:500]}"

        raise ChatbotError(message) from None

    except Exception as exc:
        error_type = type(exc).__name__
        raise ChatbotError(
            f"Unexpected error ({error_type}). "
            "Check the app configuration and Streamlit logs."
        ) from None

    try:
        content = response.text
    except (AttributeError, TypeError):
        content = None

    if not content or not content.strip():
        raise ChatbotError(
            "Gemini returned no text. The response may have been blocked "
            "or contained no text content."
        )

    return content.strip()
    



