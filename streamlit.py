import streamlit as st
import requests
from typing import Any, Dict, List, Optional

# =========================
# CONFIG
# =========================
API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Agentic RAG Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _inject_theme_css() -> None:
    st.markdown(
        """
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', system-ui, -apple-system, sans-serif;
  }

  .stApp {
    background: linear-gradient(165deg, #f0f4ff 0%, #f8fafc 35%, #ffffff 100%);
  }

  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e1b4b 0%, #312e81 50%, #3730a3 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
  }
  section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
  }
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] span,
  section[data-testid="stSidebar"] h1,
  section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3 {
    color: #e0e7ff !important;
  }
  section[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: #f8fafc;
    border-radius: 10px;
  }
  section[data-testid="stSidebar"] .stTextInput input::placeholder {
    color: rgba(224,231,255,0.5);
  }
  section[data-testid="stSidebar"] .stButton > button {
    border-radius: 10px;
    font-weight: 600;
    border: none;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }
  section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.12);
    color: #e0e7ff;
  }
  section[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(0,0,0,0.2);
  }
  section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    border-radius: 12px;
    border: 1px dashed rgba(255,255,255,0.35);
    background: rgba(255,255,255,0.06);
  }
  section[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: rgba(255,255,255,0.06);
    border-radius: 10px;
  }

  .main-header-card {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 45%, #818cf8 100%);
    border-radius: 16px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 10px 40px -10px rgba(79, 70, 229, 0.45);
    border: 1px solid rgba(255,255,255,0.15);
  }
  .main-header-card h1 {
    margin: 0 0 0.35rem 0;
    font-size: 1.85rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.02em;
  }
  .main-header-card .sub {
    margin: 0;
    color: rgba(255,255,255,0.88);
    font-size: 0.95rem;
    line-height: 1.45;
  }

  .session-pill-wrap {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
  }
  .session-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
    padding: 0.4rem 0.95rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-family: ui-monospace, monospace;
    color: #312e81;
    border: 1px solid #c7d2fe;
    word-break: break-all;
  }

  div[data-testid="stChatMessage"] {
    border-radius: 14px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.75rem;
    border: 1px solid #e2e8f0;
    background: #ffffff;
  }
  div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border-radius: 14px !important;
    border-color: #e2e8f0 !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    padding: 0.35rem 0.5rem;
  }

  .stChatInput {
    border-radius: 14px;
  }
  .stChatInput > div {
    border-radius: 14px;
    border: 1px solid #cbd5e1;
    box-shadow: 0 4px 20px -4px rgba(15, 23, 42, 0.08);
  }

  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
</style>
        """,
        unsafe_allow_html=True,
    )


_inject_theme_css()


# =========================
# HELPERS
# =========================
def api_get(endpoint: str):
    url = f"{API_BASE_URL}{endpoint}"
    return requests.get(url, timeout=60)


def api_post(endpoint: str, json: Optional[Dict[str, Any]] = None, files=None):
    url = f"{API_BASE_URL}{endpoint}"
    return requests.post(url, json=json, files=files, timeout=120)


def api_delete(endpoint: str):
    url = f"{API_BASE_URL}{endpoint}"
    return requests.delete(url, timeout=60)


def get_health() -> Dict[str, Any]:
    try:
        response = api_get("/health")
        if response.ok:
            return response.json()
        return {"system_ok": False, "error": response.text}
    except Exception as e:
        return {"system_ok": False, "error": str(e)}


def get_grouped_sessions() -> Dict[str, Any]:
    try:
        response = api_get("/messages/grouped")
        if response.ok:
            return response.json()
        return {"sessions": [], "message": response.text}
    except Exception as e:
        return {"sessions": [], "message": str(e)}


def send_agent_message(question: str, session_id: Optional[str]) -> Dict[str, Any]:
    payload = {
        "question": question,
        "session_id": session_id
    }
    response = api_post("/rag_agent", json=payload)
    if response.ok:
        return response.json()
    raise Exception(response.text)


def upload_document(uploaded_file) -> Dict[str, Any]:
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
    }
    response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=300)
    if response.ok:
        return response.json()
    raise Exception(response.text)


def delete_session(session_id: str) -> Dict[str, Any]:
    response = api_delete(f"/sessions/{session_id}")
    if response.ok:
        return response.json()
    raise Exception(response.text)


def normalize_messages(raw_messages: List[Any]) -> List[Dict[str, str]]:
    """
    Приводим сообщения к удобному формату:
    [{role: 'user'/'assistant', content: '...'}]
    """
    normalized = []

    for msg in raw_messages:
        if isinstance(msg, dict):
            role = msg.get("role", "assistant")
            content = msg.get("content", "")
            normalized.append({"role": role, "content": content})
        else:
            normalized.append({"role": "assistant", "content": str(msg)})

    return normalized


def find_session_messages(grouped_data: Dict[str, Any], session_id: str) -> List[Dict[str, str]]:
    sessions = grouped_data.get("sessions", [])
    for session in sessions:
        if session.get("session_id") == session_id:
            raw_messages = session.get("messages", [])
            return normalize_messages(raw_messages)
    return []


def session_preview(messages: List[Dict[str, str]]) -> str:
    if not messages:
        return "Empty session"

    for msg in messages:
        if msg.get("role") == "user" and msg.get("content"):
            text = msg["content"].strip().replace("\n", " ")
            return text[:40] + ("..." if len(text) > 40 else "")
    return "Session"


# =========================
# SESSION STATE
# =========================
if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "sessions_cache" not in st.session_state:
    st.session_state.sessions_cache = []


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown(
        '<p style="font-size:0.75rem;opacity:0.75;margin:0 0 0.25rem 0;">Workspace</p>',
        unsafe_allow_html=True,
    )
    st.markdown("### 🤖 Agentic RAG")
    st.caption("Documents · sessions · health")

    st.markdown("---")
    st.markdown("**Backend**")
    new_api_url = st.text_input("API URL", value=API_BASE_URL)
    API_BASE_URL = new_api_url.strip()

    if st.button("Check health", use_container_width=True):
        health = get_health()
        st.session_state.health_data = health

    health_data = st.session_state.get("health_data")
    if health_data:
        if health_data.get("system_ok"):
            st.success("System is OK")
        else:
            st.error("System is not OK")
        st.json(health_data)

    st.markdown("---")
    st.markdown("**Upload document**")

    uploaded_file = st.file_uploader(
        "Upload PDF / TXT / CSV / DOCX",
        type=["pdf", "txt", "csv", "docx"],
    )

    if st.button("Upload file", use_container_width=True):
        if uploaded_file is None:
            st.warning("Choose a file first.")
        else:
            try:
                with st.spinner("Uploading and indexing file..."):
                    result = upload_document(uploaded_file)
                if result.get("success"):
                    st.success("File uploaded successfully.")
                    st.json(result)
                else:
                    st.error("Upload failed.")
                    st.json(result)
            except Exception as e:
                st.error(f"Upload error: {e}")

    st.markdown("---")
    st.markdown("**Sessions**")

    if st.button("Refresh sessions", use_container_width=True):
        grouped = get_grouped_sessions()
        st.session_state.sessions_cache = grouped.get("sessions", [])

    if st.button("New chat", use_container_width=True):
        st.session_state.active_session_id = None
        st.session_state.chat_messages = []
        st.rerun()

    sessions_cache = st.session_state.sessions_cache

    if not sessions_cache:
        grouped = get_grouped_sessions()
        sessions_cache = grouped.get("sessions", [])
        st.session_state.sessions_cache = sessions_cache

    if sessions_cache:
        for session in sessions_cache:
            sid = session.get("session_id")
            msgs = normalize_messages(session.get("messages", []))
            preview = session_preview(msgs)

            col1, col2 = st.columns([4, 1])

            with col1:
                if st.button(f"💬 {preview}", key=f"open_{sid}", use_container_width=True):
                    st.session_state.active_session_id = sid
                    st.session_state.chat_messages = msgs
                    st.rerun()

            with col2:
                if st.button("🗑️", key=f"delete_{sid}", use_container_width=True):
                    try:
                        delete_session(sid)
                        if st.session_state.active_session_id == sid:
                            st.session_state.active_session_id = None
                            st.session_state.chat_messages = []
                        grouped = get_grouped_sessions()
                        st.session_state.sessions_cache = grouped.get("sessions", [])
                        st.success("Session deleted")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete error: {e}")
    else:
        st.info("No sessions found.")


# =========================
# MAIN PAGE
# =========================
active_session_id = st.session_state.active_session_id

st.markdown(
    """
    <div class="main-header-card">
      <h1>Agentic RAG Chat</h1>
      <p class="sub">Ask questions grounded in your documents. Chat uses <code style="background:rgba(255,255,255,0.2);padding:0.15rem 0.4rem;border-radius:6px;font-size:0.85em;">/rag_agent</code> only — the naive <code style="background:rgba(255,255,255,0.2);padding:0.15rem 0.4rem;border-radius:6px;font-size:0.85em;">/query</code> endpoint is not used.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

top_col1, top_col2 = st.columns([3, 2])

with top_col1:
    with st.container(border=True):
        st.markdown("### Current session")
        if active_session_id:
            st.markdown(
                f'<div class="session-pill-wrap"><span class="session-pill">🔑 {active_session_id}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("New session will be created automatically after first message.")

with top_col2:
    with st.container(border=True):
        st.markdown("### Sync")
        if st.button("Reload current session from backend", use_container_width=True):
            if active_session_id:
                grouped = get_grouped_sessions()
                st.session_state.sessions_cache = grouped.get("sessions", [])
                msgs = find_session_messages(grouped, active_session_id)
                st.session_state.chat_messages = msgs
                st.success("Session reloaded")
                st.rerun()
            else:
                st.warning("No active session yet.")

st.markdown("---")

# render chat
for msg in st.session_state.chat_messages:
    role = msg.get("role", "assistant")
    content = msg.get("content", "")

    with st.chat_message("user" if role == "user" else "assistant"):
        st.markdown(content)

# chat input
user_prompt = st.chat_input("Message the RAG agent…")

if user_prompt:
    # show user message immediately
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_prompt
    })

    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            try:
                result = send_agent_message(
                    question=user_prompt,
                    session_id=st.session_state.active_session_id
                )

                answer = result.get("answer", "No answer returned.")
                returned_session_id = result.get("session_id")

                st.session_state.active_session_id = returned_session_id
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": answer
                })

                st.markdown(answer)

                grouped = get_grouped_sessions()
                st.session_state.sessions_cache = grouped.get("sessions", [])

            except Exception as e:
                error_text = f"Request error: {e}"
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": error_text
                })
                st.error(error_text)
