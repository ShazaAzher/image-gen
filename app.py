import streamlit as st
import os
from anthropic import Anthropic
from dotenv import load_dotenv
import validators

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

st.set_page_config(page_title="Claude Chat + Media", layout="wide")

# ---- Session state ----
if "messages" not in st.session_state:
    st.session_state.messages = []

if "input" not in st.session_state:
    st.session_state.input = ""

# ---- User input ----
st.title("Claude Chat with Images & Video")
with st.form(key="input_form"):
    st.session_state.input = st.text_input("Type your message here:", st.session_state.input)
    submitted = st.form_submit_button("Send")
    
if submitted and st.session_state.input.strip():
    user_msg = st.session_state.input.strip()
    st.session_state.messages.append({"role": "user", "content": user_msg})
    st.session_state.input = ""  # reset input

    # ---- Call Claude ----
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=st.session_state.messages,
        max_tokens=512,
    )
    
    assistant_msg = response.content[0].text
    st.session_state.messages.append({"role": "assistant", "content": assistant_msg})

# ---- Display messages ----
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div style='text-align:right; background:#dbeafe; padding:8px; border-radius:8px; margin:4px 0;'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        # Split message by spaces to detect URLs
        parts = msg['content'].split()
        st.markdown(f"<div style='text-align:left; background:#e5e7eb; padding:8px; border-radius:8px; margin:4px 0;'>{msg['content']}</div>", unsafe_allow_html=True)
        
        for part in parts:
            if validators.url(part):
                # Images
                if any(part.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif"]):
                    st.image(part, use_column_width=True)
                # Videos
                if any(part.lower().endswith(ext) for ext in [".mp4", ".mov", ".webm"]):
                    st.video(part)
