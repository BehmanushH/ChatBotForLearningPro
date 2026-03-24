"""BanuCode - bilingual tutoring chatbot UI (Streamlit)."""

from datetime import datetime
import html

import streamlit as st

from llm_handler import get_llm_handler
from translations import get_all_translations
import streamlit.components.v1 as components

st.set_page_config(
    page_title="BanuCode",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background: #f3f5f9;
            }
            .block-container {
                max-width: 1240px;
                padding-top: 0.35rem;
                padding-bottom: 0.2rem;
            }
            header[data-testid="stHeader"] {
                background: transparent;
                height: 0;
            }
            footer {
                visibility: hidden;
                height: 0;
            }
            .bc-hero {
                background: linear-gradient(135deg, #0f4c81 0%, #1b5f9e 55%, #2f6ea8 100%);
                color: #f8fafc;
                border-radius: 12px;
                padding: 18px 20px;
                margin-bottom: 10px;
            }
            .bc-title {
                font-size: 1.7rem;
                font-weight: 700;
                margin: 0 0 4px 0;
            }
            .bc-subtitle {
                margin: 0;
                color: #e6edf8;
                font-size: 0.96rem;
                line-height: 1.45;
            }
            .bc-rail-title {
                font-size: 0.9rem;
                font-weight: 700;
                margin: 8px 0 10px 0;
                color: #1e293b;
            }
            .bc-chat-scroll {
                height: 54vh;
                min-height: 320px;
                max-height: 540px;
                overflow-y: auto;
                padding-right: 2px;
            }
            .bc-msg {
                padding: 8px 0;
                margin-bottom: 8px;
            }
            .bc-msg-meta {
                display: flex;
                justify-content: space-between;
                font-size: 0.78rem;
                color: #475569;
                margin-bottom: 4px;
                font-weight: 600;
            }
            .bc-msg-body {
                font-size: 0.93rem;
                line-height: 1.48;
                color: #0f172a;
                word-break: break-word;
            }
            div[data-testid="stButton"] > button {
                border-radius: 8px;
                border: 1px solid #cfd8e6;
                background: #f8fafd;
                color: #1e293b;
                font-size: 0.88rem;
                font-weight: 500;
            }
            div[data-testid="stButton"] > button:hover {
                border-color: #9fb6d8;
                color: #0f4c81;
            }
            div[data-testid="stSelectbox"] div[data-baseweb="select"] {
                border-color: #cfd8e6;
                border-radius: 10px;
            }
            div[data-testid="stChatInput"] {
                border-top: 0;
                padding-top: 0.3rem;
                background: transparent;
            }
            div[data-testid="stChatInput"] textarea {
                background: #edf2fa !important;
                border: 0 !important;
                border-radius: 8px !important;
                box-shadow: inset 0 0 0 1px #d3dced !important;
            }
            #bc-chat-container {
                display: flex;
                flex-direction: column;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _default_chat_title(t: dict) -> str:
    return t.get("new_chat_title", "New Chat")


def _create_chat(t: dict, messages: list[dict] | None = None) -> dict:
    now = datetime.now().isoformat()
    return {
        "id": now,
        "title": _default_chat_title(t),
        "messages": messages or [],
        "created_at": now,
        "updated_at": now,
    }


def _init_state(t: dict) -> None:
    if "language" not in st.session_state:
        st.session_state.language = "en"
    if "model_handler" not in st.session_state:
        st.session_state.model_handler = get_llm_handler()
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 512

    if "chats" not in st.session_state:
        st.session_state.chats = [_create_chat(t)]
        st.session_state.active_chat_id = st.session_state.chats[0]["id"]

    if not st.session_state.chats:
        st.session_state.chats = [_create_chat(t)]
        st.session_state.active_chat_id = st.session_state.chats[0]["id"]

    valid_ids = {chat["id"] for chat in st.session_state.chats}
    if st.session_state.get("active_chat_id") not in valid_ids:
        st.session_state.active_chat_id = st.session_state.chats[0]["id"]


def _active_chat() -> dict:
    for chat in st.session_state.chats:
        if chat["id"] == st.session_state.active_chat_id:
            return chat
    return st.session_state.chats[0]


def _set_active_chat(chat_id: str) -> None:
    st.session_state.active_chat_id = chat_id


def _start_new_chat(t: dict) -> None:
    new_chat = _create_chat(t)
    st.session_state.chats.insert(0, new_chat)
    st.session_state.active_chat_id = new_chat["id"]
    st.rerun()


def _clear_current_chat(t: dict) -> None:
    chat = _active_chat()
    chat["messages"] = []
    chat["title"] = _default_chat_title(t)
    chat["updated_at"] = datetime.now().isoformat()
    st.rerun()


def _append_to_active_chat(role: str, content: str, t: dict, usage: dict | None = None) -> None:
    chat = _active_chat()
    chat["messages"].append(
        {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "language": st.session_state.language,
            "usage": usage or {},
        }
    )
    if role == "user" and chat["title"] == _default_chat_title(t):
        chat["title"] = content.strip().replace("\n", " ")[:42]
    chat["updated_at"] = datetime.now().isoformat()


def _send_prompt(prompt: str, t: dict) -> None:
    clean = prompt.strip()
    if not clean:
        return

    _append_to_active_chat("user", clean, t)

    with st.spinner(t["please_wait"]):
        response = st.session_state.model_handler.generate_response(
            prompt=clean,
            temperature=st.session_state.temperature,
            max_tokens=st.session_state.max_tokens,
            language=st.session_state.language,
        )

    usage = st.session_state.model_handler.get_last_usage()
    _append_to_active_chat("bot", response, t, usage=usage)
    st.rerun()


def _latest_messages(messages: list[dict], limit: int = 10) -> list[dict]:
    if len(messages) <= limit:
        return messages
    return messages[-limit:]


def _render_chat_html(messages: list[dict]) -> str:
    rows = []
    for msg in messages:
        is_user = msg["role"] == "user"
        role_label = "You" if is_user else "BanuCode"
        role_icon = "🧑" if is_user else "🧠"
        safe_content = html.escape(msg["content"]).replace("\n", "<br>")
        msg_time = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M")
        usage = msg.get("usage", {}) if isinstance(msg, dict) else {}
        usage_text = ""
        if (not is_user) and isinstance(usage, dict) and usage.get("total_tokens"):
            usage_text = (
                f" | tok: {int(usage.get('prompt_tokens', 0))}/"
                f"{int(usage.get('completion_tokens', 0))}/"
                f"{int(usage.get('total_tokens', 0))}"
            )
        rows.append(
            (
                '<div class="bc-msg">'
                f'<div class="bc-msg-meta"><span>{role_icon} {role_label}</span><span>{msg_time}{usage_text}</span></div>'
                f'<div class="bc-msg-body">{safe_content}</div>'
                "</div>"
            )
        )
    return "".join(rows)


if "language" not in st.session_state:
    st.session_state.language = "en"

trans = get_all_translations(st.session_state.language)
_init_state(trans)
_inject_styles()

current_chat = _active_chat()
current_messages = current_chat["messages"]

history_col, center_col = st.columns([1.08, 2.92], gap="medium")

with history_col:
    selected_language = st.selectbox(
        trans["language_label"],
        options=["en", "dari"],
        index=0 if st.session_state.language == "en" else 1,
        format_func=lambda x: "English | انگریزی" if x == "en" else "Dari | دری",
        key="language_picker",
    )
    if selected_language != st.session_state.language:
        st.session_state.language = selected_language
        st.rerun()

    if st.button(trans["new_chat"], use_container_width=True, type="primary"):
        _start_new_chat(trans)

    st.markdown(f'<div class="bc-rail-title">{trans["chat_history"]}</div>', unsafe_allow_html=True)
    for chat in st.session_state.chats:
        title = chat["title"] if chat["title"] else _default_chat_title(trans)
        active = chat["id"] == st.session_state.active_chat_id
        label = f"● 💬 {title}" if active else f"💬 {title}"
        if st.button(label, key=f"chat_{chat['id']}", use_container_width=True, type="secondary"):
            _set_active_chat(chat["id"])
            st.rerun()

    if st.button(trans["clear_history"], use_container_width=True, type="secondary", key="clear_current"):
        _clear_current_chat(trans)

with center_col:
    st.markdown(
        f"""
        <div class="bc-hero">
            <div class="bc-title">🧠 BanuCode</div>
            <p class="bc-subtitle">{trans['chatbot_description']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not current_messages:
        st.markdown(f'<div class="bc-rail-title">{trans["example_prompts"]}</div>', unsafe_allow_html=True)
        prompt_cols = st.columns(2)
        for idx, example in enumerate(trans["example_prompt_items"]):
            with prompt_cols[idx % 2]:
                if st.button(example, key=f"example_{idx}", use_container_width=True):
                    _send_prompt(example, trans)

    visible = _latest_messages(current_messages, limit=10)

    st.markdown(f'<div id="bc-chat-container" class="bc-chat-scroll">{_render_chat_html(visible)}</div>', unsafe_allow_html=True)

    components.html(
        """
        <script>
            setTimeout(() => {
                const container = document.getElementById('bc-chat-container');
                if (container) {
                    container.parentElement.scrollTop = container.parentElement.scrollHeight;
                }
            }, 100);
        </script>
        """,
        height=0,
    )

prompt = st.chat_input(trans["user_input_placeholder"])
if prompt:
    _send_prompt(prompt, trans)



