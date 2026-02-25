import time
import requests
import streamlit as st


st.set_page_config(page_title="MultiAgentSystem UI", layout="centered")

# ----------------------------
# Helpers
# ----------------------------

def post_json(url: str, payload: dict, timeout: int = 60) -> dict:
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()

def role_from_key(node: str, key: str) -> str:
    """
    Map state keys / nodes to chat roles for display.
    """
    if key in {"facilitator_reply"}:
        return "facilitator"
    if key in {"idea_generator_reply"}:
        return "idea_generator"
    if key in {"subject_specialist_reply"}:
        return "subject_specialist"
    if key in {"critic_reply"}:
        return "critic"
    return node or "system"

def should_display(key: str, value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != "" and (key.endswith("_reply") or key in {"idea_board"})
    return False


# Color mapping per agent (minimal + clear)
ROLE_COLORS = {
    "user": "#FFFFFF",              # default chat bubble styling
    "facilitator": "#E3F2FD",        # light blue
    "idea_generator": "#E8F5E9",     # light green
    "subject_specialist": "#FFF3E0", # light orange
    "critic": "#FCE4EC",            # light pink
    # "system": "#F5F5F5",           # light grey
}

# NEW: choose which side each agent appears on
# You can swap these around however you like.
ROLE_SIDE = {
    "user": "right",
    "facilitator": "left",
    "idea_generator": "right",
    "subject_specialist": "left",
    "critic": "right",
    "system": "left",
}


def render_coloured_message(role: str, content: str):
    """
    Render a colored bubble aligned left/right (so different agents can appear on different sides).
    """
    bg = ROLE_COLORS.get(role, "#F5F5F5")
    border = "#E0E0E0"
    text = "#111111"
    side = ROLE_SIDE.get(role, "left")

    # HTML escape minimal to avoid breaking layout
    safe = (
        str(content)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    justify = "flex-end" if side == "right" else "flex-start"
    # Slightly different corner rounding to feel like chat bubbles
    radius = "14px 14px 4px 14px" if side == "right" else "14px 14px 14px 4px"

    html = f"""
    <div style="display:flex; justify-content:{justify}; margin: 2px 0px 10px 0px;">
      <div style="
          max-width: 78%;
          background: {bg};
          border: 1px solid {border};
          padding: 10px 12px;
          border-radius: {radius};
          color: {text};
          line-height: 1.35;
          white-space: pre-wrap;
          box-shadow: 0 1px 2px rgba(0,0,0,0.06);
      ">{safe}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def process_events(resp: dict):
    """
    resp:
      {
        "thread_id": "...",
        "events": [[node,key,value], ...],
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
    st.session_state.chat = []  # [{"role":..., "content":...}]
if "last_values" not in st.session_state:
    st.session_state.last_values = {}
if "needs_user_input" not in st.session_state:
    st.session_state.needs_user_input = False
if "interrupt_prompt" not in st.session_state:
    st.session_state.interrupt_prompt = None


# ----------------------------
# UI
# ----------------------------

st.title("AI 4 ED")

with st.sidebar:
    st.subheader("Server")
    st.session_state.server_url = st.text_input("FastAPI base URL", st.session_state.server_url)
    st.caption("Backend should expose: POST /start and POST /message/{thread_id}")

    st.markdown("---")
    st.subheader("Colours")
    st.caption("Agent message colours are applied to the bubble background.")

    if st.button("Reset session"):
        st.session_state.thread_id = None
        st.session_state.chat = []
        st.session_state.last_values = {}
        st.session_state.needs_user_input = False
        st.session_state.interrupt_prompt = None
        st.rerun()


# Render chat so far (agents can now appear on different sides)
for msg in st.session_state.chat:
    role = msg["role"]
    render_coloured_message(role, msg["content"])


# ----------------------------
# Start flow (no session yet)
# ----------------------------

if st.session_state.thread_id is None:
    st.subheader("Start a new session")

    subject = st.text_input("Subject", value="Education")
    essay_topic = st.text_input("Essay topic", value="AI in education and creativity")

    if st.button("Start"):
        try:
            resp = post_json(
                f"{st.session_state.server_url}/start",
                {"subject": subject, "essay_topic": essay_topic},
            )
            st.session_state.thread_id = resp["thread_id"]
            process_events(resp)
            st.rerun()
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
    # Show user message immediately
    st.session_state.chat.append({"role": "user", "content": user_text})

    try:
        resp = post_json(
            f"{st.session_state.server_url}/message/{st.session_state.thread_id}",
            {"message": user_text},
        )
        process_events(resp)
        time.sleep(0.05)
        st.rerun()
    except requests.RequestException as e:
        st.error(f"Failed to send message: {e}")