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
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Hermes-3-Llama-3.1-70B"

# --- Başlık ---
st.markdown("<h1 style='text-align: center; color: white;'>Nous AI Chat Bot</h1>", unsafe_allow_html=True)

# --- CSS ---
st.markdown("""
    <style>
        .stApp {
            background-color: black;
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }
        .message-container {
            padding-bottom: 100px;
            max-width: 800px;
            margin: auto;
        }
        .element-container:has(.stChatMessage) {
            text-align: left !important;
        }
        .chat-footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #111;
            padding: 10px 20px;
            z-index: 1000;
        }
    </style>
""", unsafe_allow_html=True)

# --- Mevcut Mesajları Göster ---
st.markdown('<div class="message-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f"{msg['content']} <span style='font-size: small; color: gray;'>({msg['time']})</span>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Kullanıcı Mesaj Girişi ---
user_input = st.chat_input("Mesajınızı yazın...")
if user_input:
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": user_input, "time": timestamp})
    with st.chat_message("user"):
        st.markdown(f"{user_input} <span style='font-size: small; color: gray;'>({timestamp})</span>", unsafe_allow_html=True)

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
            st.session_state.messages.append({"role": "assistant", "content": bot_reply, "time": bot_time})
            st.markdown(f"{bot_reply} <span style='font-size: small; color: gray;'>({bot_time})</span>", unsafe_allow_html=True)

# --- Model Seçici Chat Input Altına ---
with st.container():
    st.session_state.selected_model = st.selectbox(
        "Model Seçiniz:",
        [
            "Hermes-3-Llama-3.1-70B",
            "DeepHermes-3-Llama-3-8B-Preview",
            "DeepHermes-3-Mistral-24B-Preview",
            "Hermes-3-Llama-3.1-405B"
        ],
        index=[
            "Hermes-3-Llama-3.1-70B",
            "DeepHermes-3-Llama-3-8B-Preview",
            "DeepHermes-3-Mistral-24B-Preview",
            "Hermes-3-Llama-3.1-405B"
        ].index(st.session_state.selected_model),
        label_visibility="collapsed",
        key="model_selectbox"
    )

# Kod sonu
