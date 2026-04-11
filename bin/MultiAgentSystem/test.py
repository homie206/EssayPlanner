import requests
import streamlit as st

st.set_page_config(page_title="Isolated Download Test", layout="centered")

BACKEND_URL = "http://127.0.0.1:8001"

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "idea_board" not in st.session_state:
    st.session_state.idea_board = None
if "show_download" not in st.session_state:
    st.session_state.show_download = False
if "final_file_name" not in st.session_state:
    st.session_state.final_file_name = "essay_plan.txt"
if "final_file_mime_type" not in st.session_state:
    st.session_state.final_file_mime_type = "text/markdown"
if "chat" not in st.session_state:
    st.session_state.chat = []

def process_events(resp: dict):
    for event in resp.get("events", []):
        node, key, value = event

        if key == "idea_board" and value is not None:
            st.session_state.idea_board = str(value)

        if key == "final_file_name" and value:
            st.session_state.final_file_name = str(value)

        if key == "final_file_mime_type" and value:
            st.session_state.final_file_mime_type = str(value)

        if key == "final_message":
            st.session_state.show_download = True
            st.session_state.chat.append({"role": "assistant", "content": str(value)})

st.title("Isolated Download Test")

if st.button("Run fake final-output flow"):
    resp = requests.post(
        f"{BACKEND_URL}/start",
        json={"subject": "Education", "essay_topic": "AI in education and creativity"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    st.session_state.thread_id = data["thread_id"]
    process_events(data)
    st.rerun()

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if st.session_state.idea_board:
    st.markdown("### Preview")
    st.markdown(st.session_state.idea_board)

if st.session_state.show_download and st.session_state.idea_board:
    st.success("Download is ready.")

    st.download_button(
        label="⬇️ Download Essay Plan",
        data=st.session_state.idea_board,
        file_name=st.session_state.final_file_name,
        mime=st.session_state.final_file_mime_type,
    )