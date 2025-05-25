import streamlit as st
import requests
import time
from datetime import datetime

# --- API Ayarları ---
API_URL = "https://inference-api.nousresearch.com/v1/chat/completions"
API_KEY = "sk-ZhUb5k6PN6cCoSZb-jyueQ"

# --- Sayfa Yapılandırması ---
st.set_page_config(page_title="EfePro AI Chat Bot", layout="centered")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "persisted_messages" not in st.session_state:
    st.session_state.persisted_messages = []
if "logs" not in st.session_state:
    st.session_state.logs = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Hermes-3-Llama-3.1-405B"

# --- CSS ---
st.markdown("""
    <style>
        .stApp {
            background-color: black;
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }
        label, .stSelectbox label {
            color: white !important;
        }
        [class^="st-emotion-cache-"][class*="16tyu1"] {
            color: #fff !important;
        }
        .message-container {
            padding-bottom: 200px;
            max-width: 800px;
            margin: auto;
        }
        .chat-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #111;
            padding: 10px 20px;
            z-index: 999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            border-top: 1px solid #333;
        }
        .stChatMessage {
            background-color: #222;
            padding: 12px 16px;
            border-radius: 12px;
            margin-bottom: 10px;
            max-width: 90%;
            word-wrap: break-word;
            color: #fff !important;
        }
        .stChatMessage[data-testid="stChatMessage-assistant"] {
            background-color: #2a2a2a;
            border: 1px solid #FFD700;
            box-shadow: 0 0 10px #FFD70033;
        }
        .stChatMessage[data-testid="stChatMessage-user"] {
            background-color: #444;
        }
        @media screen and (max-width: 600px) {
            .chat-footer {
                padding: 8px 12px;
            }
        }
    </style>
""", unsafe_allow_html=True)

# --- Başlık ---
st.markdown("<h1 style='text-align: center; color: white;'>EfePro AI Chat Bot</h1>", unsafe_allow_html=True)

# --- Mesajları Göster ---
st.markdown('<div class="message-container">', unsafe_allow_html=True)
for msg in st.session_state.persisted_messages:
    with st.chat_message(msg["role"]):
        st.markdown(
            f"<span style='font-size: small; color: gray;'>({msg['time']})</span> {msg['content']}",
            unsafe_allow_html=True
        )
st.markdown('</div>', unsafe_allow_html=True)

# --- Chat Footer ---
with st.markdown('<div class="chat-footer">', unsafe_allow_html=True):
    st.session_state.selected_model = st.selectbox(
        "Model Seçiniz:",
        [
            "Hermes-3-Llama-3.1-405B",
            "Hermes-3-Llama-3.1-70B",
            "DeepHermes-3-Llama-3-8B-Preview",
            "DeepHermes-3-Mistral-24B-Preview"
        ],
        index=[
            "Hermes-3-Llama-3.1-405B",
            "Hermes-3-Llama-3.1-70B",
            "DeepHermes-3-Llama-3-8B-Preview",
            "DeepHermes-3-Mistral-24B-Preview"
        ].index(st.session_state.selected_model),
        key="model_selectbox"
    )
    user_input = st.chat_input("Mesajınızı yazın...", key="chat_input_main")

# --- Mesaj Gönderme ---
if user_input:
    timestamp = datetime.now().strftime("%H:%M")
    user_msg = {"role": "user", "content": user_input, "time": timestamp}
    st.session_state.messages.append(user_msg)
    st.session_state.persisted_messages.append(user_msg)
    st.session_state.logs.append(f"[{timestamp}] USER: {user_input}")

    with st.chat_message("user"):
        st.markdown(f"<span style='font-size: small; color: gray;'>({timestamp})</span> {user_input}", unsafe_allow_html=True)

    with st.chat_message("assistant"):
        with st.spinner("Yazıyor..."):
            time.sleep(1)
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": st.session_state.selected_model,
                "messages": st.session_state.messages[-5:],
                "temperature": 0.7
            }
            try:
                res = requests.post(API_URL, headers=headers, json=data)
                if res.status_code == 200:
                    bot_reply = res.json()["choices"][0]["message"]["content"]
                else:
                    bot_reply = f"Hata: {res.status_code}"
            except Exception as e:
                bot_reply = f"API hatası: {str(e)}"

            bot_time = datetime.now().strftime("%H:%M")
            bot_msg = {"role": "assistant", "content": bot_reply, "time": bot_time}
            st.session_state.messages.append(bot_msg)
            st.session_state.persisted_messages.append(bot_msg)
            st.session_state.logs.append(f"[{bot_time}] BOT: {bot_reply}")

            st.markdown(f"<span style='font-size: small; color: gray;'>({bot_time})</span> {bot_reply}", unsafe_allow_html=True)
