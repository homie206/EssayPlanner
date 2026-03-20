import importlib.util
import time
from pathlib import Path

import requests
import streamlit as st

# Load agent_config.py directly (by file path) to avoid triggering
# bin/RichUI/__init__.py, which imports heavy orchestrator/agent deps.
_spec = importlib.util.spec_from_file_location(
    "agent_config",
    Path(__file__).resolve().parents[1] / "RichUI" / "agent_config.py",
)
_agent_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_agent_config)
AGENT_CONFIG = _agent_config.AGENT_CONFIG


st.set_page_config(page_title="MultiAgentSystem UI", layout="centered")


# ----------------------------
# Helpers
# ----------------------------

# Build reverse lookup: state_key -> agent_name
_STATE_KEY_TO_AGENT = {}
for _name, _cfg in AGENT_CONFIG.items():
    _STATE_KEY_TO_AGENT[_cfg["state_key"]] = _name
    # Also map the _reply key for idea_structurer (its state_key is idea_board)
    _STATE_KEY_TO_AGENT[f"{_name}_reply"] = _name


def post_json(url: str, payload: dict, timeout: int = 300) -> dict:
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


def role_from_key(node: str, key: str) -> str:
    """Map state keys / nodes to agent names using AGENT_CONFIG."""
    if key in _STATE_KEY_TO_AGENT:
        return _STATE_KEY_TO_AGENT[key]
    return node or "system"


def should_display(key: str, value) -> bool:
    """Only show agent replies (NOT the idea_board raw value)."""
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != "" and key.endswith("_reply")
    return False


def render_chat_message(role: str, content: str):
    """Render a single chat message using st.chat_message()."""
    if role == "user":
        with st.chat_message("user", avatar="✨"):
            st.markdown(content)
    else:
        cfg = AGENT_CONFIG.get(role)
        if cfg:
            with st.chat_message(name=cfg["label"], avatar=cfg["emoji"]):
                st.markdown(
                    f'<div style="'
                    f'background:{cfg["bg_color"]};'
                    f'border-left:4px solid {cfg["st_color"]};'
                    f'border-radius:0.4rem;'
                    f'padding:0.6rem 0.8rem;'
                    f'margin:-0.25rem 0">'
                    f'<p style="margin:0 0 0.3rem 0;font-size:0.75rem;'
                    f'font-weight:700;color:{cfg["st_color"]};'
                    f'text-transform:uppercase;letter-spacing:0.05em">'
                    f'{cfg["emoji"]} {cfg["label"]}</p>'
                    f'{content}</div>',
                    unsafe_allow_html=True,
                )
        else:
            with st.chat_message("assistant"):
                st.markdown(content)


def process_events(resp: dict):
    """
    Process events from the backend response.

    resp:
      {
        "thread_id": "...",
        "events": [[node, key, value], ...],
        "needs_user_input": bool,
        "interrupt_prompt": str|None
      }
    """
    events = resp.get("events", [])
    for e in events:
        if not (isinstance(e, (list, tuple)) and len(e) == 3):
            continue
        node, key, value = e

        # Interrupt event
        if node == "__interrupt__":
            st.session_state.needs_user_input = True
            st.session_state.interrupt_prompt = str(value)
            continue

        # Avoid duplicate displays
        last_val = st.session_state.last_values.get(key)
        if last_val == value:
            continue
        st.session_state.last_values[key] = value

        # Track idea_board state in session
        if key == "idea_board" and value is not None:
            st.session_state.idea_board = str(value)

        # Push displayable agent messages into chat log
        if should_display(str(key), value):
            st.session_state.chat.append(
                {"role": role_from_key(str(node), str(key)), "content": str(value)}
            )

    st.session_state.needs_user_input = bool(resp.get("needs_user_input", False))
    st.session_state.interrupt_prompt = resp.get("interrupt_prompt")


# ----------------------------
# Session state init
# ----------------------------

if "server_url" not in st.session_state:
    st.session_state.server_url = "http://127.0.0.1:8000"
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "chat" not in st.session_state:
    st.session_state.chat = []
if "last_values" not in st.session_state:
    st.session_state.last_values = {}
if "needs_user_input" not in st.session_state:
    st.session_state.needs_user_input = False
if "interrupt_prompt" not in st.session_state:
    st.session_state.interrupt_prompt = None
if "idea_board" not in st.session_state:
    st.session_state.idea_board = None


# ----------------------------
# UI
# ----------------------------

st.title("AI 4 ED")

with st.sidebar:
    st.subheader("Server")
    st.session_state.server_url = st.text_input(
        "FastAPI base URL", st.session_state.server_url
    )
    st.caption("Backend should expose: POST /start and POST /message/{thread_id}")

    st.markdown("---")

    # Agent legend
    with st.expander("Agent Roles", expanded=True):
        st.markdown("✨ **You** — your messages")
        for cfg in AGENT_CONFIG.values():
            swatch = (
                f'<span style="display:inline-block;width:12px;height:12px;'
                f'border-radius:3px;background:{cfg["bg_color"]};'
                f'border:2px solid {cfg["st_color"]};vertical-align:middle;'
                f'margin-right:6px;"></span>'
            )
            st.markdown(
                f'{swatch}{cfg["emoji"]} **{cfg["label"]}**',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Idea Board
    with st.expander("Idea Board", expanded=True):
        if st.session_state.idea_board:
            st.markdown(st.session_state.idea_board)
        else:
            st.caption("No ideas yet. Start a session to begin.")

    st.markdown("---")

    if st.button("Reset session"):
        st.session_state.thread_id = None
        st.session_state.chat = []
        st.session_state.last_values = {}
        st.session_state.needs_user_input = False
        st.session_state.interrupt_prompt = None
        st.session_state.idea_board = None
        st.rerun()


# Render chat history
for msg in st.session_state.chat:
    render_chat_message(msg["role"], msg["content"])


# ----------------------------
# Start flow (no session yet)
# ----------------------------

if st.session_state.thread_id is None:
    st.subheader("Start a new session")

    subject = st.text_input("Subject", value="Education")
    essay_topic = st.text_input("Essay topic", value="AI in education and creativity")

    if st.button("Start"):
        try:
            with st.spinner("Agents are thinking..."):
                resp = post_json(
                    f"{st.session_state.server_url}/start",
                    {"subject": subject, "essay_topic": essay_topic},
                )
            st.session_state.thread_id = resp["thread_id"]
            process_events(resp)
            st.rerun()
        except requests.ConnectionError:
            st.error(
                "Could not connect to the backend server. "
                "Make sure it is running at: "
                f"`{st.session_state.server_url}`"
            )
            st.info(
                "Start the backend with:\n\n"
                "```\n"
                "uv run uvicorn bin.MultiAgentSystem.app:app "
                "--reload --host 127.0.0.1 --port 8000\n"
                "```"
            )
        except requests.RequestException as e:
            st.error(f"Failed to start session: {e}")

    st.stop()


# ----------------------------
# Active session flow
# ----------------------------

if st.session_state.needs_user_input and st.session_state.interrupt_prompt:
    st.info(st.session_state.interrupt_prompt)

user_text = st.chat_input("Type your reply here")

if user_text:
    st.session_state.chat.append({"role": "user", "content": user_text})

    # Show the user's message immediately before waiting for agents
    render_chat_message("user", user_text)

    try:
        with st.spinner("Agents are thinking..."):
            resp = post_json(
                f"{st.session_state.server_url}/message/{st.session_state.thread_id}",
                {"message": user_text},
            )
        process_events(resp)
        time.sleep(0.05)
        st.rerun()
    except requests.ConnectionError:
        st.error(
            "Lost connection to the backend server. "
            "Check that it is still running at: "
            f"`{st.session_state.server_url}`"
        )
    except requests.RequestException as e:
        st.error(f"Failed to send message: {e}")
