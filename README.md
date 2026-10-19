# AI Chatbot using Generative AI

A clean, beginner-friendly Generative AI chatbot built with **Python**, **Streamlit**, and the **OpenAI API**. It answers questions, remembers conversation context during a session, and is ready for local use, GitHub, and deployment.

This project is designed so every file has a clear job. You should be able to explain the full request-response flow in an interview.

---

## Overview

The app is a chat interface in the browser. When you send a message, Streamlit stores it in session memory, a small Python service sends the full conversation to OpenAI, and the assistant reply is shown in the chat window.

Secrets stay in a local `.env` file. They are never hardcoded and never shown in the UI.

---

## Features

- LLM-powered conversations
- Conversation memory for the current session
- Prompt engineering via a dedicated system prompt
- OpenAI API integration (current Python SDK)
- Secure environment variables (`.env`)
- Modern Streamlit chat UI
- User-friendly error handling
- Clear chat functionality
- Configurable model name
- GitHub-ready project layout

---

## Architecture

```
User
 ↓
Streamlit UI (app.py)
 ↓
Conversation History (st.session_state)
 ↓
Python Chatbot Service (chatbot.py)
 ↓
OpenAI API
 ↓
Generated Response
 ↓
Streamlit UI
```

1. The user types a message in the Streamlit chat input.
2. The app appends that message to `st.session_state.messages`.
3. `get_response()` sends the full message list (system + history) to OpenAI.
4. The model returns an assistant reply.
5. The reply is stored in session state and rendered as a chat bubble.

---

## Tech Stack

- Python 3.11+
- Streamlit
- OpenAI API (official Python SDK)
- python-dotenv

LangChain is intentionally not used so the architecture stays easy to explain.

---

## Project Structure

```
ai-chatbot/
├── app.py              # Streamlit UI, session memory, sidebar, chat flow
├── chatbot.py          # OpenAI client, API calls, error handling
├── prompts.py          # System prompt (assistant behavior)
├── requirements.txt    # Python dependencies
├── .env.example        # Placeholder environment variables (no secrets)
├── .gitignore          # Ignores .env, venv, cache, editor files
├── README.md           # Project documentation
└── screenshots/        # Optional UI screenshots for GitHub
    └── .gitkeep
```

| File | Responsibility |
| --- | --- |
| `app.py` | User interface. Initializes chat history, displays messages, handles input, clear-chat, and loading state. |
| `chatbot.py` | Talks to OpenAI. Reads `OPENAI_API_KEY` and `OPENAI_MODEL`, sends messages, returns the reply. |
| `prompts.py` | Holds the system prompt so behavior can be changed without touching API or UI code. |
| `requirements.txt` | Exact libraries needed to run the app. |
| `.env.example` | Template for local setup. Copy to `.env` and add your own key. |
| `.gitignore` | Prevents secrets, virtualenvs, and cache files from being committed. |
| `screenshots/` | Place for README images after you run the app. |

---

## Installation

```bash
git clone <repository-url>
cd ai-chatbot
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Setup

1. Copy the example file:

```bash
copy .env.example .env
```

On Linux/macOS:

```bash
cp .env.example .env
```

2. Edit `.env` and add your values:

```
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
```

Get an API key from [OpenAI](https://platform.openai.com/api-keys).

**Never commit `.env` or paste your API key into GitHub, README, or source code.**  
`.gitignore` already excludes `.env`.

---

## Run

```bash
streamlit run app.py
```

The app opens in your browser (usually `http://localhost:8501`).

---

## How It Works

1. Streamlit starts `app.py` and builds the page.
2. On first load, `st.session_state.messages` is created with the system prompt from `prompts.py`.
3. Previous user and assistant messages (if any) are drawn with `st.chat_message`.
4. The user submits text through `st.chat_input`.
5. The user message is added to history.
6. `chatbot.get_response(messages)` calls `client.chat.completions.create(...)`.
7. OpenAI returns `choices[0].message.content`.
8. That text is appended as an `assistant` message and shown in the UI.

If the key is missing, invalid, or the network fails, `chatbot.py` raises a `ChatbotError` and `app.py` shows a friendly `st.error` without leaking secrets.

---

## Conversation Memory

Streamlit reruns the script on every interaction. Without `st.session_state`, chat history would disappear.

This app stores a list of message dictionaries:

```python
{"role": "system" | "user" | "assistant", "content": "..."}
```

Each API call sends the **full list**, so the model can recall earlier turns (for example, your name) until you click **Clear Chat** or refresh the page.

---

## Future Improvements

- PDF Q&A / RAG (retrieve answers from your documents)
- Voice input and output
- Persistent chat history in a database
- Multiple LLM providers (Anthropic, Gemini, local models)
- Web search for live information
- User authentication
- Multi-agent architecture

---

## Resume Description

Built a production-style Generative AI chatbot using Python, Streamlit, and the OpenAI API, with session-based conversation memory, secure environment-variable configuration, modular prompt and API layers, and user-friendly error handling.

---

## Security

- API keys live only in `.env`
- `.env` is listed in `.gitignore`
- The UI never displays the API key
- Error messages do not include secrets or raw exception dumps
