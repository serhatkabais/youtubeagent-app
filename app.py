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

# Sayfa Yapılandırması (Streamlit gereği ilk çağrı olmalı)
st.set_page_config(
    page_title="İzleyici İklimi Aynası / Audience Climate Mirror",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dil Seçimi / Language Selection
lang_choice = st.sidebar.radio("Dil / Language 🌐", ["Türkçe", "English"], index=0, horizontal=True)
lang = "tr" if lang_choice == "Türkçe" else "en"

# Language Translation Dictionary
UI_TXT = {
    "tr": {
        "page_title": "İzleyici İklimi Aynası",
        "sidebar_expander": "ℹ️ Ajan Tanımı ve Akademik Bağlam",
        "agent_id": "Ajan Kimliği",
        "agent_role": "Ajan Rolü",
        "system_instruction": "Sistem Talimatı",
        "thesis_context": "Tez Bağlamı",
        "thesis_desc": "Bu çalışma, çevrimiçi/gayriresmi izleyici topluluklarındaki iklimi, jargonları ve izleyici kimliklerini inceleyerek içerik üreticilerine ve araştırmacılara veri tabanlı öneriler sunan bir karar destek aracıdır.",
        "ethical_boundary": "Gözetim ve Etik Sınır",
        "ethical_desc": "<b>Uyarı:</b> Ajan çıktıları kesin yargılar barındırmaz. Eğitim tasarım kararları verilirken insan (öğretmen/araştırmacı) gözetimi zorunludur.",
        "api_settings": "🔌 Yapay Zekâ API Ayarları",
        "api_status": "Sistemdeki API Durumları:",
        "configured": "Yapılandırıldı",
        "not_configured": "Yapılandırılmadı",
        "select_models": "### 🛠️ Mutabakat Modellerini Seç",
        "model_config": "Model Yapılandırması",
        "provider": "Sağlayıcı",
        "custom_model": "Özel Model Gir (Custom)...",
        "custom_model_code": "Özel Model Kodu:",
        "test_connections": "🔌 Servis Bağlantılarını Test Et",
        "testing_conn": "Seçilen 3 modelin bağlantıları test ediliyor...",
        "no_key": "sağlayıcısı için geçerli bir API anahtarı bulunamadı.",
        "conn_success": "bağlantısı başarılı!",
        "conn_err": "bağlantı hatası:",
        "all_tests_passed": "🏆 Tüm model bağlantı testleri başarıyla tamamlandı!",
        "main_title": "İzleyici İklimi Aynası",
        "main_subtitle": "Sanal İzleyici Topluluklarındaki Jargon, Duygu ve Akran Kültürü Çözümleyicisi",
        "tab_home": "🏠 Ana Sayfa",
        "tab_analysis": "🔴 📊 ANALİZ PANELİ (Buradan Başlatın) 👈",
        "tab_logs": "🪵 Ajan İşlem Günlüğü (Logs)",
        "purpose": "🎯 Projenin Amacı ve Kapsamı",
        "purpose_desc": "Bu proje, asenkron ve gayriresmi video izleme platformlarındaki kültürel iklimi ve dil örüntülerini analiz eder. Sistemimiz, izleyicilerin yapay zekâ okuryazarlığı düzeylerini, gelecek kaygılarını, teknik entegrasyon bariyerlerini ve akran yardımlaşma kültürlerini çözümleyerek içerik üreticileri ve araştırmacılara şu katkıları sunar:\n\n- **İklim Analizi:** Topluluk dilini tarayarak grubun 'yaratıcı/estetik' mi, 'teknik/otomasyon' odaklı mı olduğunu otomatik olarak belirler.\n- **Kişiselleştirilmiş İzleyici Önerileri:** Hem topluluğun geneline yönelik tavsiyeler üretir, hem de tek tek her bir yorum için özel izleyici odaklı yönlendirmeler geliştirir.\n- **Akran Mentörlüğü Tespiti:** Birbirine teknik destek veren akran liderleri saptar.",
        "how_it_works": "💡 Nasıl Çalışır?",
        "how_it_works_desc": "1. **Video Bağlantısı Girin:** YouTube videosunun linkini girdiğinizde, sistem anında video künyesini çeker.\n2. **Yorumları Çekin:** 'Tüm Yorumlar' seçeneğiyle tüm havuzu indirebilir veya 'Özel Sayıda Yorum' seçeneğiyle rastgele örneklem oluşturabilirsiniz.\n3. **Toplu ve Tekil Analiz:** Sistem toplu grafikleri ve raporları oluştururken, siz de tekil yorumlar arasında butonlarla gezinebilirsiniz.",
        "agent_title": "🤖 İzleyici Topluluğu Analiz ve Karar Destek Ajanı",
        "control_center": "⚡ Ajan Kontrol Merkezi",
        "control_desc": "Analiz edilecek YouTube videosunu sol sütundan girin/seçin; API sağlayıcısını ve modelini sağ sütundan seçerek alttaki büyük kırmızı butona basın.",
        "target_video": "📺 1. Hedef YouTube Videosu",
        "video_input_label": "YouTube Video URL veya Video ID:",
        "btn_meta": "🔍 Video Künyesini Çek ve Yükle",
        "fetching_meta": "Video künyesi çekiliyor...",
        "channel": "Kanal",
        "views": "İzlenme",
        "likes": "Beğeni",
        "total_comments": "Toplam Yorum",
        "model_settings": "⚙️ 2. Ajan Modeli & Analiz Ayarları",
        "key_missing_err": "❌ Mutabakat modellerinden biri için geçerli bir API anahtarı bulunamadı. Lütfen anahtar durumlarını sol menüden kontrol edin.",
        "consensus_active": "🎓 **Çoklu LLM Mutabakat Modu Aktif**",
        "selected_models": "Seçilen Modeller:",
        "sampling_options": "📥 Yorum İndirme ve Örneklem Seçenekleri",
        "download_all": "Tüm Yorumlar (Maksimum 500 Yorum)",
        "download_custom": "Özel Sayıda Yorum Limiti (Rastgele Örneklem)",
        "comment_count_label": "İndirilecek/Örnekleme Alınacak Yorum Sayısı:",
        "btn_analyze": "🚀 Yorumları Çek ve Etnografik Analizleri Yap",
        "fetching_comments": "Yorumlar indiriliyor ve anonimleştiriliyor...",
        "success_analysis": "Başarıyla {count} yorum indirildi, SHA-256 ile maskelendi ve analiz edildi!",
        "fetching_comments_err": "Yorumlar çekilemedi. Lütfen bağlantıyı kontrol edin veya videonun yorumlara açık olduğundan emin olun.",
        "used_model": "Kullanılan Analiz Modeli/Sistem:",
        "reliability_index": "🎓 Akademik Güvenilirlik & Mutabakat İndeksi",
        "reliability_desc": "Bu analiz, 3 farklı yapay zekâ modelinin paralel değerlendirmeleri karşılaştırılarak oluşturulmuştur. Aşağıdaki metrikler, modeller arasındaki tutarlılığı (Güvenilirlik) akademik standartlarda (Fleiss' Kappa) göstermektedir.",
        "distribution_summary": "Değerlendirme Dağılım Özeti (N={count} Yorum):",
        "full_consensus": "Tam Mutabakat (3/3)",
        "full_consensus_desc": "yorum (%{pct}) - Tüm alanlarda 3 model de aynı kodlamayı yaptı.",
        "majority_decision": "Çoğunluk Kararı (2/3)",
        "majority_decision_desc": "yorum (%{pct}) - Modeller arasında 2/3 oylama ile karar verildi.",
        "disagreement": "Uyuşmazlık (1/3)",
        "disagreement_desc": "yorum (%{pct}) - 3 model de farklı kodlamalar yaptı (Birincil model kararı uygulandı).",
        "overall_consensus": "Genel Mutabakat Oranı",
        "sentiment_kappa": "Duygu Analizi Kappa (κ)",
        "category_kappa": "Kategori Sınıflandırma Kappa (κ)",
        "role_kappa": "Rol Sınıflandırma Kappa (κ)",
        "detected_community": "Otomatik Saptanan Topluluk Türü:",
        "sentiment_climate": "Duygu ve Kaygı İklimi",
        "sentiment_dist": "Duygu ve Kaygı Dağılımı",
        "role_dist": "Dijital Rol Dağılımı",
        "model_consensus": "Modeller Arası Mutabakat",
        "consensus_dist": "Mutabakat Dağılımı",
        "download_pdf": "Analiz Raporunu PDF Olarak İndir",
        "individual_analysis": "### Tekil Yorum Analizi ve Gezinti",
        "individual_desc": "Yorumlar arasında tek tek gezinebilir, her bir izleyici yorumu için ajanın ürettiği özel izleyici odaklı tavsiyeyi inceleyebilirsiniz.",
        "comment_num": "Yorum {index} / {total}",
        "category_col": "Duygu/Kaygı Kategorisi:",
        "role_col": "Saptanan Topluluk Rolü:",
        "consensus_level_col": "Güven Derecesi (Mutabakat):",
        "analysis_details_col": "LLM Analiz Detayları:",
        "detected_rhetoric": "Saptanan Retorik:",
        "special_advice": "Özel İzleyici Odaklı Öneri / Müdahale:",
        "btn_prev": "ÖNCEKİ YORUM",
        "btn_next": "SONRAKİ YORUM",
        "raw_matrix": "🛠️ İndirilen Tüm Yorumların Ham Kodlama Matrisi (Tablo)",
        "raw_user": "Kullanıcı",
        "raw_comment": "Yorum",
        "raw_sentiment": "Duygu",
        "raw_category": "Kategori",
        "raw_role": "Saptanan Rol",
        "raw_consensus": "Mutabakat",
        "raw_confidence": "Güven Skoru",
        "raw_likes": "Beğeni",
        "logs_title": "### 🪵 Ajan İşlem Günlüğü (Bellek / Karar Geçmişi)",
        "logs_desc": "Yönergedeki 'En az oturum içi geçmiş veya işlem günlüğü tutulmalıdır' maddesinin kanıtıdır.",
        "original_lang": "Orijinal Dil",
        "translation": "Çeviri"
    },
    "en": {
        "page_title": "Audience Climate Mirror",
        "sidebar_expander": "ℹ️ Agent Definition & Academic Context",
        "agent_id": "Agent Identity",
        "agent_role": "Agent Role",
        "system_instruction": "System Instruction",
        "thesis_context": "Thesis Context",
        "thesis_desc": "This study is a decision support tool that analyzes the climate, jargon, and viewer identities in online/informal learning audience communities to offer data-backed suggestions to content creators and researchers.",
        "ethical_boundary": "Oversight & Ethical Boundaries",
        "ethical_desc": "<b>Warning:</b> Agent outputs do not constitute absolute judgments. Human (teacher/researcher) oversight is mandatory when making instructional design decisions.",
        "api_settings": "🔌 AI API Settings",
        "api_status": "System API Statuses:",
        "configured": "Configured",
        "not_configured": "Not Configured",
        "select_models": "### 🛠️ Select Consensus Models",
        "model_config": "Model Configuration",
        "provider": "Provider",
        "custom_model": "Enter Custom Model...",
        "custom_model_code": "Custom Model Code:",
        "test_connections": "🔌 Test Service Connections",
        "testing_conn": "Testing connections of the 3 selected models...",
        "no_key": "valid API key not found for provider.",
        "conn_success": "connection successful!",
        "conn_err": "connection error:",
        "all_tests_passed": "🏆 All model connection tests completed successfully!",
        "main_title": "Audience Climate Mirror",
        "main_subtitle": "Jargon, Emotion, and Peer Culture Analyzer in Virtual Audience Communities",
        "tab_home": "🏠 Home Page",
        "tab_analysis": "🔴 📊 ANALYSIS PANEL (Start Here) 👈",
        "tab_logs": "🪵 Agent Action Logs",
        "purpose": "🎯 Project Purpose and Scope",
        "purpose_desc": "This project analyzes the cultural climate and language patterns on asynchronous and informal video viewing platforms. Our system resolves viewers' AI literacy levels, future anxieties, technical integration barriers, and peer assistance cultures, contributing the following to content creators and researchers:\n\n- **Climate Analysis:** Scans the community language to automatically determine if the group is 'creative/aesthetic' or 'technical/automation' oriented.\n- **Personalized Audience Recommendations:** Generates recommendations for the general community, as well as specific audience-oriented guidance for each individual comment.\n- **Peer Mentorship Detection:** Detects peer leaders providing technical support to each other.",
        "how_it_works": "💡 How it Works",
        "how_it_works_desc": "1. **Enter Video Link:** When you enter the YouTube video link, the system instantly fetches the video metadata.\n2. **Fetch Comments:** You can download the entire pool with the 'All Comments' option or create a random sample with the 'Custom Comment Limit' option.\n3. **Aggregated & Individual Analysis:** While the system generates aggregated charts and reports, you can navigate between individual comments using navigation buttons.",
        "agent_title": "🤖 Audience Community Analysis & Decision Support Agent",
        "control_center": "⚡ Agent Control Center",
        "control_desc": "Enter/select the YouTube video to analyze on the left; select the API provider and model on the right, and click the big red button below.",
        "target_video": "📺 1. Target YouTube Video",
        "video_input_label": "YouTube Video URL or Video ID:",
        "btn_meta": "🔍 Fetch and Load Video Metadata",
        "fetching_meta": "Fetching video metadata...",
        "channel": "Channel",
        "views": "Views",
        "likes": "Likes",
        "total_comments": "Total Comments",
        "model_settings": "⚙️ 2. Agent Model & Analysis Settings",
        "key_missing_err": "❌ A valid API key was not found for one of the consensus models. Please check the key statuses in the left menu.",
        "consensus_active": "🎓 **Multi-LLM Consensus Mode Active**",
        "selected_models": "Selected Models:",
        "sampling_options": "📥 Comment Download & Sampling Options",
        "download_all": "All Comments (Maximum 500 Comments)",
        "download_custom": "Custom Comment Count Limit (Random Sample)",
        "comment_count_label": "Number of Comments to Download/Sample:",
        "btn_analyze": "🚀 Fetch Comments & Perform Ethnographic Analysis",
        "fetching_comments": "Downloading and anonymizing comments...",
        "success_analysis": "Successfully downloaded {count} comments, masked with SHA-256, and analyzed!",
        "fetching_comments_err": "Comments could not be fetched. Please check the link or ensure the video is open to comments.",
        "used_model": "Analysis Model/System Used:",
        "reliability_index": "🎓 Academic Reliability & Consensus Index",
        "reliability_desc": "This analysis was created by comparing the parallel evaluations of 3 different AI models. The metrics below show the consistency (Reliability) between models at academic standards (Fleiss' Kappa).",
        "distribution_summary": "Evaluation Distribution Summary (N={count} Comments):",
        "full_consensus": "Full Consensus (3/3)",
        "full_consensus_desc": "comments (%{pct}) - All 3 models made the same coding in all fields.",
        "majority_decision": "Majority Decision (2/3)",
        "majority_decision_desc": "comments (%{pct}) - Decided with 2/3 voting among models.",
        "disagreement": "Disagreement (1/3)",
        "disagreement_desc": "comments (%{pct}) - All 3 models made different codings (Primary model decision applied).",
        "overall_consensus": "Overall Consensus Rate",
        "sentiment_kappa": "Sentiment Analysis Kappa (κ)",
        "category_kappa": "Category Classification Kappa (κ)",
        "role_kappa": "Role Detection Kappa (κ)",
        "detected_community": "Automatically Detected Community Type:",
        "sentiment_climate": "Sentiment and Anxiety Climate",
        "sentiment_dist": "Sentiment and Anxiety Distribution",
        "role_dist": "Digital Role Distribution",
        "model_consensus": "Consensus Across Models",
        "consensus_dist": "Consensus Distribution",
        "download_pdf": "Download Analysis Report as PDF",
        "individual_analysis": "### Individual Comment Analysis and Navigation",
        "individual_desc": "You can navigate through comments one by one and review the custom audience-focused recommendation produced by the agent for each comment.",
        "comment_num": "Comment {index} / {total}",
        "category_col": "Sentiment/Anxiety Category:",
        "role_col": "Detected Community Role:",
        "consensus_level_col": "Confidence Level (Consensus):",
        "analysis_details_col": "LLM Analysis Details:",
        "detected_rhetoric": "Detected Rhetorical Devices:",
        "special_advice": "Special Audience-Oriented Recommendation / Intervention:",
        "btn_prev": "PREVIOUS COMMENT",
        "btn_next": "NEXT COMMENT",
        "raw_matrix": "🛠️ Raw Coding Matrix of All Downloaded Comments (Table)",
        "raw_user": "User",
        "raw_comment": "Comment",
        "raw_sentiment": "Sentiment",
        "raw_category": "Category",
        "raw_role": "Detected Role",
        "raw_consensus": "Consensus",
        "raw_confidence": "Confidence Score",
        "raw_likes": "Likes",
        "logs_title": "### 🪵 Agent Action Log (Memory / Decision History)",
        "logs_desc": "Evidence for the instruction 'At least inside-session history or transaction log must be kept'.",
        "original_lang": "Original Language",
        "translation": "Translation"
    }
}

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
    if option.startswith("[FREE] "):
        return option[7:]
    if option.startswith("[PRO] "):
        return option[6:]
    return option

def get_model_index(model_list, target_model_name):
    for idx, name in enumerate(model_list):
        if target_model_name.lower() in name.lower():
            return idx
    return 0

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
    
    button[data-baseweb="tab"] {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.05rem !important;
        transition: all 0.3s ease !important;
    }
    
    button[data-baseweb="tab"]:nth-child(2) {
        border: 2px solid #8B0000 !important;
        border-radius: 6px !important;
        font-weight: 800 !important;
        box-shadow: 0 0 10px rgba(139, 0, 0, 0.2) !important;
        animation: intenseBlink 1.2s infinite alternate !important;
    }
    
    @keyframes intenseBlink {
        0% {
            background-color: #FFF2F2 !important;
            color: #8B0000 !important;
            box-shadow: 0 0 5px rgba(139, 0, 0, 0.2) !important;
            transform: scale(1);
        }
        50% {
            background-color: #FFD2D2 !important;
            color: #D32F2F !important;
            box-shadow: 0 0 15px rgba(139, 0, 0, 0.6) !important;
        }
        100% {
            background-color: #FF8A8A !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 25px rgba(255, 0, 0, 0.8) !important;
            transform: scale(1.03);
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
with st.sidebar.expander(UI_TXT[lang]["sidebar_expander"], expanded=False):
    st.markdown(f"### {UI_TXT[lang]['agent_id']}")
    st.markdown(f"**{UI_TXT[lang]['agent_role']}:**\n`{agent.role if lang == 'tr' else 'Audience Communities Climate and Jargon Analysis Decision Support Agent'}`")
    st.markdown(f"**{UI_TXT[lang]['system_instruction']}:**")
    st.caption(agent.system_instructions if lang == 'tr' else "You are a decision support agent reporting audience climate to instructional designers and content creators by examining implicit language, jargon, future anxieties, excitements, and community roles in educational video comments.")
    st.divider()
    st.markdown(f"### {UI_TXT[lang]['thesis_context']}")
    st.info(UI_TXT[lang]["thesis_desc"])
    st.divider()
    st.markdown(f"### {UI_TXT[lang]['ethical_boundary']}")
    st.markdown(
        f"<div class='ethical-warning'>{UI_TXT[lang]['ethical_desc']}</div>", 
        unsafe_allow_html=True
    )
st.sidebar.markdown(f"### {UI_TXT[lang]['api_settings']}")

# .env'den anahtarları oku
groq_key = os.getenv("GROQ_API_KEY")
or_key = os.getenv("OPENROUTER_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

# API Modellerini Dinamik Olarak Çekme
if "gemini_models" not in st.session_state:
    st.session_state.gemini_models = []
if "groq_models" not in st.session_state:
    st.session_state.groq_models = []
if "openrouter_models" not in st.session_state:
    st.session_state.openrouter_models = []

from api_client import get_available_gemini_models, get_available_groq_models, get_available_openrouter_models

if gemini_key and not gemini_key.startswith("your_") and len(gemini_key.strip()) > 10 and not st.session_state.gemini_models:
    st.session_state.gemini_models = get_available_gemini_models(gemini_key)
if groq_key and not groq_key.startswith("your_") and len(groq_key.strip()) > 10 and not st.session_state.groq_models:
    st.session_state.groq_models = get_available_groq_models(groq_key)
if or_key and not or_key.startswith("your_") and len(or_key.strip()) > 10 and not st.session_state.openrouter_models:
    st.session_state.openrouter_models = get_available_openrouter_models(or_key)

gemini_fallback = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
groq_fallback = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768", "llama-3.1-8b-instant"]
or_fallback = [
    "deepseek/deepseek-chat",
    "meta-llama/llama-3.3-70b-instruct", 
    "qwen/qwen-2.5-72b-instruct",
    "google/gemini-flash-1.5",
    "meta-llama/llama-3.1-8b-instruct"
]

gemini_list = st.session_state.gemini_models if st.session_state.gemini_models else gemini_fallback
groq_list = st.session_state.groq_models if st.session_state.groq_models else groq_fallback
or_list = st.session_state.openrouter_models if st.session_state.openrouter_models else or_fallback

gemini_formatted = format_model_options(gemini_list, "gemini")
groq_formatted = format_model_options(groq_list, "groq")
or_formatted = format_model_options(or_list, "openrouter")

# Anahtar durumlarını göster
st.sidebar.caption(UI_TXT[lang]["api_status"])
if groq_key and not groq_key.startswith("your_") and len(groq_key.strip()) > 10:
    st.sidebar.markdown(f"- **Groq API:** 🟢 `{UI_TXT[lang]['configured']}`")
else:
    st.sidebar.markdown(f"- **Groq API:** 🔴 `{UI_TXT[lang]['not_configured']}`")
    
if or_key and not or_key.startswith("your_") and len(or_key.strip()) > 10:
    st.sidebar.markdown(f"- **OpenRouter:** 🟢 `{UI_TXT[lang]['configured']}`")
else:
    st.sidebar.markdown(f"- **OpenRouter:** 🔴 `{UI_TXT[lang]['not_configured']}`")
    
if gemini_key and not gemini_key.startswith("your_") and len(gemini_key.strip()) > 10:
    st.sidebar.markdown(f"- **Gemini API:** 🟢 `{UI_TXT[lang]['configured']}`")
else:
    st.sidebar.markdown(f"- **Gemini API:** 🔴 `{UI_TXT[lang]['not_configured']}`")

MODELS_MAP = {
    "Groq API": (groq_formatted, groq_key, "groq"),
    "OpenRouter": (or_formatted, or_key, "openrouter"),
    "Gemini API": (gemini_formatted, gemini_key, "gemini")
}

consensus_mode = True
models_config_list = []

st.sidebar.markdown(UI_TXT[lang]["select_models"])

# Model 1
st.sidebar.markdown(f"**1. {UI_TXT[lang]['model_config']}**")
m1_prov = st.sidebar.selectbox(f"{UI_TXT[lang]['provider']} 1:", ["OpenRouter", "Gemini API", "Groq API"], key="m1_prov")
m1_models_list, m1_key, m1_code = MODELS_MAP[m1_prov]
m1_default_idx = get_model_index(m1_models_list, "deepseek/deepseek-chat")
if m1_default_idx == 0:
    m1_default_idx = get_model_index(m1_models_list, "deepseek-chat")
if m1_default_idx == 0:
    m1_default_idx = get_model_index(m1_models_list, "deepseek")
m1_choice = st.sidebar.selectbox("Model 1:", m1_models_list + [UI_TXT[lang]["custom_model"]], index=m1_default_idx, key="m1_choice")
m1_val = ""
if m1_choice == UI_TXT[lang]["custom_model"]:
    m1_val = st.sidebar.text_input(f"{UI_TXT[lang]['custom_model_code']} 1:", key="m1_custom").strip()
else:
    m1_val = parse_selected_model(m1_choice)
models_config_list.append({"provider": m1_code, "api_key": m1_key, "model": m1_val})

# Model 2
st.sidebar.markdown(f"**2. {UI_TXT[lang]['model_config']}**")
m2_prov = st.sidebar.selectbox(f"{UI_TXT[lang]['provider']} 2:", ["OpenRouter", "Gemini API", "Groq API"], key="m2_prov")
m2_models_list, m2_key, m2_code = MODELS_MAP[m2_prov]
m2_default_idx = get_model_index(m2_models_list, "google/gemini-2.0-flash")
if m2_default_idx == 0:
    m2_default_idx = get_model_index(m2_models_list, "gemini-2.0-flash")
if m2_default_idx == 0:
    m2_default_idx = get_model_index(m2_models_list, "gemini-flash")
if m2_default_idx == 0 and len(m2_models_list) > 1:
    m2_default_idx = 1
m2_choice = st.sidebar.selectbox("Model 2:", m2_models_list + [UI_TXT[lang]["custom_model"]], index=m2_default_idx, key="m2_choice")
m2_val = ""
if m2_choice == UI_TXT[lang]["custom_model"]:
    m2_val = st.sidebar.text_input(f"{UI_TXT[lang]['custom_model_code']} 2:", key="m2_custom").strip()
else:
    m2_val = parse_selected_model(m2_choice)
models_config_list.append({"provider": m2_code, "api_key": m2_key, "model": m2_val})

# Model 3
st.sidebar.markdown(f"**3. {UI_TXT[lang]['model_config']}**")
m3_prov = st.sidebar.selectbox(f"{UI_TXT[lang]['provider']} 3:", ["OpenRouter", "Gemini API", "Groq API"], key="m3_prov")
m3_models_list, m3_key, m3_code = MODELS_MAP[m3_prov]
m3_default_idx = get_model_index(m3_models_list, "qwen/qwen3-30b-a3b")
if m3_default_idx == 0:
    m3_default_idx = get_model_index(m3_models_list, "qwen3-30b")
if m3_default_idx == 0:
    m3_default_idx = get_model_index(m3_models_list, "qwen")
if m3_default_idx == 0 and len(m3_models_list) > 2:
    m3_default_idx = 2
m3_choice = st.sidebar.selectbox("Model 3:", m3_models_list + [UI_TXT[lang]["custom_model"]], index=m3_default_idx, key="m3_choice")
m3_val = ""
if m3_choice == UI_TXT[lang]["custom_model"]:
    m3_val = st.sidebar.text_input(f"{UI_TXT[lang]['custom_model_code']} 3:", key="m3_custom").strip()
else:
    m3_val = parse_selected_model(m3_choice)
models_config_list.append({"provider": m3_code, "api_key": m3_key, "model": m3_val})

# Durumu State'e kaydet
if "active_api" not in st.session_state:
    st.session_state.active_api = None

# Bağlantı Testi
if st.sidebar.button(UI_TXT[lang]["test_connections"]):
    from api_client import test_api_connection
    all_ok = True
    with st.spinner(UI_TXT[lang]["testing_conn"]):
        for idx, cfg in enumerate(models_config_list):
            p_code = cfg["provider"]
            key = cfg["api_key"]
            model_val = cfg["model"]
            
            if not key or key.startswith("your_") or len(key.strip()) <= 10:
                st.sidebar.error(f"❌ Model {idx+1} {UI_TXT[lang]['no_key']}")
                all_ok = False
                break
                
            success, model_resolved, msg = test_api_connection(p_code, key, selected_model=model_val)
            if success:
                st.sidebar.success(f"🟢 Model {idx+1} ({model_resolved}) {UI_TXT[lang]['conn_success']}")
            else:
                st.sidebar.error(f"🔴 Model {idx+1} {UI_TXT[lang]['conn_err']} {msg}")
                all_ok = False
                
        if all_ok:
            st.session_state.active_api = {
                "models_config": models_config_list,
                "consensus_mode": True
            }
            st.sidebar.success(UI_TXT[lang]["all_tests_passed"])
        else:
            st.session_state.active_api = None

# Ana Sayfa Başlık Alanı
st.markdown(f"<div class='main-title'>{UI_TXT[lang]['main_title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-title'>{UI_TXT[lang]['main_subtitle']}</div>", unsafe_allow_html=True)

# Sekmelerin Oluşturulması
tab_intro, tab_analiz, tab_loglar = st.tabs([
    UI_TXT[lang]["tab_home"], 
    UI_TXT[lang]["tab_analysis"], 
    UI_TXT[lang]["tab_logs"]
])

# ----------------- TAB 1: ANA SAYFA -----------------
with tab_intro:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<h3 class='agent-header'>{UI_TXT[lang]['purpose']}</h3>", unsafe_allow_html=True)
        st.markdown(UI_TXT[lang]["purpose_desc"])
    with col2:
        st.markdown(f"<h3 class='agent-header'>{UI_TXT[lang]['how_it_works']}</h3>", unsafe_allow_html=True)
        st.markdown(UI_TXT[lang]["how_it_works_desc"])

# ----------------- TAB 2: ANALİZ VE GÖRSELLEŞTİRME -----------------
with tab_analiz:
    st.markdown(f"<h2 class='agent-header'>{UI_TXT[lang]['agent_title']}</h2>", unsafe_allow_html=True)
    st.write("")
    
    # Ajan Kontrol Paneli Rehberi (Kılavuz)
    st.markdown(f"""
    <div class='premium-card' style='border-left: 5px solid #8B0000; background-color: #FFF9F9; padding: 1rem; margin-bottom: 1.5rem;'>
        <h4 style='margin: 0 0 5px 0; color: #8B0000; font-family: "Playfair Display", serif;'>⚡ {UI_TXT[lang]['control_center']}</h4>
        <p style='margin: 0; font-size: 0.92rem; color: #333333;'>
            {UI_TXT[lang]['control_desc']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # İlk açılışta varsayılan örnek videoyu otomatik yükle
    if not st.session_state.default_loaded and st.session_state.video_id == DEFAULT_VIDEO_ID and st.session_state.video_metadata is None:
        with st.spinner("Örnek video künyesi yükleniyor..." if lang == "tr" else "Loading sample video metadata..."):
            meta = video_kunyesi_uret(DEFAULT_VIDEO_ID)
            st.session_state.video_metadata = meta
            st.session_state.video_id = DEFAULT_VIDEO_ID
            st.session_state.default_loaded = True

    # İki Sütunlu Grid Layout
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown(f"### {UI_TXT[lang]['target_video']}")
        
        youtube_url = st.text_input(
            UI_TXT[lang]["video_input_label"], 
            value=f"https://www.youtube.com/watch?v={st.session_state.video_id}" if len(st.session_state.video_id) == 11 else st.session_state.video_id,
            placeholder="Örn: https://www.youtube.com/watch?v=HK6y8DAPN_0"
        )
        
        btn_get_meta = st.button(UI_TXT[lang]["btn_meta"], use_container_width=True)
        
        if (youtube_url and btn_get_meta) or btn_get_meta:
            if youtube_url:
                video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
                video_id = video_id_match.group(1) if video_id_match else youtube_url.strip()
                
                with st.spinner(UI_TXT[lang]["fetching_meta"]):
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
            st.markdown(f"👤 {UI_TXT[lang]['channel']}: `{meta['uploader']}`")
            st.markdown(f"👀 {UI_TXT[lang]['views']}: `{meta['views']}` | 👍 {UI_TXT[lang]['likes']}: `{meta.get('likes', 'Bilinmiyor' if lang == 'tr' else 'Unknown')}`")
            st.markdown(f"💬 {UI_TXT[lang]['total_comments']}: `{meta.get('comment_count', 'Bilinmiyor' if lang == 'tr' else 'Unknown')}`")
            st.markdown("</div>", unsafe_allow_html=True)
            
    with col_right:
        st.markdown(f"### {UI_TXT[lang]['model_settings']}")
        
        selected_api_info = None
        btn_disabled = True
        
        keys_missing = False
        for cfg in models_config_list:
            if not cfg["api_key"] or cfg["api_key"].startswith("your_") or len(cfg["api_key"].strip()) <= 10:
                keys_missing = True
                break
        
        if keys_missing:
            st.error(UI_TXT[lang]["key_missing_err"])
        else:
            st.success(UI_TXT[lang]["consensus_active"])
            models_summary = "\n".join([f"- Model {idx+1} ({cfg['provider'].upper()}): `{cfg['model']}`" for idx, cfg in enumerate(models_config_list)])
            st.info(f"{UI_TXT[lang]['selected_models']}\n{models_summary}")
            selected_api_info = {
                "models_config": models_config_list,
                "consensus_mode": True
            }
            btn_disabled = False
                    
        st.markdown("---")
        st.markdown(f"**{UI_TXT[lang]['sampling_options']}**")
        download_mode = st.radio("İndirme Modu:", [UI_TXT[lang]["download_all"], UI_TXT[lang]["download_custom"]], label_visibility="collapsed")
        custom_count = st.number_input(UI_TXT[lang]["comment_count_label"], min_value=5, max_value=500, value=30, disabled=(download_mode == UI_TXT[lang]["download_all"]))
        
        st.markdown("---")
        st.markdown("""
        <style>
        div.stButton > button[kind="primary"] {
            background-color: #8B0000 !important;
            color: #FFFFFF !important;
            border: 2px solid #8B0000 !important;
            box-shadow: 0 4px 15px rgba(139, 0, 0, 0.4) !important;
            font-size: 1.1rem !important;
            height: 3rem !important;
            width: 100% !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #111111 !important;
            border-color: #111111 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button(UI_TXT[lang]["btn_analyze"], type="primary", use_container_width=True, disabled=btn_disabled):
            with st.spinner(UI_TXT[lang]["fetching_comments"]):
                limit = 500
                raw_comments = download_live_comments(st.session_state.video_id, limit)
                
                if raw_comments:
                    if not download_mode.startswith("Tüm Yorumlar" if lang == "tr" else "All Comments") and len(raw_comments) > custom_count:
                        selected_comments = random.sample(raw_comments, custom_count)
                        for idx, c in enumerate(selected_comments):
                            c["id"] = idx + 1
                    else:
                        selected_comments = raw_comments
                        
                    st.session_state.comments_data = selected_comments
                    st.session_state.comment_index = 0
                    
                    try:
                        progress_bar = st.progress(0.0, text="Yapay zekâ yorumları analiz ediyor..." if lang == "tr" else "AI is analyzing comments...")
                        def update_progress(val):
                            progress_bar.progress(val, text=f"Yapay zekâ yorumları analiz ediyor... %{int(val*100)}" if lang == "tr" else f"AI is analyzing comments... {int(val*100)}%")
                            
                        if selected_api_info:
                            selected_api_info["progress_callback"] = update_progress
                            
                        analysis = agent.video_analiz_et(
                            selected_comments, 
                            meta=st.session_state.video_metadata, 
                            api_info=selected_api_info,
                            lang=lang
                        )
                        progress_bar.empty()
                        st.session_state.analysis_result = analysis
                        st.success(UI_TXT[lang]["success_analysis"].format(count=len(selected_comments)))
                    except Exception as err:
                        st.error("❌ Yapay Zekâ Analiz Hatası:" if lang == "tr" else "❌ AI Analysis Error:")
                        st.code(str(err), language="text")
                        st.info("💡 Not: API hatası aldınız. API anahtarınızın veya seçtiğiniz model isminin doğruluğundan emin olun." if lang == "tr" else "💡 Note: You received an API error. Check the validity of your API key or model name.")
                else:
                    st.error(UI_TXT[lang]["fetching_comments_err"])
                    
    # Analiz Sonuçları Var ise Göster
    if st.session_state.analysis_result and st.session_state.comments_data:
        analysis = st.session_state.analysis_result
        comments = st.session_state.comments_data
        
        st.markdown("---")
        model_name = analysis.get("model_info", "Kural Tabanlı Analiz (Çevrimdışı)" if lang == "tr" else "Rule-Based Analysis (Offline)")
        st.info(f"**{UI_TXT[lang]['used_model']}** {model_name}")
        
        # Mutabakat Raporu Akademik Güvenilirlik Kartı
        if analysis.get("consensus_stats"):
            c_stats = analysis["consensus_stats"]
            llm_results = analysis.get("llm_results", [])
            total_comments = len(comments)
            
            tam_mutabakat_count = sum(1 for r in llm_results if r.get("consensus_details", {}).get("agreement_level") in ["Tam Mutabakat", "Full Consensus"])
            cogunluk_count = sum(1 for r in llm_results if r.get("consensus_details", {}).get("agreement_level") in ["Çoğunluk Kararı", "Majority Decision"])
            uyusmazlik_count = sum(1 for r in llm_results if r.get("consensus_details", {}).get("agreement_level") in ["Uyuşmazlık", "Disagreement"])
            
            tam_pct = round((tam_mutabakat_count / total_comments) * 100, 1) if total_comments > 0 else 0.0
            cogunluk_pct = round((cogunluk_count / total_comments) * 100, 1) if total_comments > 0 else 0.0
            uyusmazlik_pct = round((uyusmazlik_count / total_comments) * 100, 1) if total_comments > 0 else 0.0

            st.markdown(f"""
            <div class='premium-card' style='border-left: 5px solid #1A365D; background-color: #F0F4F8; padding: 1.5rem; margin-bottom: 1.5rem;'>
                <h3 style='margin: 0 0 10px 0; color: #1A365D; font-family: "Playfair Display", serif;'>{UI_TXT[lang]['reliability_index']}</h3>
                <p style='margin: 0 0 15px 0; font-size: 0.95rem; color: #333333;'>
                    {UI_TXT[lang]['reliability_desc']}
                </p>
                <div style='margin-bottom: 20px; font-size: 0.95rem; color: #111; background: white; padding: 12px; border: 1px solid #D5CDB5;'>
                    <b>{UI_TXT[lang]['distribution_summary'].format(count=total_comments)}</b><br/>
                    - 🟢 <b>{UI_TXT[lang]['full_consensus']}:</b> {tam_mutabakat_count} {UI_TXT[lang]['full_consensus_desc'].format(pct=tam_pct)}<br/>
                    - 🔵 <b>{UI_TXT[lang]['majority_decision']}:</b> {cogunluk_count} {UI_TXT[lang]['majority_decision_desc'].format(pct=cogunluk_pct)}<br/>
                    - 🔴 <b>{UI_TXT[lang]['disagreement']}:</b> {uyusmazlik_count} {UI_TXT[lang]['disagreement_desc'].format(pct=uyusmazlik_pct)}
                </div>
                <div style='display: flex; gap: 20px; flex-wrap: wrap;'>
                    <div style='flex: 1; min-width: 180px; background: white; padding: 10px; border: 1px solid #D5CDB5;'>
                        <span style='font-size:0.85rem; color:#666;'>{UI_TXT[lang]['overall_consensus']}</span><br/>
                        <span style='font-size:1.8rem; font-weight:bold; color:#1A365D;'>%{c_stats['consensus_rate']}</span>
                    </div>
                    <div style='flex: 1; min-width: 180px; background: white; padding: 10px; border: 1px solid #D5CDB5;'>
                        <span style='font-size:0.85rem; color:#666;'>{UI_TXT[lang]['sentiment_kappa']}</span><br/>
                        <span style='font-size:1.4rem; font-weight:bold; color:#2B6CB0;'>{c_stats['fleiss_kappa_sentiment']}</span><br/>
                        <span style='font-size:0.75rem; color:#555;'>{c_stats['fleiss_kappa_sentiment_text']}</span>
                    </div>
                    <div style='flex: 1; min-width: 180px; background: white; padding: 10px; border: 1px solid #D5CDB5;'>
                        <span style='font-size:0.85rem; color:#666;'>{UI_TXT[lang]['category_kappa']}</span><br/>
                        <span style='font-size:1.4rem; font-weight:bold; color:#2B6CB0;'>{c_stats['fleiss_kappa_category']}</span><br/>
                        <span style='font-size:0.75rem; color:#555;'>{c_stats['fleiss_kappa_category_text']}</span>
                    </div>
                    <div style='flex: 1; min-width: 180px; background: white; padding: 10px; border: 1px solid #D5CDB5;'>
                        <span style='font-size:0.85rem; color:#666;'>{UI_TXT[lang]['role_kappa']}</span><br/>
                        <span style='font-size:1.4rem; font-weight:bold; color:#2B6CB0;'>{c_stats['fleiss_kappa_role']}</span><br/>
                        <span style='font-size:0.75rem; color:#555;'>{c_stats['fleiss_kappa_role_text']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"### {UI_TXT[lang]['detected_community']} <span style='color:#8B0000;'>{analysis['topluluk_turu_str']}</span>", unsafe_allow_html=True)
        
        editorial_colors = ["#8B0000", "#111111", "#444444", "#777777", "#A5A5A5", "#D5CDB5", "#EBEBEB"]
        
        if analysis.get("consensus_stats"):
            col_g1, col_g2, col_g3 = st.columns(3)
        else:
            col_g1, col_g2 = st.columns(2)
            col_g3 = None
            
        with col_g1:
            st.markdown(f"#### {UI_TXT[lang]['sentiment_climate']}")
            duygu_df = pd.DataFrame(list(analysis["duygu"].items()), columns=["Category", "Frequency"] if lang == "en" else ["Kategori", "Sıklık"])
            fig_d = px.pie(duygu_df, values="Frequency" if lang == "en" else "Sıklık", names="Category" if lang == "en" else "Kategori", title=UI_TXT[lang]["sentiment_dist"], color_discrete_sequence=editorial_colors)
            st.plotly_chart(fig_d, use_container_width=True)
        with col_g2:
            st.markdown(f"#### {UI_TXT[lang]['role_dist']}")
            rol_df = pd.DataFrame(list(analysis["rol"].items()), columns=["Role", "Frequency"] if lang == "en" else ["Rol", "Sıklık"])
            fig_r = px.bar(rol_df, x="Role" if lang == "en" else "Rol", y="Frequency" if lang == "en" else "Sıklık", title=UI_TXT[lang]["role_dist"], color="Role" if lang == "en" else "Rol", color_discrete_sequence=editorial_colors)
            st.plotly_chart(fig_r, use_container_width=True)
        
        if col_g3:
            with col_g3:
                st.markdown(f"#### {UI_TXT[lang]['model_consensus']}")
                llm_results = analysis.get("llm_results", [])
                levels = [r.get("consensus_details", {}).get("agreement_level", "Bilinmeyen" if lang == "tr" else "Unknown") for r in llm_results]
                from collections import Counter
                level_counts = Counter(levels)
                mutabakat_df = pd.DataFrame(list(level_counts.items()), columns=["Consensus Level" if lang == "en" else "Mutabakat Seviyesi", "Frequency" if lang == "en" else "Sıklık"])
                mutabakat_colors = ["#2E7D32", "#1A365D", "#8B0000"]
                fig_m = px.pie(mutabakat_df, values="Frequency" if lang == "en" else "Sıklık", names="Consensus Level" if lang == "en" else "Mutabakat Seviyesi", title=UI_TXT[lang]["consensus_dist"], color_discrete_sequence=mutabakat_colors)
                st.plotly_chart(fig_m, use_container_width=True)
            
        st.markdown("---")
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown(analysis["rapor"], unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # PDF Rapor İndirme Butonu
        try:
            from pdf_generator import generate_analysis_pdf
            pdf_data = generate_analysis_pdf(st.session_state.video_metadata, analysis, comments)
            st.download_button(
                label=UI_TXT[lang]["download_pdf"],
                data=pdf_data,
                file_name=f"izleyici_iklimi_analiz_raporu_{st.session_state.video_id}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as pdf_err:
            st.warning(f"PDF Raporu oluşturulamadı: {pdf_err}" if lang == "tr" else f"Could not create PDF report: {pdf_err}")
        
        # TEKİL YORUM GEZİNTİ PANELİ
        st.markdown("---")
        st.markdown(f"{UI_TXT[lang]['individual_analysis']}")
        st.caption(UI_TXT[lang]["individual_desc"])
        
        total_len = len(comments)
        current_idx = st.session_state.comment_index
        
        if current_idx >= total_len:
            current_idx = 0
            st.session_state.comment_index = 0
            
        c_item = comments[current_idx]
        c_id = c_item.get("id")
        
        llm_results = analysis.get("llm_results")
        c_llm = None
        if llm_results:
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
        st.write(f"**{UI_TXT[lang]['comment_num'].format(index=current_idx + 1, total=total_len)}**")
        
        lang_info = ""
        orig_lang = c_llm.get("original_lang", "").lower() if c_llm else ""
        target_lang = "tr" if lang == "tr" else "en"
        
        translation_block = ""
        if orig_lang and orig_lang != target_lang:
            trans_comment = c_llm.get("translated_comment", "")
            if trans_comment and trans_comment != c_item['comment']:
                translation_block = f"""
                <div style='margin-top:8px; padding:8px 12px; background-color:#F0F4F8; border-left:3px solid #2B6CB0; font-size:0.95rem;'>
                    <b>🌐 {UI_TXT[lang]['translation']} ({target_lang.upper()}):</b><br/>
                    <i>{trans_comment}</i>
                </div>
                """
            lang_info = f" | 🌐 {UI_TXT[lang]['original_lang']}: `{orig_lang.upper()}`"

        st.markdown(
            f"<div class='comment-bubble'>"
            f"<b>{c_item['username']}</b> ({c_item.get('likes', 0)} {UI_TXT[lang]['raw_likes'].lower()}{lang_info})<br/>"
            f"<p style='margin-top:6px; color:#111111; font-size:1.1rem; font-family:\"Playfair Display\", serif;'>{c_item['comment']}</p>"
            f"{translation_block}"
            f"</div>", 
            unsafe_allow_html=True
        )
        
        col_nav_res1, col_nav_res2 = st.columns(2)
        with col_nav_res1:
            st.markdown(f"**{UI_TXT[lang]['category_col']}** `{c_duygu}`")
        with col_nav_res2:
            st.markdown(f"**{UI_TXT[lang]['role_col']}** `{c_rol}`")
            
        if c_llm:
            st.markdown("---")
            if "consensus_details" in c_llm:
                votes = c_llm["consensus_details"]["votes"]
                agree_lvl = c_llm["consensus_details"]["agreement_level"]
                lbl_color = "#8B0000" if agree_lvl in ["Uyuşmazlık", "Disagreement"] else ("#2B6CB0" if agree_lvl in ["Çoğunluk Kararı", "Majority Decision"] else "#2E7D32")
                
                st.markdown(f"**{UI_TXT[lang]['consensus_level_col']}** <span style='color:{lbl_color}; font-weight:bold;'>{agree_lvl} (Confidence: {c_llm['confidence']})</span>", unsafe_allow_html=True)
                
                vote_table = []
                for field in ["sentiment", "category", "role"]:
                    row = {"Analiz Alanı" if lang == "tr" else "Analysis Area": field.capitalize()}
                    for model_name, val in votes[field].items():
                        short_model = model_name.split("/")[-1] if "/" in model_name else model_name
                        row[short_model] = val
                    vote_table.append(row)
                
                st.dataframe(pd.DataFrame(vote_table).set_index("Analiz Alanı" if lang == "tr" else "Analysis Area"), use_container_width=True)
            else:
                st.markdown(f"**{UI_TXT[lang]['analysis_details_col']}**")
                st.markdown(f"> *{c_reasoning}*")
            if c_devices:
                st.markdown(f"**{UI_TXT[lang]['detected_rhetoric']}** `{'`, `'.join(c_devices)}`")
            
        st.markdown(f"<div style='margin-top:10px; padding:12px; border-left:3px solid #8B0000; background:#FFF5F5;'>", unsafe_allow_html=True)
        st.markdown(f"**{UI_TXT[lang]['special_advice']}**<br/>{c_tavsiye}", unsafe_allow_html=True)
        st.markdown(f"</div>", unsafe_allow_html=True)
        st.markdown(f"</div>", unsafe_allow_html=True)
        
        # Gezinti Butonları
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button(UI_TXT[lang]["btn_prev"], use_container_width=True):
            st.session_state.comment_index = (st.session_state.comment_index - 1) % total_len
            st.rerun()
        if col_btn2.button(UI_TXT[lang]["btn_next"], use_container_width=True):
            st.session_state.comment_index = (st.session_state.comment_index + 1) % total_len
            st.rerun()
            
        # Ham Veri İnceleme
        with st.expander(UI_TXT[lang]["raw_matrix"]):
            detailed_table = []
            for item in comments:
                single_girdi = [item]
                c_llm = next((r for r in llm_results if r.get("original_id") == item["id"]), None) if llm_results else None
                
                if c_llm:
                    single_duygu = c_llm.get("sentiment")
                    single_cat = c_llm.get("category")
                    single_rol = c_llm.get("role")
                    agree_lvl = c_llm.get("consensus_details", {}).get("agreement_level", "Tek LLM" if lang == "tr" else "Single LLM")
                    conf = c_llm.get("confidence", 1.0)
                    orig_l = c_llm.get("original_lang", "tr")
                    trans_c = c_llm.get("translated_comment", "")
                else:
                    single_duygu = list(duygu_ve_kaygi_analizi(single_girdi, analysis["topluluk_turu"]).keys())[0]
                    single_cat = "Karma / Genel" if lang == "tr" else "Mixed / General"
                    single_rol = list(dijital_rol_dedektoru(single_girdi, analysis["topluluk_turu"]).keys())[0]
                    agree_lvl = "Kural Tabanlı" if lang == "tr" else "Rule-Based"
                    conf = 1.0
                    orig_l = "tr"
                    trans_c = ""
                    
                detailed_table.append({
                    UI_TXT[lang]["raw_user"]: item["username"],
                    UI_TXT[lang]["raw_comment"]: item["comment"],
                    UI_TXT[lang]["original_lang"]: orig_l.upper(),
                    UI_TXT[lang]["translation"]: trans_c,
                    UI_TXT[lang]["raw_sentiment"]: single_duygu,
                    UI_TXT[lang]["raw_category"]: single_cat,
                    UI_TXT[lang]["raw_role"]: single_rol,
                    UI_TXT[lang]["raw_consensus"]: agree_lvl,
                    UI_TXT[lang]["raw_confidence"]: conf,
                    UI_TXT[lang]["raw_likes"]: item.get("likes", 0)
                })
            st.dataframe(pd.DataFrame(detailed_table), use_container_width=True)

# ----------------- TAB 3: BELLEK VE LOG KAYITLARI -----------------
with tab_loglar:
    st.markdown(UI_TXT[lang]["logs_title"])
    st.caption(UI_TXT[lang]["logs_desc"])
    
    log_df = pd.DataFrame(agent.get_logs())
    st.dataframe(log_df, use_container_width=True)
