import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import re
import random
from dotenv import load_dotenv
load_dotenv()

from agent import IklimAynasiAgent
from get_youtube_comments import download_live_comments, video_kunyesi_uret
from tools import duygu_ve_kaygi_analizi, dijital_rol_dedektoru, topluluk_turu_tespit_et, tekil_yorum_izleyici_onerisi

def format_model_options(models, provider):
    formatted = []
    if provider == "gemini":
        free_models = [m for m in models if "flash" in m.lower()]
        other_models = [m for m in models if "flash" not in m.lower()]
        for m in free_models:
            formatted.append(f"[FREE] {m}")
        for m in other_models:
            formatted.append(f"[PRO] {m}")
    elif provider == "groq":
        for m in models:
            formatted.append(f"[FREE] {m}")
    elif provider == "openrouter":
        free_models = [m for m in models if m.endswith(":free")]
        other_models = [m for m in models if not m.endswith(":free")]
        for m in free_models:
            formatted.append(f"[FREE] {m}")
        for m in other_models:
            formatted.append(f"[PRO] {m}")
    else:
        formatted = list(models)
    return formatted

def parse_selected_model(option):
    if not option:
        return ""
    if option.startswith("[FREE] ") or option.startswith("[PRO] "):
        option = option[7:]
    return option

# Sayfa Yapılandırması ve Akademik Tema
st.set_page_config(
    page_title="İzleyici İklimi Aynası",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Editorial CSS (The New Yorker / Academic Style)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Playfair+Display:ital,wght@0,600;0,800;1,600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Lora', Georgia, serif;
        color: #222222;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: #F9F7F1;
    }
    
    [data-testid="stSidebar"] {
        background-color: #F4EFE6;
        border-right: 1px solid #D5CDB5;
    }
    
    .main-title {
        font-family: 'Playfair Display', serif;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0.2rem;
        text-align: center;
        color: #111111;
        letter-spacing: -0.02em;
        border-bottom: 3px double #111111;
        padding-bottom: 15px;
    }
    
    .sub-title {
        font-family: 'Lora', serif;
        font-style: italic;
        color: #444444;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        margin-top: 10px;
        text-align: center;
    }
    
    .premium-card {
        background: #FFFFFF;
        padding: 2rem;
        border: 1px solid #111111;
        box-shadow: 2px 2px 0px #111111;
        margin-bottom: 1.5rem;
    }
    
    .agent-header {
        border-left: 4px solid #8B0000;
        padding-left: 10px;
        font-weight: 600;
        color: #8B0000;
        font-family: 'Playfair Display', serif;
    }
    
    .ethical-warning {
        border: 1px solid #8B0000;
        padding: 10px 15px;
        color: #8B0000;
        font-size: 0.9rem;
        background: #FFF5F5;
        font-style: italic;
    }
    
    .highlight-txt {
        font-weight: 600;
        color: #8B0000;
    }
    
    .comment-bubble {
        background: #FFFFFF;
        padding: 15px 20px;
        margin-bottom: 12px;
        border-left: 3px solid #8B0000;
        border-top: 1px solid #E5E5E5;
        border-right: 1px solid #E5E5E5;
        border-bottom: 1px solid #E5E5E5;
    }
    
    .navigation-box {
        background: #F4EFE6;
        border: 1px solid #111111;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    /* Streamlit overrides for better print aesthetics */
    .stButton>button {
        border: 1px solid #111111;
        border-radius: 0;
        background-color: #FFFFFF;
        color: #111111;
        font-family: 'Playfair Display', serif;
        text-transform: uppercase;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #111111;
        color: #FFFFFF;
        border: 1px solid #111111;
    }
    
    .stAlert {
        border-radius: 0;
        border: 1px solid #111111;
    }
    
    /* Tab Styling and Second Tab Pulse Highlight */
    button[data-baseweb="tab"] {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.05rem !important;
        transition: all 0.3s ease !important;
    }
    
    /* Highlight the second tab */
    button[data-baseweb="tab"]:nth-child(2) {
        border-left: 2px solid #8B0000 !important;
        border-right: 2px solid #8B0000 !important;
        background-color: #FFF2F2 !important;
        color: #8B0000 !important;
        font-weight: bold !important;
        border-radius: 4px 4px 0 0 !important;
        box-shadow: 0 -2px 10px rgba(139, 0, 0, 0.1) !important;
        animation: pulseTab 3s infinite alternate !important;
    }
    
    @keyframes pulseTab {
        0% {
            background-color: #FFF2F2;
            box-shadow: 0 -2px 5px rgba(139, 0, 0, 0.1);
        }
        100% {
            background-color: #FFE0E0;
            box-shadow: 0 -2px 15px rgba(139, 0, 0, 0.3);
        }
    }
</style>
""", unsafe_allow_html=True)

# Ajan Başlatma (Oturum Geçmişini Korumak için st.session_state kullanımı)
if "agent" not in st.session_state:
    st.session_state.agent = IklimAynasiAgent()

agent = st.session_state.agent

# Varsayılan Örnek Video
DEFAULT_VIDEO_ID = "L_a3s0ObozI"

# State İlklendirme
if "video_id" not in st.session_state:
    st.session_state.video_id = DEFAULT_VIDEO_ID
if "video_metadata" not in st.session_state:
    st.session_state.video_metadata = None
if "comments_data" not in st.session_state:
    st.session_state.comments_data = []
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "comment_index" not in st.session_state:
    st.session_state.comment_index = 0
if "show_new_video_input" not in st.session_state:
    st.session_state.show_new_video_input = False
if "default_loaded" not in st.session_state:
    st.session_state.default_loaded = False

# Sidebar: Ajan Bilgileri ve Tanımı
st.sidebar.markdown(f"### Ajan Kimliği")
st.sidebar.markdown(f"**Ajan Rolü:**\n`{agent.role}`")
st.sidebar.markdown("**Sistem Talimatı:**")
st.sidebar.caption(agent.system_instructions)

st.sidebar.divider()
st.sidebar.markdown("### Tez Bağlamı")
st.sidebar.info(
    "Bu çalışma, çevrimiçi/gayriresmi izleyici topluluklarındaki iklimi, jargonları ve "
    "izleyici kimliklerini inceleyerek içerik üreticilerine ve araştırmacılara veri tabanlı "
    "öneriler sunan bir karar destek aracıdır."
)

st.sidebar.divider()
st.sidebar.markdown("### Gözetim ve Etik Sınır")
st.sidebar.markdown(
    "<div class='ethical-warning'>"
    "<b>Uyarı:</b> Ajan çıktıları kesin yargılar barındırmaz. "
    "Eğitim tasarım kararları verilirken insan (öğretmen/araştırmacı) gözetimi zorunludur."
    "</div>", 
    unsafe_allow_html=True
)

st.sidebar.divider()
st.sidebar.markdown("### 🔌 Yapay Zekâ API Ayarları")

# .env'den anahtarları oku
groq_key = os.getenv("GROQ_API_KEY")
or_key = os.getenv("OPENROUTER_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

# API Modellerini Dinamik Olarak Çekme (Oturum hafızasında tutulur)
if "gemini_models" not in st.session_state:
    st.session_state.gemini_models = []
if "groq_models" not in st.session_state:
    st.session_state.groq_models = []
if "openrouter_models" not in st.session_state:
    st.session_state.openrouter_models = []

from api_client import get_available_gemini_models, get_available_groq_models, get_available_openrouter_models

# Anahtarlar var ise ve henüz çekilmediyse arka planda tek seferde yükle
if gemini_key and not gemini_key.startswith("your_") and len(gemini_key.strip()) > 10 and not st.session_state.gemini_models:
    st.session_state.gemini_models = get_available_gemini_models(gemini_key)
if groq_key and not groq_key.startswith("your_") and len(groq_key.strip()) > 10 and not st.session_state.groq_models:
    st.session_state.groq_models = get_available_groq_models(groq_key)
if or_key and not or_key.startswith("your_") and len(or_key.strip()) > 10 and not st.session_state.openrouter_models:
    st.session_state.openrouter_models = get_available_openrouter_models(or_key)

# En güncel modelleri içeren fallback listeler
gemini_fallback = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
groq_fallback = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768", "llama-3.1-8b-instant"]
or_fallback = [
    "meta-llama/llama-3.3-70b-instruct:free", 
    "qwen/qwen3-coder:free", 
    "google/gemma-4-31b-it:free", 
    "google/gemma-4-26b-a4b-it:free", 
    "meta-llama/llama-3.2-3b-instruct:free"
]

gemini_list = st.session_state.gemini_models if st.session_state.gemini_models else gemini_fallback
groq_list = st.session_state.groq_models if st.session_state.groq_models else groq_fallback
or_list = st.session_state.openrouter_models if st.session_state.openrouter_models else or_fallback

gemini_formatted = format_model_options(gemini_list, "gemini")
groq_formatted = format_model_options(groq_list, "groq")
or_formatted = format_model_options(or_list, "openrouter")

# Anahtar durumlarını göster
st.sidebar.caption("Sistemdeki API Durumları:")
if groq_key and not groq_key.startswith("your_") and len(groq_key.strip()) > 10:
    st.sidebar.markdown("- **Groq API:** 🟢 `Yapılandırıldı`")
else:
    st.sidebar.markdown("- **Groq API:** 🔴 `Yapılandırılmadı`")
    
if or_key and not or_key.startswith("your_") and len(or_key.strip()) > 10:
    st.sidebar.markdown("- **OpenRouter:** 🟢 `Yapılandırıldı`")
else:
    st.sidebar.markdown("- **OpenRouter:** 🔴 `Yapılandırılmadı`")
    
if gemini_key and not gemini_key.startswith("your_") and len(gemini_key.strip()) > 10:
    st.sidebar.markdown("- **Gemini API:** 🟢 `Yapılandırıldı`")
else:
    st.sidebar.markdown("- **Gemini API:** 🔴 `Yapılandırılmadı`")

# Sağlayıcı Seçimi
api_provider_selection = st.sidebar.selectbox(
    "Aktif Analiz Sağlayıcısı:",
    ["Kural Tabanlı (Çevrimdışı Fallback)", "Groq API", "OpenRouter", "Gemini API"]
)

# Model Listesi Tanımları
MODELS_MAP = {
    "Groq API": groq_formatted,
    "OpenRouter": or_formatted,
    "Gemini API": gemini_formatted
}

selected_model_option = None
if api_provider_selection != "Kural Tabanlı (Çevrimdışı Fallback)":
    model_list = MODELS_MAP.get(api_provider_selection, []) + ["Özel Model Gir (Custom)..."]
    model_choice = st.sidebar.selectbox("Kullanılacak Model Seçimi:", model_list)
    if model_choice == "Özel Model Gir (Custom)...":
        selected_model_option = st.sidebar.text_input("Özel Model Kodunu Girin (Örn: google/gemma-7b):")
    else:
        selected_model_option = parse_selected_model(model_choice)

# Durumu State'e kaydet
if "active_api" not in st.session_state:
    st.session_state.active_api = None

# Bağlantı Testi
if api_provider_selection != "Kural Tabanlı (Çevrimdışı Fallback)":
    prov_map = {
        "Groq API": ("groq", groq_key),
        "OpenRouter": ("openrouter", or_key),
        "Gemini API": ("gemini", gemini_key)
    }
    provider_code, selected_key = prov_map[api_provider_selection]
    
    if st.sidebar.button("🔌 Servis Bağlantısını Test Et"):
        if selected_key and not selected_key.startswith("your_") and len(selected_key.strip()) > 10:
            from api_client import test_api_connection
            with st.spinner("Bağlantı test ediliyor..."):
                success, model_resolved, msg = test_api_connection(provider_code, selected_key, selected_model=selected_model_option)
                if success:
                    st.session_state.active_api = {
                        "provider": provider_code,
                        "api_key": selected_key,
                        "model": model_resolved
                    }
                    st.sidebar.success(msg)
                else:
                    st.session_state.active_api = None
                    st.sidebar.error(msg)
        else:
            st.sidebar.warning("Seçilen servis için .env dosyasında geçerli bir anahtar bulunamadı.")
else:
    st.session_state.active_api = None


# Ana Sayfa Başlık Alanı
st.markdown("<div class='main-title'>İzleyici İklimi Aynası</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Sanal İzleyici Topluluklarındaki Jargon, Duygu ve Akran Kültürü Çözümleyicisi</div>", unsafe_allow_html=True)

# Sekmelerin Oluşturulması
tab_intro, tab_analiz, tab_loglar = st.tabs([
    "🏠 Ana Sayfa", 
    "⚡ 📊 İzleyici Topluluğu & Analiz Paneli", 
    "🪵 Ajan İşlem Günlüğü (Logs)"
])

# ----------------- TAB 1: ANA SAYFA -----------------
with tab_intro:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 class='agent-header'>🎯 Projenin Amacı ve Kapsamı</h3>", unsafe_allow_html=True)
        st.markdown(
            "Bu proje, asenkron ve gayriresmi video izleme platformlarındaki kültürel iklimi "
            "ve dil örüntülerini analiz eder. Sistemimiz, izleyicilerin yapay zekâ okuryazarlığı düzeylerini, "
            "gelecek kaygılarını, teknik entegrasyon bariyerlerini ve akran yardımlaşma kültürlerini "
            "çözümleyerek içerik üreticileri ve araştırmacılara şu katkıları sunar:"
        )
        st.markdown(
            "- **İklim Analizi:** Topluluk dilini tarayarak grubun 'yaratıcı/estetik' mi, 'teknik/otomasyon' odaklı mı olduğunu otomatik olarak belirler.\n"
            "- **Kişiselleştirilmiş İzleyici Önerileri:** Hem topluluğun geneline yönelik tavsiyeler üretir, hem de tek tek her bir yorum için özel izleyici odaklı yönlendirmeler geliştirir.\n"
            "- **Akran Mentörlüğü Tespiti:** Birbirine teknik destek veren akran liderleri saptar."
        )
    with col2:
        st.markdown("<h3 class='agent-header'>💡 Nasıl Çalışır?</h3>", unsafe_allow_html=True)
        st.markdown(
            "1. **Video Bağlantısı Girin:** YouTube videosunun linkini girdiğinizde, sistem anında video künyesini çeker.\n"
            "2. **Yorumları Çekin:** 'Tüm Yorumlar' seçeneğiyle tüm havuzu indirebilir veya 'Özel Sayıda Yorum' seçeneğiyle rastgele örneklem oluşturabilirsiniz.\n"
            "3. **Toplu ve Tekil Analiz:** Sistem toplu grafikleri ve raporları oluştururken, siz de tekil yorumlar arasında butonlarla gezinebilirsiniz."
        )

# ----------------- TAB 2: ANALİZ VE GÖRSELLEŞTİRME -----------------
with tab_analiz:
    st.markdown("<h2 class='agent-header'>🤖 İzleyici Topluluğu Analiz ve Karar Destek Ajanı</h2>", unsafe_allow_html=True)
    st.write("")
    
    # Ajan Kontrol Paneli Rehberi (Kılavuz)
    st.markdown("""
    <div class='premium-card' style='border-left: 5px solid #8B0000; background-color: #FFF9F9; padding: 1rem; margin-bottom: 1.5rem;'>
        <h4 style='margin: 0 0 5px 0; color: #8B0000; font-family: "Playfair Display", serif;'>⚡ Ajan Kontrol Merkezi</h4>
        <p style='margin: 0; font-size: 0.92rem; color: #333333;'>
            Analiz edilecek YouTube videosunu sol sütundan girin/seçin; API sağlayıcısını ve modelini sağ sütundan seçerek alttaki büyük kırmızı butona basın.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # İlk açılışta varsayılan örnek videoyu otomatik yükle
    if not st.session_state.default_loaded and st.session_state.video_id == DEFAULT_VIDEO_ID and st.session_state.video_metadata is None:
        with st.spinner("Örnek video künyesi yükleniyor..."):
            meta = video_kunyesi_uret(DEFAULT_VIDEO_ID)
            st.session_state.video_metadata = meta
            st.session_state.video_id = DEFAULT_VIDEO_ID
            st.session_state.default_loaded = True

    # İki Sütunlu Grid Layout
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("### 📺 1. Hedef YouTube Videosu")
        
        # YouTube URL veya ID girişi (Her zaman görünür, gizli değil)
        youtube_url = st.text_input(
            "YouTube Video URL veya Video ID:", 
            value=f"https://www.youtube.com/watch?v={st.session_state.video_id}" if len(st.session_state.video_id) == 11 else st.session_state.video_id,
            placeholder="Örn: https://www.youtube.com/watch?v=HK6y8DAPN_0"
        )
        
        btn_get_meta = st.button("🔍 Video Künyesini Çek ve Yükle", use_container_width=True)
        
        if (youtube_url and btn_get_meta) or btn_get_meta:
            if youtube_url:
                video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
                video_id = video_id_match.group(1) if video_id_match else youtube_url.strip()
                
                with st.spinner("Video künyesi çekiliyor..."):
                    meta = video_kunyesi_uret(video_id)
                    st.session_state.video_metadata = meta
                    st.session_state.video_id = video_id
                    st.session_state.comments_data = []
                    st.session_state.analysis_result = None
                    st.session_state.comment_index = 0
                    st.rerun()

        # Künye Gösterim Kartı
        if st.session_state.video_metadata:
            meta = st.session_state.video_metadata
            st.markdown("<div class='premium-card' style='padding: 1.2rem; margin-top: 1rem;'>", unsafe_allow_html=True)
            st.image(meta["thumbnail"], use_container_width=True)
            st.markdown(f"**[{meta['title']}]({meta['url']})**")
            st.markdown(f"👤 Kanal: `{meta['uploader']}`")
            st.markdown(f"👀 İzlenme: `{meta['views']}` | 👍 Beğeni: `{meta.get('likes', 'Bilinmiyor')}`")
            st.markdown(f"💬 Toplam Yorum: `{meta.get('comment_count', 'Bilinmiyor')}`")
            st.markdown("</div>", unsafe_allow_html=True)
            
    with col_right:
        st.markdown("### ⚙️ 2. Ajan Modeli & Analiz Ayarları")
        
        provider_selection = st.selectbox(
            "Analiz Yapılacak Yapay Zekâ Sağlayıcısı / Yöntemi:",
            options=["-- Lütfen Bir Sağlayıcı Seçin --", "Kural Tabanlı Analiz (Çevrimdışı Fallback)", "Gemini API", "Groq API", "OpenRouter"]
        )
        
        selected_api_info = None
        btn_disabled = True
        
        if provider_selection == "-- Lütfen Bir Sağlayıcı Seçin --":
            st.warning("⚠️ Analizi başlatabilmek için lütfen yukarıdan bir sağlayıcı seçin.")
        elif provider_selection == "Kural Tabanlı Analiz (Çevrimdışı Fallback)":
            selected_api_info = None
            btn_disabled = False
        else:
            prov_map = {
                "Groq API": ("groq", groq_key, groq_formatted),
                "OpenRouter": ("openrouter", or_key, or_formatted),
                "Gemini API": ("gemini", gemini_key, gemini_formatted)
            }
            provider_code, selected_key, provider_models = prov_map[provider_selection]
            
            if not selected_key or selected_key.startswith("your_") or len(selected_key.strip()) <= 10:
                st.error(f"❌ {provider_selection} seçildi ancak sistemde geçerli bir API anahtarı yapılandırılmamış. Lütfen sol menüden anahtar durumuna bakın.")
            else:
                model_options = provider_models + ["Özel Model Gir (Custom)..."]
                selected_model_choice = st.selectbox(f"Kullanılacak Yapay Zekâ Modeli ({provider_selection}):", options=model_options)
                
                model_value = ""
                if selected_model_choice == "Özel Model Gir (Custom)...":
                    model_value = st.text_input("Özel Model Kodunu Girin (Örn: google/gemma-7b):").strip()
                else:
                    model_value = parse_selected_model(selected_model_choice)
                    
                if not model_value:
                    st.warning("⚠️ Analizi başlatabilmek için lütfen bir model seçin veya özel model kodu girin.")
                else:
                    selected_api_info = {
                        "provider": provider_code,
                        "api_key": selected_key,
                        "model": model_value
                    }
                    btn_disabled = False
                    
        st.markdown("---")
        st.markdown("**📥 Yorum İndirme ve Örneklem Seçenekleri**")
        download_mode = st.radio("İndirme Modu:", ["Tüm Yorumlar (Maksimum 500 Yorum)", "Özel Sayıda Yorum Limiti (Rastgele Örneklem)"], label_visibility="collapsed")
        custom_count = st.number_input("İndirilecek/Örnekleme Alınacak Yorum Sayısı:", min_value=5, max_value=500, value=30, disabled=(download_mode == "Tüm Yorumlar (Maksimum 500 Yorum)"))
        
        st.markdown("---")
        # Kırmızı ve belirgin primary buton CSS'i
        st.markdown("""
        <style>
        div.stButton > button[kind="primary"] {
            background-color: #8B0000 !important;
            color: #FFFFFF !important;
            border: 2px solid #8B0000 !important;
            box-shadow: 0 4px 15px rgba(139, 0, 0, 0.4) !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Yorumları Çek ve Etnografik Analizleri Yap", type="primary", use_container_width=True, disabled=btn_disabled):
            with st.spinner("Yorumlar indiriliyor ve anonimleştiriliyor..."):
                limit = 500
                raw_comments = download_live_comments(st.session_state.video_id, limit)
                
                if raw_comments:
                    if not download_mode.startswith("Tüm Yorumlar") and len(raw_comments) > custom_count:
                        selected_comments = random.sample(raw_comments, custom_count)
                        for idx, c in enumerate(selected_comments):
                            c["id"] = idx + 1
                    else:
                        selected_comments = raw_comments
                        
                    st.session_state.comments_data = selected_comments
                    st.session_state.comment_index = 0
                    
                    try:
                        progress_bar = st.progress(0.0, text="Yapay zekâ yorumları analiz ediyor...")
                        def update_progress(val):
                            progress_bar.progress(val, text=f"Yapay zekâ yorumları analiz ediyor... %{int(val*100)}")
                            
                        if selected_api_info:
                            selected_api_info["progress_callback"] = update_progress
                            
                        analysis = agent.video_analiz_et(
                            selected_comments, 
                            meta=st.session_state.video_metadata, 
                            api_info=selected_api_info
                        )
                        progress_bar.empty()
                        st.session_state.analysis_result = analysis
                        st.success(f"Başarıyla {len(selected_comments)} yorum indirildi, SHA-256 ile maskelendi ve analiz edildi!")
                    except Exception as err:
                        st.error(f"❌ Yapay Zekâ Analiz Hatası: {err}")
                        st.info("💡 Not: API hatası aldınız. API anahtarınızın veya seçtiğiniz model isminin doğruluğundan emin olun. Gerekirse 'Kural Tabanlı Analiz (Çevrimdışı Fallback)' yöntemini kullanabilirsiniz.")
                else:
                    st.error("Yorumlar çekilemedi. Lütfen bağlantıyı kontrol edin veya videonun yorumlara açık olduğundan emin olun.")
                    
    # Analiz Sonuçları Var ise Göster
    if st.session_state.analysis_result and st.session_state.comments_data:
        analysis = st.session_state.analysis_result
        comments = st.session_state.comments_data
        
        st.markdown("---")
        # Analizde Hangi Modelin Kullanıldığını Göster (Kullanıcı Talebi)
        model_name = analysis.get("model_info", "Kural Tabanlı Analiz (Çevrimdışı)")
        st.info(f"**Kullanılan Analiz Modeli/Sistem:** {model_name}")
        
        st.markdown(f"### Otomatik Saptanan Topluluk Türü: <span style='color:#8B0000;'>{analysis['topluluk_turu_str']}</span>", unsafe_allow_html=True)
        
        editorial_colors = ["#8B0000", "#111111", "#444444", "#777777", "#A5A5A5", "#D5CDB5", "#EBEBEB"]
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("#### Duygu ve Kaygı İklimi")
            duygu_df = pd.DataFrame(list(analysis["duygu"].items()), columns=["Kategori", "Sıklık"])
            fig_d = px.pie(duygu_df, values="Sıklık", names="Kategori", title="Duygu ve Kaygı Dağılımı", color_discrete_sequence=editorial_colors)
            st.plotly_chart(fig_d, use_container_width=True)
        with col_g2:
            st.markdown("#### Dijital Rol Dağılımı")
            rol_df = pd.DataFrame(list(analysis["rol"].items()), columns=["Rol", "Sıklık"])
            fig_r = px.bar(rol_df, x="Rol", y="Sıklık", title="Dijital Rol Dağılımı", color="Rol", color_discrete_sequence=editorial_colors)
            st.plotly_chart(fig_r, use_container_width=True)
            
        st.markdown("---")
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown(analysis["rapor"], unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # PDF Rapor İndirme Butonu
        try:
            from pdf_generator import generate_analysis_pdf
            pdf_data = generate_analysis_pdf(st.session_state.video_metadata, analysis, comments)
            st.download_button(
                label="Analiz Raporunu PDF Olarak İndir",
                data=pdf_data,
                file_name=f"izleyici_iklimi_analiz_raporu_{st.session_state.video_id}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as pdf_err:
            st.warning(f"PDF Raporu oluşturulamadı: {pdf_err}")

        
        # TEKİL YORUM GEZİNTİ PANELİ
        st.markdown("---")
        st.markdown("### Tekil Yorum Analizi ve Gezinti")
        st.caption("Yorumlar arasında tek tek gezinebilir, her bir izleyici yorumu için ajanın ürettiği özel izleyici odaklı tavsiyeyi inceleyebilirsiniz.")
        
        total_len = len(comments)
        current_idx = st.session_state.comment_index
        
        # Sınır denetimi
        if current_idx >= total_len:
            current_idx = 0
            st.session_state.comment_index = 0
            
        c_item = comments[current_idx]
        c_id = c_item.get("id")
        
        # LLM analizi yapılmışsa oradan çek, yoksa kural tabanlı yap
        llm_results = analysis.get("llm_results")
        c_llm = None
        if llm_results:
            # İlgili yorumu id ile bul
            c_llm = next((r for r in llm_results if r.get("original_id") == c_id), None)
            
        if c_llm:
            c_duygu = f"{c_llm.get('category')} ({c_llm.get('sentiment')})"
            c_rol = c_llm.get("role")
            c_tavsiye = tekil_yorum_izleyici_onerisi(c_item["comment"], c_llm.get("sentiment", ""), c_rol, analysis["topluluk_turu"])
            c_reasoning = c_llm.get("reasoning", "")
            c_devices = c_llm.get("rhetorical_devices", [])
        else:
            c_girdi = [c_item]
            c_duygu = list(duygu_ve_kaygi_analizi(c_girdi, analysis["topluluk_turu"]).keys())[0]
            c_rol = list(dijital_rol_dedektoru(c_girdi, analysis["topluluk_turu"]).keys())[0]
            c_tavsiye = tekil_yorum_izleyici_onerisi(c_item["comment"], c_duygu, c_rol, analysis["topluluk_turu"])
            c_reasoning = ""
            c_devices = []
        
        st.markdown(f"<div class='navigation-box'>", unsafe_allow_html=True)
        st.write(f"**Yorum {current_idx + 1} / {total_len}**")
        
        st.markdown(
            f"<div class='comment-bubble'>"
            f"<b>{c_item['username']}</b> ({c_item.get('likes', 0)} beğeni)<br/>"
            f"<p style='margin-top:6px; color:#111111; font-size:1.1rem; font-family:\"Playfair Display\", serif;'>{c_item['comment']}</p>"
            f"</div>", 
            unsafe_allow_html=True
        )
        
        col_nav_res1, col_nav_res2 = st.columns(2)
        with col_nav_res1:
            st.markdown(f"**Duygu/Kaygı Kategorisi:** `{c_duygu}`")
        with col_nav_res2:
            st.markdown(f"**Saptanan Topluluk Rolü:** `{c_rol}`")
            
        if c_llm:
            st.markdown("---")
            st.markdown(f"**LLM Analiz Detayları:**")
            st.markdown(f"> *{c_reasoning}*")
            if c_devices:
                st.markdown(f"**Saptanan Retorik:** `{'`, `'.join(c_devices)}`")
            
        st.markdown(f"<div style='margin-top:10px; padding:12px; border-left:3px solid #8B0000; background:#FFF5F5;'>", unsafe_allow_html=True)
        st.markdown(f"**Özel İzleyici Odaklı Öneri / Müdahale:**<br/>{c_tavsiye}", unsafe_allow_html=True)
        st.markdown(f"</div>", unsafe_allow_html=True)
        st.markdown(f"</div>", unsafe_allow_html=True)
        
        # Gezinti Butonları
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("ÖNCEKİ YORUM", use_container_width=True):
            st.session_state.comment_index = (st.session_state.comment_index - 1) % total_len
            st.rerun()
        if col_btn2.button("SONRAKİ YORUM", use_container_width=True):
            st.session_state.comment_index = (st.session_state.comment_index + 1) % total_len
            st.rerun()
            
        # Ham Veri İnceleme
        with st.expander("🛠️ İndirilen Tüm Yorumların Ham Kodlama Matrisi (Tablo)"):
            detailed_table = []
            for item in comments:
                single_girdi = [item]
                single_duygu = list(duygu_ve_kaygi_analizi(single_girdi, analysis["topluluk_turu"]).keys())[0]
                single_rol = list(dijital_rol_dedektoru(single_girdi, analysis["topluluk_turu"]).keys())[0]
                detailed_table.append({
                    "Kullanıcı": item["username"],
                    "Yorum": item["comment"],
                    "Saptanan Kategori": single_duygu,
                    "Saptanan Rol": single_rol,
                    "Beğeni": item.get("likes", 0)
                })
            st.dataframe(pd.DataFrame(detailed_table), use_container_width=True)

# ----------------- TAB 3: BELLEK VE LOG KAYITLARI -----------------
with tab_loglar:
    st.markdown("### 🪵 Ajan İşlem Günlüğü (Bellek / Karar Geçmişi)")
    st.caption("Yönergedeki 'En az oturum içi geçmiş veya işlem günlüğü tutulmalıdır' maddesinin kanıtıdır.")
    
    log_df = pd.DataFrame(agent.get_logs())
    st.dataframe(log_df, use_container_width=True)

