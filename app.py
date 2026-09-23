import streamlit as st
import requests

st.set_page_config(
    page_title="Personal Assistant - Suraj",
    layout="wide",
    initial_sidebar_state="expanded"
)

WEBHOOK_URL = "http://localhost:5678/webhook/1cb8c062-ad8a-4fbf-8299-b4c9550b20a8"

st.markdown("""
<style>
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
}
.assistant-header {
    padding: 1.2rem 1.5rem;
    border-radius: 16px;
    border: 1px solid rgba(128,128,128,0.2);
    margin-bottom: 1.5rem;
}
.assistant-title {
    font-size: 2rem;
    font-weight: 700;
}
.assistant-subtitle {
    color: #777;
    font-size: 0.95rem;
}
.capability-card {
    padding: 1rem;
    border-radius: 12px;
    border: 1px solid rgba(128,128,128,0.2);
    margin-bottom: 0.7rem;
}
.small-text {
    color: #777;
    font-size: 0.85rem;
}
div[data-testid="stChatMessage"] {
    border-radius: 14px;
    margin-bottom: 0.5rem;
}
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128,128,128,0.2);
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown("## Personal Assistant")
    st.caption("AI-powered productivity assistant")

    st.divider()

    st.markdown("### Capabilities")
    st.markdown("""
    **Calendar**  
    Create and view calendar events.

    **Gmail**  
    Read, summarize, send and reply to emails.

    **Tasks**  
    Create, view and delete tasks.

    **Notes**  
    Create and update notes.

    **Expenses**  
    Track expenses and calculate totals.

    **Information**  
    Answer questions and search the web.
    """)

    st.divider()

    st.markdown("### Quick Actions")

    if st.button("Create an event", use_container_width=True):
        st.session_state.quick_prompt = "Create an event for tomorrow at 10:00 AM for 2 hours."
        st.rerun()

    if st.button("Today's events", use_container_width=True):
        st.session_state.quick_prompt = "Show me my calendar events for today."
        st.rerun()

    if st.button("Check emails", use_container_width=True):
        st.session_state.quick_prompt = "Show me my latest emails."
        st.rerun()

    if st.button("Create a task", use_container_width=True):
        st.session_state.quick_prompt = "Create a task to review my project tomorrow."
        st.rerun()

    if st.button("Create a note", use_container_width=True):
        st.session_state.quick_prompt = "Create a new note about today's work."
        st.rerun()

    if st.button("Add an expense", use_container_width=True):
        st.session_state.quick_prompt = "Add an expense of Rs. 500 for food."
        st.rerun()

    st.divider()

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Connected through n8n automation")

st.markdown("""
<div class="assistant-header">
    <div class="assistant-title">Personal Assistant</div>
    <div class="assistant-subtitle">
        Your AI-powered productivity assistant for calendar, email,
        tasks, notes, expenses and information.
    </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("### How can I help you?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="capability-card">
        <b>Calendar</b><br>
        <span class="small-text">Create events and check your schedule.</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="capability-card">
        <b>Gmail</b><br>
        <span class="small-text">Read, summarize and manage emails.</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="capability-card">
        <b>Tasks</b><br>
        <span class="small-text">Create and manage your to-do list.</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="capability-card">
        <b>Notes</b><br>
        <span class="small-text">Create and update your notes.</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="capability-card">
        <b>Expenses</b><br>
        <span class="small-text">Track expenses and calculate totals.</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="capability-card">
        <b>Information</b><br>
        <span class="small-text">Ask questions and search for information.</span>
        </div>
        """, unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

quick_prompt = st.session_state.pop("quick_prompt", None)
user_message = st.chat_input("Message your personal assistant...")

if quick_prompt:
    user_message = quick_prompt

if user_message:
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Assistant is working..."):
            try:
                response = requests.post(
                    WEBHOOK_URL,
                    json={
                        "message": user_message,
                        "conversation": st.session_state.messages
                    },
                    timeout=120
                )

                response.raise_for_status()

                try:
                    data = response.json()
                except ValueError:
                    raise Exception(
                        f"n8n returned non-JSON response:\n{response.text[:1000]}"
                    )

                ai_response = None

                if isinstance(data, list):
                    if data and isinstance(data[0], dict):
                        ai_response = (
                            data[0].get("output")
                            or data[0].get("response")
                            or data[0].get("message")
                            or data[0].get("text")
                        )

                elif isinstance(data, dict):
                    ai_response = (
                        data.get("output")
                        or data.get("response")
                        or data.get("message")
                        or data.get("text")
                    )

                if not ai_response:
                    raise Exception(
                        f"No assistant output found in n8n response:\n{data}"
                    )

                ai_response = str(ai_response)

            except requests.exceptions.ConnectionError:
                ai_response = (
                    "**Could not connect to n8n.**\n\n"
                    "Make sure n8n is running on `http://localhost:5678` "
                    "and that your webhook workflow is active."
                )

            except requests.exceptions.Timeout:
                ai_response = "**The assistant timed out.**"

            except requests.exceptions.HTTPError as e:
                ai_response = (
                    f"**n8n returned an HTTP error.**\n\n"
                    f"`{e}`\n\n"
                    f"```text\n{response.text[:1000]}\n```"
                )

            except Exception as e:
                ai_response = f"**Assistant error**\n\n```text\n{e}\n```"

        st.markdown(ai_response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_response
    })