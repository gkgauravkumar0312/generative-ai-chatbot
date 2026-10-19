"""
Chatbot service: talks to the OpenAI API.

This module does not know about Streamlit. It only:
- reads configuration from environment variables
- sends conversation history to the model
- returns the assistant's reply or a user-friendly error
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import APIConnectionError, APIError, AuthenticationError, OpenAI, RateLimitError

# Always load .env from this project folder, not the process working directory.
# Streamlit may keep this module imported, so we also reload before each request.
_ENV_FILE = Path(__file__).resolve().parent / ".env"


def _load_env() -> None:
    """Load OPENAI_* values from the project .env file."""
    load_dotenv(_ENV_FILE)
    # An empty OPENAI_API_KEY already in the OS environment would otherwise
    # block python-dotenv (it does not override existing variables by default).
    if not os.getenv("OPENAI_API_KEY", "").strip():
        load_dotenv(_ENV_FILE, override=True)


class ChatbotError(Exception):
    """Raised when the chatbot cannot produce a response."""


def _get_api_key() -> str:
    """Return the OpenAI API key or raise a clear configuration error."""
    _load_env()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "your_api_key_here":
        raise ChatbotError(
            "OpenAI API key is missing. Add OPENAI_API_KEY to your .env file "
            "and restart the app."
        )
    return api_key


def get_model_name() -> str:
    """Return the configured model name, with a safe default."""
    _load_env()
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"


def get_client() -> OpenAI:
    """Create an OpenAI client using the key from the environment."""
    return OpenAI(api_key=_get_api_key())


def get_response(messages: list[dict], model: str | None = None) -> str:
    """
    Send conversation history to the LLM and return the assistant reply.

    messages: list of {"role": "system"|"user"|"assistant", "content": "..."}
    model: optional model override from the UI; otherwise uses OPENAI_MODEL
    """
    if not messages:
        raise ChatbotError("No conversation history was provided.")

    selected_model = (model or get_model_name()).strip()
    if not selected_model:
        raise ChatbotError("No OpenAI model is configured. Set OPENAI_MODEL in .env.")

    try:
        client = get_client()
        completion = client.chat.completions.create(
            model=selected_model,
            messages=messages,
        )
    except AuthenticationError:
        raise ChatbotError(
            "The OpenAI API key is invalid. Check OPENAI_API_KEY in your .env file."
        ) from None
    except RateLimitError:
        raise ChatbotError(
            "The OpenAI API rate limit was reached. Please wait a moment and try again."
        ) from None
    except APIConnectionError:
        raise ChatbotError(
            "Could not connect to OpenAI. Check your internet connection and try again."
        ) from None
    except APIError:
        raise ChatbotError(
            "The OpenAI service returned an error. Please try again in a moment."
        ) from None
    except ChatbotError:
        raise
    except Exception:
        raise ChatbotError(
            "Something went wrong while generating a response. Please try again."
        ) from None

    try:
        content = completion.choices[0].message.content
    except (AttributeError, IndexError, TypeError):
        raise ChatbotError(
            "Received an unexpected response from the model. Please try again."
        ) from None

    if not content or not str(content).strip():
        raise ChatbotError(
            "The model returned an empty response. Please try again."
        )

    return str(content).strip()
