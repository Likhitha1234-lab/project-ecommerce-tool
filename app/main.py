import streamlit as st
import streamlit.components.v1 as components
from faq import ingest_faq_data, faq_chain
from sql import sql_chain
from pathlib import Path
from router import router


# ---------------- Page Configuration ----------------
st.set_page_config(
    page_title="E-commerce Bot",
    page_icon="\U0001F916",
    layout="centered"
)


# ---------------- FAQ Data ----------------
faqs_path = Path(__file__).parent / "resources/faq_data.csv"
ingest_faq_data(faqs_path)


# ---------------- Router Function ----------------
def ask(query):
    route = router(query).name

    if route == "faq":
        return faq_chain(query)

    elif route == "sql":
        return sql_chain(query)

    else:
        return f"Route {route} not implemented yet"


# ---------------- Page Heading ----------------
st.title("\U0001F916 E-commerce Bot")


# ---------------- Styling ----------------
st.markdown(
    """
    <style>
    :root {
        --bg-base: #e9ebf0;
        --bg-panel: #ffffff;
        --bg-panel-alt: #eef1f8;
        --border: #d7dae2;
        --text-main: #23242a;
        --text-muted: #767a87;
        --accent: #4b6ef5;
    }

    /* Entire app background */
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main,
    .stApp {
        background-color: var(--bg-base) !important;
        color: var(--text-main);
    }

    /* Top header */
    [data-testid="stHeader"] {
        background-color: var(--bg-base) !important;
        border-bottom: 1px solid var(--border);
    }

    /* Bottom chat input area */
    [data-testid="stBottom"] > div {
        background-color: var(--bg-base) !important;
    }

    /* Main content width */
    .block-container {
        padding-top: 2rem;
        max-width: 820px;
    }

    /* Main heading */
    h1 {
        font-weight: 600;
        color: var(--text-main) !important;
        border-bottom: 1px solid var(--border);
        padding-bottom: 0.6rem;
        margin-bottom: 1.4rem;
    }

    /* Chat bubbles */
    [data-testid="stChatMessage"] {
        background-color: var(--bg-panel);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.7rem;
        box-shadow: 0 1px 3px rgba(20, 20, 40, 0.07);
    }

    /* User chat bubble */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background-color: var(--bg-panel-alt);
    }

    /* Chat text */
    [data-testid="stChatMessage"] p {
        color: var(--text-main);
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        background-color: var(--bg-panel) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(20, 20, 40, 0.05) !important;
    }

    /* Chat input focus */
    [data-testid="stChatInput"]:focus-within {
        border: 1px solid var(--accent) !important;
    }

    /* Input text */
    [data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: var(--text-main) !important;
    }

    /* Placeholder */
    [data-testid="stChatInput"] textarea::placeholder {
        color: var(--text-muted) !important;
    }

    /* Submit button */
    [data-testid="stChatInputSubmitButton"] {
        background-color: var(--bg-panel-alt) !important;
        border-radius: 8px !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-thumb {
        background-color: var(--border);
        border-radius: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- Chat Input ----------------
query = st.chat_input("Write your query")


# ---------------- Chat History ----------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------- Handle New Query ----------------
if query:

    # Display user message
    with st.chat_message("user"):
        st.markdown(query)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    # Get response
    response = ask(query)

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )


# ---------------- Auto Scroll ----------------
components.html(
    """
    <script>
        var streamlitDoc = window.parent.document;

        var mainContainer = streamlitDoc.querySelector('section.main');

        if (mainContainer) {
            mainContainer.scrollTo({
                top: mainContainer.scrollHeight,
                behavior: 'smooth'
            });
        }

        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    </script>
    """,
    height=0,
)