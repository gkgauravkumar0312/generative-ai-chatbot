"""
Streamlit UI for the Generative AI chatbot.

This file handles layout, session memory, and user interaction.
API calls live in chatbot.py so the UI stays easy to read.
"""

import streamlit as st

from chatbot import ChatbotError, get_model_name, get_response
from prompts import SYSTEM_PROMPT


def init_session() -> None:
    """Create conversation history on first load of this browser session."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
    if "model_name" not in st.session_state:
        st.session_state.model_name = get_model_name()


def reset_chat() -> None:
    """Clear the conversation but keep the system prompt."""
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]


def render_sidebar() -> None:
    """Settings panel: show the model and allow clearing chat history."""
    with st.sidebar:
        st.header("Settings")
        st.caption("The API key is loaded from your `.env` file and is never shown here.")

        st.text_input(
            "Model",
            value=st.session_state.model_name,
            disabled=True,
            help="Change OPENAI_MODEL in your .env file, then restart the app.",
        )

        if st.button("Clear Chat", use_container_width=True, type="primary"):
            reset_chat()
            st.rerun()

        st.divider()
        st.markdown(
            "Conversation memory lasts for this browser session only. "
            "Clearing the chat or refreshing the page starts a new conversation."
        )


def render_chat_history() -> None:
    """Display user and assistant messages using Streamlit chat bubbles."""
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_message(user_text: str) -> None:
    """Append the user message, call the model, then show the reply."""
    user_text = user_text.strip()
    if not user_text:
        st.warning("Please enter a message before sending.")
        return

    st.session_state.messages.append({"role": "user", "content": user_text})

    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                reply = get_response(
                    st.session_state.messages,
                    model=st.session_state.model_name,
                )
        except ChatbotError as error:
            st.error(str(error))
            st.session_state.messages.pop()
            return

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})


def main() -> None:
    st.set_page_config(
        page_title="AI Chatbot",
        page_icon="💬",
        layout="centered",
    )

    init_session()

    st.markdown(
        """
        <style>
            .block-container { padding-top: 2rem; padding-bottom: 2rem; }
            [data-testid="stSidebar"] { min-width: 260px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("AI Chatbot")
    st.caption("Generative AI Assistant powered by OpenAI")

    render_sidebar()
    render_chat_history()

    prompt = st.chat_input("Ask a question...")
    if prompt:
        handle_user_message(prompt)


if __name__ == "__main__":
    main()
