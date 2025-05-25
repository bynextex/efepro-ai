import streamlit as st
import requests
import time
from datetime import datetime
import os
import json

# --- API Ayarları ---
API_URL = "https://inference-api.nousresearch.com/v1/chat/completions"
API_KEY = st.secrets["API_KEY"]

HISTORY_FILE = "chat_history.json"

# --- Sayfa Yapılandırması ---
st.set_page_config(page_title="EfePro AI Chat Bot", layout="centered")

# --- Session State Başlat ---
for key, default in {
    "messages": [],
    "persisted_messages": [],
    "logs": [],
    "selected_model": "Hermes-3-Llama-3.1-405B",
    "history_loaded": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Geçmişi Otomatik Yükle (ilk çalışmada bir kez) ---
if os.path.exists(HISTORY_FILE) and not st.session_state.history_loaded:
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
        st.session_state.persisted_messages = history
        st.session_state.messages = history.copy()
        st.session_state.history_loaded = True
        st.toast("💾 Önceki sohbet geçmişi yüklendi.")

# --- CSS ---
st.markdown("""
    <style>
        .stApp {
            background-color: black;
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }
            
        .neon-title {
            font-size: 2rem;
            position: fixed !important;
            text-align: center;
            font-weight: bold;
            margin-top: 10px;
            margin-bottom: 25px;
            color: #00ffff;
            text-shadow:
                0 0 5px #00ffff,
                0 0 10px #00ffff,
                0 0 20px #00ffff,
                0 0 40px #00e0ff,
                0 0 80px #00e0ff;
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
            
        .custom-clear-button button {
            background-color: #111 !important;
            color: #00ffff !important;
            font-size: 11px !important;
            border: 1px solid #00ffff !important;
            border-radius: 4px;
            padding: 2px 8px;
            margin: 0 auto;
            display: block;
        }
        .custom-clear-button button:hover {
            background-color: #00ffff !important;
            color: black !important;
        }

        /* FOOTER alanını özel renge çek */
        .chat-footer {
            position: fixed;
            bottom: 0px;
            left: 0;
            right: 0;
            width: 100%;
            min-width: 100%;
            background-color: rgb(22, 33, 33);  /* Senin verdiğin koyu ton */
            display: flex;
            flex-direction: column;
            -webkit-box-align: center;
            align-items: center;
            padding: 10px 20px;
            z-index: 999;
            border-top: 1px solid #333;
        }


        /* HEADER üst bar koyu ve sabit */
        header.st-emotion-cache-1eyfjps {
            position: fixed !important;
            top: 0px !important;
            left: 0px;
            right: 0px;
            height: 3.75rem;
            background: rgb(0, 0, 0) !important;
            z-index: 999990;
            outline: none;
        }

        @media screen and (max-width: 600px) {
            .chat-footer {
                padding: 8px 12px;
            }
        }
    </style>
""", unsafe_allow_html=True)

# --- Başlık ---
st.markdown("""
<div class="neon-title">EfePro AI Chat Bot</div>
""", unsafe_allow_html=True)

# --- Mesajları Göster ---
st.markdown('<div class="message-container">', unsafe_allow_html=True)
for msg in st.session_state.persisted_messages:
    with st.chat_message(msg["role"]):
        st.markdown(
            f"<span style='font-size: small; color: gray;'>({msg['time']})</span> {msg['content']}",
            unsafe_allow_html=True
        )
st.markdown('</div>', unsafe_allow_html=True)

# --- Footer (model + input) ---
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

# --- Scroll-to-bottom Script ---
st.markdown("""
    <script>
    var chatContainer = window.parent.document.querySelector('.element-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    </script>
""", unsafe_allow_html=True)

# --- Mesaj Gönderme ---
if user_input:
    timestamp = datetime.now().strftime("%H:%M")
    user_msg = {"role": "user", "content": user_input, "time": timestamp}
    st.session_state.messages.append(user_msg)
    st.session_state.persisted_messages.append(user_msg)
    st.session_state.logs.append(f"[{timestamp}] USER: {user_input}")

    # --- Otomatik kayıt ---
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.persisted_messages, f, ensure_ascii=False, indent=2)

    with st.chat_message("user"):
        st.markdown(f"<span style='font-size: small; color: gray;'>({timestamp})</span> {user_input}", unsafe_allow_html=True)

    with st.chat_message("assistant"):
        with st.spinner("Yazıyor..."):
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": st.session_state.selected_model,
                "messages": st.session_state.messages[-5:],
                "temperature": 0.7
            }
            start_time = time.time()
            try:
                res = requests.post(API_URL, headers=headers, json=data)
                latency = time.time() - start_time
                if res.status_code == 200:
                    bot_reply = res.json()["choices"][0]["message"]["content"]
                else:
                    bot_reply = f"Hata: {res.status_code}"
            except Exception as e:
                bot_reply = f"API hatası: {str(e)}"
                latency = 0

            bot_time = datetime.now().strftime("%H:%M")
            bot_msg = {"role": "assistant", "content": bot_reply, "time": bot_time}
            st.session_state.messages.append(bot_msg)
            st.session_state.persisted_messages.append(bot_msg)

            # --- Otomatik kayıt ---
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(st.session_state.persisted_messages, f, ensure_ascii=False, indent=2)

            st.session_state.logs.append(f"[{bot_time}] BOT yanıt süresi: {latency:.2f} saniye")
            st.session_state.logs.append(f"[{bot_time}] BOT: {bot_reply}")

            st.markdown(f"<span style='font-size: small; color: gray;'>({bot_time})</span> {bot_reply}", unsafe_allow_html=True)

# --- Geçmişi Manuel Temizle Butonu (Küçük Stil) ---
with st.container():
    st.markdown('<div class="custom-clear-button">', unsafe_allow_html=True)
    if st.button("🧹"):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
            st.session_state.persisted_messages = []
            st.session_state.messages = []
            st.session_state.history_loaded = False
            st.toast("🧹 Geçmiş dosyası silindi. Sayfayı yenileyin.")
    st.markdown('</div>', unsafe_allow_html=True)
