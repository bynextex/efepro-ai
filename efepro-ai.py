import streamlit as st
import requests
import time
from datetime import datetime

# --- API Ayarları ---
API_URL = "https://inference-api.nousresearch.com/v1/chat/completions"
API_KEY = "sk-ZhUb5k6PN6cCoSZb-jyueQ"

# --- Sayfa Yapılandırması ---
st.set_page_config(page_title="ChatBot UI", layout="centered")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- HTML, CSS (Header sabitleme, sola hizalama, stil ayarları) ---
st.markdown("""
    <style>
        .stApp {
            background-color: black;
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }
        header.fixed {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #111;
            padding: 10px 20px;
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .model-box {
            color: white;
        }
        .controls button {
            background: #444;
            color: white;
            border: none;
            padding: 10px 15px;
            margin: 0 5px;
            font-size: 18px;
            border-radius: 5px;
            cursor: pointer;
        }
        .message-container {
            padding-top: 80px;
            max-width: 800px;
            margin: auto;
        }
        .element-container:has(.stChatMessage) {
            text-align: left !important;
        }
    </style>
    <header class="fixed">
        <div class="model-box">
            <label>Model seçiniz:</label>
        </div>
        <div class="controls">
            <button onclick="player.previousVideo()">⏮</button>
            <button onclick="togglePlay()">▶️/⏸️</button>
            <button onclick="toggleMute()">🔇</button>
            <button onclick="player.nextVideo()">⏭</button>
        </div>
    </header>
    <iframe id="player" width="0" height="0" style="display:none;" src="https://www.youtube.com/embed/videoseries?list=PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI&autoplay=1&loop=1&mute=0&enablejsapi=1" frameborder="0" allow="autoplay"></iframe>
    <script src="https://www.youtube.com/iframe_api"></script>
    <script>
        var player;
        function onYouTubeIframeAPIReady() {
            player = new YT.Player('player', {
                events: {
                    'onReady': onPlayerReady
                }
            });
        }
        function onPlayerReady(event) {
            event.target.setVolume(100);
            event.target.playVideo();
        }
        function togglePlay() {
            var state = player.getPlayerState();
            if (state === YT.PlayerState.PLAYING) {
                player.pauseVideo();
            } else {
                player.playVideo();
            }
        }
        function toggleMute() {
            if (player.isMuted()) {
                player.unMute();
            } else {
                player.mute();
            }
        }
    </script>
""", unsafe_allow_html=True)

# --- Model Seçimi ---
model = st.selectbox("", [
    "Hermes-3-Llama-3.1-70B",
    "DeepHermes-3-Llama-3-8B-Preview",
    "DeepHermes-3-Mistral-24B-Preview",
    "Hermes-3-Llama-3.1-405B"
], label_visibility="collapsed")

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
                "model": model,
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

# Kod sonu
