import streamlit as st
import requests
import time
from datetime import datetime
from streamlit_lottie import st_lottie
import json

# --- Sayfa Yapılandırması (İlk Komut) ---
st.set_page_config(page_title="EfePro AI Chat Bot", layout="centered")

# --- API Ayarları ---
API_URL = "https://inference-api.nousresearch.com/v1/chat/completions"
API_KEY = "sk-ZhUb5k6PN6cCoSZb-jyueQ"

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Hermes-3-Llama-3.1-70B"
if "robot_message_shown" not in st.session_state:
    st.session_state.robot_message_shown = False

# --- Lottie Animasyon Yükleyici ---
def load_lottie(path):
    with open(path, "r") as f:
        return json.load(f)

lottie_robot = load_lottie("animation.json")

# --- Koyu Tema & Stil ---
st.markdown("""
    <style>
            
        /* Genel olarak st-emotion-cache arka plan ve yazı rengi ayarı */
        [class^="st-emotion-cache-"] {
        background-color: transparent !important;
        color: rgb(230, 234, 241) !important;
        }

        /* Alt elemanların da metin rengini ayarla */
        [class^="st-emotion-cache-"] * {
        color: rgb(230, 234, 241) !important;
        }

        /* Mesaj yazma kutusunun container’ı: özel border, border-radius ve arka plan */
        .st-emotion-cache-yd4u6l {
        border: 1px solid #f5c300 !important;
        border-radius: 1.25rem !important;
        background-color: rgb(240, 242, 246) !important;  /* Beyazımsı ama şeffaf olmayan */
        }
            
        /* Robot animasyonunu saran container */
        #robot-container {
            background-color: transparent !important;
        }

        /* Eğer lottie animasyonunun arka planı varsa, onu da kaldır */
        .lottie-container > div {
            background-color: transparent !important;
        }

        /* Otomatik oluşturulan element-container ve cache class'ını resetle */
        .stElementContainer.element-container.st-emotion-cache-17lr0tt.e1lln2w81 {
            all: unset !important;
            /* display:none !important;  -- sadece görünmez yapmak istersen açabilirsin */
        }
            
        .stApp {
            background-color: #000;
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }
        .robot-top {
            display: flex;
            justify-content: flex-end;
            margin-top: 0;
            margin-right: 20px;
            z-index: 10;
        }
        .model-top {
            background-color: #111;
            padding: 10px 20px;
            margin-top: 0;
            margin-bottom: 20px;
            border-radius: 10px;
        }
        .message-container {
            max-width: 900px;
            margin: auto;
            padding-bottom: 140px;
        }
        .robot-bubble {
            position: absolute;
            top: 200px;
            right: 40px;
            background: #222;
            color: #fff;
            padding: 8px 12px;
            border-radius: 10px;
            font-size: 14px;
            animation: fadeInOut 6s ease-in-out;
            white-space: nowrap;
        }
        @keyframes fadeInOut {
            0% {opacity: 0;}
            10% {opacity: 1;}
            90% {opacity: 1;}
            100% {opacity: 0;}
        }
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #111;
            padding: 10px 20px;
            text-align: center;
            z-index: 999;
        }
    </style>
""", unsafe_allow_html=True)

# --- Üst Robot Animasyonu ve Baloncuk ---
st.markdown('<div class="robot-top">', unsafe_allow_html=True)
st_lottie(lottie_robot, height=140, key="robot")
if not st.session_state.robot_message_shown:
    st.markdown('<div class="robot-bubble">Merhaba, ben Efe\'nin yapay zekasıyım 🤖</div>', unsafe_allow_html=True)
    st.session_state.robot_message_shown = True
st.markdown('</div>', unsafe_allow_html=True)

# --- Üst Model Seçici ---
st.markdown('<div class="model-top">', unsafe_allow_html=True)
st.session_state.selected_model = st.selectbox(
    "🧠 Model Seçiniz:",
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
    key="model_selectbox"
)
st.markdown('</div>', unsafe_allow_html=True)

# --- Mesajları Göster ---
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

# --- Footer ---
st.markdown('<div class="footer">© 2025 EfePro AI</div>', unsafe_allow_html=True)
