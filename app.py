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
from database_manager import (
    init_database,
    save_analysis,
    get_all_analyses,
    get_analysis,
    delete_analysis,
    get_meta_analysis_dataframe,
    export_combined_corpus
)

db_status = init_database()

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
        "thesis_context": "Akademik Araştırma ve Tez Bağlamı",
        "thesis_desc": "Bu çalışma, çevrimiçi gayriresmi izleyici topluluklarındaki (YouTube) siber-kültürel iklimi, dilsel jargonları, kolektif duygulanımı (Sara Ahmed) ve Kozinets'in netnografik rollerini inceleyen hesaplamalı bir dijital antropoloji araştırma platformudur.",
        "ethical_boundary": "Gözetim ve Etik Sınır",
        "ethical_desc": "<b>Uyarı:</b> Ajan çıktıları kesin yargılar barındırmaz. Nitel araştırmalarda araştırmacının özdüşünümselliği (reflexivity) ve insan gözetimi esastır.",
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
        "main_subtitle": "Sanal Topluluklarda Büyük Dil Modelleri Destekli Hesaplamalı Netnografi ve Siber-Antropoloji Platformu",
        "tab_home": "🏠 Araştırma Bağlamı",
        "tab_analysis": "🔴 📊 ETNOGRAFİK SAHA ANALİZİ 👈",
        "tab_fieldnotes": "📓 Araştırmacı Saha Defteri",
        "tab_logs": "🪵 Ajan Günlüğü & Özdüşünümsellik",
        "purpose": "🎯 Araştırmanın Amacı ve Kuramsal Kapsamı",
        "purpose_desc": "Bu araştırma platformu, video paylaşım platformlarındaki asenkron informal etkileşimleri siber-kültürel ve antropolojik bir mercekten inceler. Sistemimiz; Kozinets'in netnografik tipolojisini, Sara Ahmed'in duygulanım teorisini ve Clifford Geertz'in 'yoğun betimleme' ilkesini hesaplamalı büyük dil modelleri ile birleştirerek şu analizleri sunar:\n\n- **Kolektif Duygulanım & İklim:** İzleyicilerin teknolojik prekarite, mesleki kaygı ve keşif coşkusu dağılımını haritalar.\n- **Kozinets Netnografik Rolleri:** Topluluk üyelerini İçeridekiler (Akran Mentörleri), Tutkulular (Üreticiler), Sosyalleşenler ve Turistler olarak sınıflandırır.\n- **Siber-Retorik Çözümleme:** İroni, kinaye ve sarkastik övgü gibi örtük söylemleri çözerek alt-metinleri aydınlatır.",
        "how_it_works": "💡 Saha Çalışması Metodolojisi",
        "how_it_works_desc": "1. **Dijital Saha Seçimi:** Hedef YouTube video bağlantısını girin veya arşivlenmiş hazır etnografik veri setini seçin.\n2. **Kriptografik Etik Arıtma:** Sistem, yorumları indirirken kullanıcı adlarını SHA-256 ile anında hash'ler ve @mentions ifadelerini maskeler.\n3. **Çoklu LLM Mutabakatı:** 3 farklı yapay zekâ modeli paralel çalışarak Fleiss' Kappa güvenilirlik indeksiyle etnografik kodlama üretir.\n4. **Saha Notu ve Dışa Aktarma:** Yorumlar arasında gezinirken araştırmacı saha defterine nitel notlar alabilir, tüm matrisi MAXQDA / Excel uyumlu indirebilirsiniz.",
        "agent_title": "🤖 Hesaplamalı Netnografi ve Siber-Kültür Araştırma Ajanı",
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
        "logs_title": "### 🪵 Ajan İşlem Günlüğü (Özdüşünümsellik / Bellek Kayıtları)",
        "logs_desc": "Dijital etnografik saha günlüğü; ajanın aldığı analitik ve metodolojik kararların özdüşünümsel (reflexive) kayıt defteridir.",
        "original_lang": "Orijinal Dil",
        "translation": "Çeviri",
        "silent_majority_title": "👻 Sessiz Çoğunluk & Görünmez İzleyici Analizi (Lurkers & 90-9-1 Kuralı)",
        "silent_majority_desc": "Jakob Nielsen'in (2006) Katılım Eşitsizliği ve Nonnecke & Preece'in (2000) Çevrimiçi Sessiz Kitle (Lurker) Etnografisi kuramları uyarınca izlenme, beğeni ve yorum oranlarının modellenmesi.",
        "cvr_label": "Yorum/İzlenme Oranı (CVR)",
        "lvr_label": "Beğeni/İzlenme Oranı (LVR)",
        "lurker_ratio_label": "Sessiz İzleyici (Lurker) Oranı",
        "vitality_typology_label": "Topluluk Canlılık Tipolojisi",
        "nielsen_distribution": "Nielsen 90-9-1 Katılım Eşitsizliği Modeli",
        "or_pool_title": "OpenRouter Model Havuzu Filtresi:",
        "or_pool_all": "Tümü (Önce Ücretsizler, Sonra En Ucuzdan Pahalıya)",
        "or_pool_free": "Yalnızca Ücretsiz Modeller ([FREE])",
        "or_pool_paid": "Yalnızca Ücretli Modeller (En Ucuzdan Başlayarak)",
        "tab_meta": "📚 Meta-Analiz & Saha Arşivi",
        "meta_title": "📚 Çok-Sahalı Karşılaştırmalı Etnografi ve Saha Arşivi",
        "meta_desc": "Farklı dijital sahalarda (YouTube video topluluklarında) yürütülen etnografik araştırmaların saklandığı, karşılaştırmalı meta-analizlerin yapıldığı ve geçmiş çalışmaların tek tıkla oturuma geri yüklenebildiği araştırma havuzu.",
        "meta_stat_total": "İncelenen Saha (Video)",
        "meta_stat_comments": "Analiz Edilen Yorum",
        "meta_stat_avg_cvr": "Ort. CVR (Katılım)",
        "meta_stat_avg_lurker": "Ort. Sessiz Kitle (Lurker)",
        "meta_community_dist": "Topluluk Türü Dağılımı",
        "meta_lurker_comparison": "Sahalar Arası Katılım ve Sessiz Kitle (Lurker) Karşılaştırması",
        "meta_consensus_comparison": "Sahalar Arası Çoklu LLM Mutabakat Güvenilirliği (Fleiss' Kappa)",
        "meta_saved_fields": "📁 Kayıtlı Etnografik Sahalar",
        "meta_btn_load": "📥 Sahayı Oturuma Yükle",
        "meta_btn_delete": "🗑️ Sahayı Arşivden Sil",
        "meta_btn_export_all": "📦 Tüm Sahaları Birleşik Excel (.xlsx) Olarak İndir (Meta + Tüm Yorumlar)",
        "meta_empty_state": "Henüz kayıtlı bir saha bulunmuyor. 'Etnografik Saha Analizi' sekmesinden bir videoyu analiz ettiğinizde otomatik olarak buraya arşivlenecektir.",
        "meta_field_loaded": "✅ '{title}' başlıklı saha çalışması başarıyla aktif oturuma yüklendi!",
        "meta_field_deleted": "🗑️ Saha çalışması arşivden silindi.",
        "firebase_card_title": "🔥 Kalıcı Bulut Veri Tabanı (Firebase Firestore)",
        "firebase_connected_msg": "Firebase Firestore bağlantısı aktif. Tüm saha çalışmaları bulutta kalıcı olarak saklanmaktadır.",
        "firebase_local_msg": "Şu anda Yerel JSON Arşiv modu devrede (`data/fieldwork_archive.json`). Firebase Firestore'a bağlanmak için `firebase_credentials.json` dosyasını proje kök dizinine ekleyebilirsiniz."
    },
    "en": {
        "page_title": "Audience Climate Mirror",
        "sidebar_expander": "ℹ️ Agent Definition & Academic Context",
        "agent_id": "Agent Identity",
        "agent_role": "Agent Role",
        "system_instruction": "System Instruction",
        "thesis_context": "Academic Research & Thesis Context",
        "thesis_desc": "This study is a computational digital anthropology research platform investigating cyber-cultural climates, linguistic jargons, collective affect (Sara Ahmed), and Kozinets' netnographic roles in online video audience communities (YouTube).",
        "ethical_boundary": "Oversight & Ethical Boundaries",
        "ethical_desc": "<b>Warning:</b> Automated outputs do not constitute absolute truths. In qualitative research, researcher reflexivity and critical human oversight are paramount.",
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
        "main_subtitle": "Multi-LLM Computational Netnography & Cyber-Anthropology Platform for Virtual Communities",
        "tab_home": "🏠 Research Context",
        "tab_analysis": "🔴 📊 ETHNOGRAPHIC FIELDWORK 👈",
        "tab_fieldnotes": "📓 Field Notes & Reflexivity",
        "tab_logs": "🪵 Agent Reflexivity Log",
        "purpose": "🎯 Research Purpose and Theoretical Scope",
        "purpose_desc": "This research platform examines asynchronous informal interactions on video-sharing platforms through a cyber-cultural and anthropological lens. By combining Kozinets' netnographic typology, Sara Ahmed's affect theory, and Clifford Geertz's 'thick description' with computational Large Language Models, it delivers:\n\n- **Collective Affect & Climate:** Maps distributions of technological precarity, occupational anxiety, and euphoria.\n- **Kozinets Netnographic Roles:** Classifies members into Insiders (Peer Mentors), Devotees (Creators), Minglers (Socializers), and Tourists (Lurkers).\n- **Cyber-Rhetorical Decoding:** Resolves implicit discourse such as irony, innuendo, and sarcastic praise to illuminate subtexts.",
        "how_it_works": "💡 Fieldwork Methodology",
        "how_it_works_desc": "1. **Digital Field Selection:** Enter target YouTube link or select preloaded archived ethnographic datasets.\n2. **Cryptographic Ethical Anonymization:** Hashes usernames via SHA-256 and scrubs @mentions upon fetching.\n3. **Multi-LLM Consensus:** 3 distinct models run concurrently to provide Fleiss' Kappa inter-coder reliability.\n4. **Field Notes & Export:** Take ethnographic notes in real-time and export full coding matrices to MAXQDA / Excel (.xlsx).",
        "agent_title": "🤖 Computational Netnography & Cyber-Culture Research Agent",
        "control_center": "⚡ Agent Control Center",
        "control_panel": "## 🎛️ Digital Ethnographic Research & Data Collection Console",
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
        "logs_desc": "Digital ethnographic field log; a reflexive record of analytical and algorithmic decisions made by the agent.",
        "original_lang": "Original Language",
        "translation": "Translation",
        "silent_majority_title": "👻 Silent Majority & Invisible Audience Analysis (Lurkers & 90-9-1 Rule)",
        "silent_majority_desc": "Audience participation vitality modeled on view, like, and comment ratios framed by Jakob Nielsen's (2006) Participation Inequality and Nonnecke & Preece's (2000) Lurker Ethnography.",
        "cvr_label": "Comment-to-View Ratio (CVR)",
        "lvr_label": "Like-to-View Ratio (LVR)",
        "lurker_ratio_label": "Silent Audience (Lurker) Ratio",
        "vitality_typology_label": "Community Vitality Typology",
        "nielsen_distribution": "Nielsen 90-9-1 Participation Inequality Model",
        "or_pool_title": "OpenRouter Model Pool Filter:",
        "or_pool_all": "All (Free First, Then Cheapest to Most Expensive)",
        "or_pool_free": "Free Models Only ([FREE])",
        "or_pool_paid": "Paid Models Only (Price Sorted - Cheapest First)",
        "tab_meta": "📚 Meta-Analysis & Field Archive",
        "meta_title": "📚 Cross-Field Comparative Ethnography & Field Archive",
        "meta_desc": "Research repository where digital ethnographic studies conducted across various YouTube communities are archived, cross-field comparative meta-analyses are visualized, and past fieldwork can be loaded back into active sessions.",
        "meta_stat_total": "Examined Fields (Videos)",
        "meta_stat_comments": "Analyzed Comments",
        "meta_stat_avg_cvr": "Mean CVR (Participation)",
        "meta_stat_avg_lurker": "Mean Silent Audience (Lurker)",
        "meta_community_dist": "Community Type Distribution",
        "meta_lurker_comparison": "Cross-Field Engagement & Silent Majority (Lurker) Comparison",
        "meta_consensus_comparison": "Cross-Field Multi-LLM Inter-Coder Reliability (Fleiss' Kappa)",
        "meta_saved_fields": "📁 Archived Ethnographic Fields",
        "meta_btn_load": "📥 Load Field Into Session",
        "meta_btn_delete": "🗑️ Delete From Archive",
        "meta_btn_export_all": "📦 Download Combined Corpus Excel (.xlsx) (Meta + All Coded Comments)",
        "meta_empty_state": "No archived fields found yet. When you run an analysis in the 'Ethnographic Fieldwork' tab, it will be automatically archived here.",
        "meta_field_loaded": "✅ Fieldwork '{title}' successfully loaded into active session!",
        "meta_field_deleted": "🗑️ Fieldwork deleted from archive.",
        "firebase_card_title": "🔥 Persistent Cloud Database (Firebase Firestore)",
        "firebase_connected_msg": "Firebase Firestore is active. All fieldwork data is permanently stored in the cloud.",
        "firebase_local_msg": "Currently operating in Local JSON Archive mode (`data/fieldwork_archive.json`). To connect to Firebase Firestore, place `firebase_credentials.json` in the project root."
    }
}

def format_model_options(models, provider):
    formatted = []
    for m in models:
        # Eğer zaten bir ön ek etiketi varsa ([FREE], [$X.XX/1M], [PRO]), olduğu gibi koru
        if m.startswith("["):
            formatted.append(m)
            continue

        if provider == "gemini":
            if "flash" in m.lower():
                formatted.append(f"[FREE] {m}")
            else:
                formatted.append(f"[PRO] {m}")
        elif provider == "groq":
            formatted.append(f"[FREE] {m}")
        elif provider == "openrouter":
            if m.endswith(":free"):
                formatted.append(f"[FREE] {m}")
            else:
                formatted.append(f"[PRO] {m}")
        else:
            formatted.append(m)
    return formatted

def parse_selected_model(option):
    if not option:
        return ""
    # [FREE], [$0.14/1M], [PRO] vb. tüm etiketleri temizleyip ham model kodunu döner
    return re.sub(r"^\[.*?\]\s*", "", option).strip()

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
if "openrouter_models_detailed" not in st.session_state:
    st.session_state.openrouter_models_detailed = None

from api_client import get_available_gemini_models, get_available_groq_models, get_available_openrouter_models

if gemini_key and not gemini_key.startswith("your_") and len(gemini_key.strip()) > 10 and not st.session_state.gemini_models:
    st.session_state.gemini_models = get_available_gemini_models(gemini_key)
if groq_key and not groq_key.startswith("your_") and len(groq_key.strip()) > 10 and not st.session_state.groq_models:
    st.session_state.groq_models = get_available_groq_models(groq_key)
if or_key and not or_key.startswith("your_") and len(or_key.strip()) > 10 and not st.session_state.openrouter_models_detailed:
    st.session_state.openrouter_models_detailed = get_available_openrouter_models(or_key, detailed=True)
    if st.session_state.openrouter_models_detailed:
        st.session_state.openrouter_models = st.session_state.openrouter_models_detailed.get("all", [])

gemini_fallback = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
groq_fallback = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768", "llama-3.1-8b-instant"]

or_fallback_free = [
    "[FREE] meta-llama/llama-3.3-70b-instruct:free",
    "[FREE] qwen/qwen3-coder:free",
    "[FREE] google/gemma-4-31b-it:free",
    "[FREE] meta-llama/llama-3.2-3b-instruct:free"
]
or_fallback_paid = [
    "[$0.14/1M] deepseek/deepseek-chat",
    "[$0.15/1M] google/gemini-2.0-flash-001",
    "[$0.15/1M] openai/gpt-4o-mini",
    "[$0.40/1M] meta-llama/llama-3.3-70b-instruct",
    "[$2.50/1M] openai/gpt-4o"
]
or_fallback_all = or_fallback_free + or_fallback_paid

# OpenRouter Model Havuzu Filtresi
st.sidebar.markdown(f"**{UI_TXT[lang]['or_pool_title']}**")
or_filter_choice = st.sidebar.selectbox(
    "Filtrele:" if lang == "tr" else "Filter:",
    [
        UI_TXT[lang]["or_pool_all"],
        UI_TXT[lang]["or_pool_free"],
        UI_TXT[lang]["or_pool_paid"]
    ],
    index=0,
    key="or_pool_filter_choice"
)

if st.session_state.openrouter_models_detailed:
    if or_filter_choice == UI_TXT[lang]["or_pool_free"]:
        or_list = st.session_state.openrouter_models_detailed.get("free", [])
    elif or_filter_choice == UI_TXT[lang]["or_pool_paid"]:
        or_list = st.session_state.openrouter_models_detailed.get("paid", [])
    else:
        or_list = st.session_state.openrouter_models_detailed.get("all", [])
else:
    if or_filter_choice == UI_TXT[lang]["or_pool_free"]:
        or_list = or_fallback_free
    elif or_filter_choice == UI_TXT[lang]["or_pool_paid"]:
        or_list = or_fallback_paid
    else:
        or_list = or_fallback_all

gemini_list = st.session_state.gemini_models if st.session_state.gemini_models else gemini_fallback
groq_list = st.session_state.groq_models if st.session_state.groq_models else groq_fallback

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

if db_status.get("firestore_connected"):
    st.sidebar.markdown(f"- **Veri Tabanı:** 🟢 `Firebase Firestore`" if lang == "tr" else f"- **Database:** 🟢 `Firebase Firestore`")
else:
    st.sidebar.markdown(f"- **Veri Tabanı:** 🟠 `Yerel JSON Arşivi`" if lang == "tr" else f"- **Database:** 🟠 `Local JSON Archive`")

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
tab_intro, tab_analiz, tab_sahanotu, tab_meta, tab_loglar = st.tabs([
    UI_TXT[lang]["tab_home"], 
    UI_TXT[lang]["tab_analysis"], 
    UI_TXT[lang]["tab_fieldnotes"],
    UI_TXT[lang]["tab_meta"],
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
        
        data_source_mode = st.radio(
            "Saha Veri Kaynağı:" if lang == "tr" else "Field Data Source:",
            ["Canlı YouTube Sahası (URL ile Çek)" if lang == "tr" else "Live YouTube Field (Fetch via URL)",
             "Arşivlenmiş Etnografik Saha Verisi (data/ornek_yorumlar.json)" if lang == "tr" else "Archived Ethnographic Field Dataset (data/ornek_yorumlar.json)"],
            index=0
        )
        
        if data_source_mode.startswith("Arşiv" if lang == "tr" else "Archived"):
            if st.button("📂 Arşivlenmiş Saha Verisini Yükle (15 Yorum)" if lang == "tr" else "📂 Load Archived Fieldwork Data (15 Comments)", use_container_width=True):
                try:
                    with open("data/ornek_yorumlar.json", "r", encoding="utf-8") as f:
                        sample_comments = json.load(f)
                    st.session_state.comments_data = sample_comments
                    st.session_state.video_metadata = {
                        "title": "Yapay Zeka Ajanları ve Otomasyonun Geleceği [Arşiv Saha Çalışması]",
                        "uploader": "Teknoloji & Siber-Kültür Laboratuvarı",
                        "views": "142,500",
                        "likes": "4,820",
                        "comment_count": "15 (Nitel Etnografik Örneklem)",
                        "upload_date": "15.01.2026",
                        "thumbnail": "https://img.youtube.com/vi/L_a3s0ObozI/maxresdefault.jpg",
                        "url": "https://www.youtube.com/watch?v=L_a3s0ObozI"
                    }
                    st.session_state.video_id = "L_a3s0ObozI"
                    st.session_state.analysis_result = None
                    st.session_state.comment_index = 0
                    st.session_state.is_sample_mode = True
                    st.success("Örnek etnografik veri yüklendi! Sağ panelden analizi başlatabilirsiniz." if lang == "tr" else "Sample ethnographic dataset loaded! Start analysis from the right panel.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Veri yüklenemedi: {e}")
        else:
            st.session_state.is_sample_mode = False
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
            
            # Hızlı Sessiz Çoğunluk Özeti (Lurkers & Vitality)
            from tools import analiz_et_sessiz_cogunluk
            quick_sc = analiz_et_sessiz_cogunluk(meta.get("views"), meta.get("likes"), meta.get("comment_count"), lang=lang)
            if quick_sc["views"] > 0:
                st.markdown(f"""
                <div style='margin-top: 10px; padding: 10px 12px; background: #FAF9F6; border-left: 3px solid {quick_sc["badge_color"]}; font-size: 0.85rem;'>
                    <b>👻 {UI_TXT[lang]['vitality_typology_label']}:</b> <span style='color:{quick_sc["badge_color"]}; font-weight: bold;'>{quick_sc["tipoloji_baslik"]}</span><br/>
                    <span style='color: #555;'>CVR (Yorum/İzlenme): <b>%{quick_sc["cvr"]:.3f}</b> | Lurker (Sessiz Kitle): <b>%{quick_sc["lurker_ratio"]:.1f}</b></span>
                </div>
                """, unsafe_allow_html=True)
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
                if st.session_state.get("is_sample_mode") and st.session_state.comments_data:
                    raw_comments = st.session_state.comments_data
                else:
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
                        
                        # Otomatik Veritabanı / Arşiv Kaydı (Firebase Firestore & Yerel JSON)
                        try:
                            save_res = save_analysis(
                                st.session_state.video_id,
                                st.session_state.video_metadata,
                                analysis,
                                selected_comments
                            )
                            if save_res.get("success"):
                                storage_label = "Firebase Firestore" if save_res.get("storage") == "firestore" else ("Yerel JSON Arşivi" if lang == "tr" else "Local JSON Archive")
                                st.toast(f"💾 Saha çalışması {storage_label} sistemine arşivlendi!" if lang == "tr" else f"💾 Fieldwork archived to {storage_label}!", icon="📚")
                        except Exception as s_err:
                            pass
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

        # Sessiz Çoğunluk & Katılım Eşitsizliği (Lurkers & 90-9-1) Kartı
        sc = analysis.get("sessiz_cogunluk")
        if not sc and st.session_state.video_metadata:
            from tools import analiz_et_sessiz_cogunluk
            sc = analiz_et_sessiz_cogunluk(
                st.session_state.video_metadata.get("views"), 
                st.session_state.video_metadata.get("likes"), 
                st.session_state.video_metadata.get("comment_count", len(comments)), 
                lang=lang
            )

        if sc and sc.get("views", 0) > 0:
            st.markdown(f"""
            <div class='premium-card' style='border-left: 5px solid {sc["badge_color"]}; background-color: #FAF9F6; padding: 1.5rem; margin-bottom: 1.5rem;'>
                <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
                    <h3 style='margin: 0; color: #111111; font-family: "Playfair Display", serif;'>{UI_TXT[lang]['silent_majority_title']}</h3>
                    <span style='background: {sc["badge_color"]}; color: white; padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 0.85rem;'>{sc["tipoloji_baslik"]}</span>
                </div>
                <p style='margin: 8px 0 15px 0; font-size: 0.9rem; color: #555555;'>
                    {UI_TXT[lang]['silent_majority_desc']}
                </p>
                <div style='display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 15px;'>
                    <div style='flex: 1; min-width: 140px; background: white; padding: 12px; border: 1px solid #D5CDB5;'>
                        <span style='font-size:0.8rem; color:#666;'>👀 {UI_TXT[lang]['views']}</span><br/>
                        <span style='font-size:1.5rem; font-weight:bold; color:#111111;'>{sc["views"]:,}</span>
                    </div>
                    <div style='flex: 1; min-width: 140px; background: white; padding: 12px; border: 1px solid #D5CDB5;'>
                        <span style='font-size:0.8rem; color:#666;'>💬 {UI_TXT[lang]['cvr_label']}</span><br/>
                        <span style='font-size:1.5rem; font-weight:bold; color:#2B6CB0;'>%{sc["cvr"]:.3f}</span><br/>
                        <span style='font-size:0.75rem; color:#777;'>({sc["comments"]:,} / {sc["views"]:,})</span>
                    </div>
                    <div style='flex: 1; min-width: 140px; background: white; padding: 12px; border: 1px solid #D5CDB5;'>
                        <span style='font-size:0.8rem; color:#666;'>👍 {UI_TXT[lang]['lvr_label']}</span><br/>
                        <span style='font-size:1.5rem; font-weight:bold; color:#2E7D32;'>%{sc["lvr"]:.3f}</span><br/>
                        <span style='font-size:0.75rem; color:#777;'>({sc["likes"]:,} / {sc["views"]:,})</span>
                    </div>
                    <div style='flex: 1; min-width: 140px; background: white; padding: 12px; border: 1px solid #D5CDB5;'>
                        <span style='font-size:0.8rem; color:#666;'>🤫 {UI_TXT[lang]['lurker_ratio_label']}</span><br/>
                        <span style='font-size:1.5rem; font-weight:bold; color:#8B0000;'>%{sc["lurker_ratio"]:.2f}</span><br/>
                        <span style='font-size:0.75rem; color:#777;'>Görünmez Kitle</span>
                    </div>
                </div>
                <div style='background: white; padding: 12px 16px; border: 1px solid #D5CDB5; margin-bottom: 12px;'>
                    <b style='font-size: 0.9rem;'>📊 {UI_TXT[lang]['nielsen_distribution']} (Jakob Nielsen, 2006):</b><br/>
                    <div style='display: flex; height: 16px; width: 100%; border-radius: 3px; overflow: hidden; margin: 8px 0;'>
                        <div style='background: #8B0000; width: {max(sc["nielsen"]["lurkers_pct"], 1.0)}%;' title='Sessiz İzleyiciler (Lurkers): %{sc["nielsen"]["lurkers_pct"]}'></div>
                        <div style='background: #2E7D32; width: {max(sc["nielsen"]["intermittent_pct"], 1.0)}%;' title='Hafif Katılımcılar (Beğenenler): %{sc["nielsen"]["intermittent_pct"]}'></div>
                        <div style='background: #2B6CB0; width: {max(sc["nielsen"]["creators_pct"], 1.0)}%;' title='Aktif Yorumcular: %{sc["nielsen"]["creators_pct"]}'></div>
                    </div>
                    <div style='display: flex; justify-content: space-between; font-size: 0.8rem; color: #444;'>
                        <span>🤫 <b>Sessiz İzleyici (Lurker):</b> %{sc["nielsen"]["lurkers_pct"]}</span>
                        <span>👍 <b>Hafif Katılımcı:</b> %{sc["nielsen"]["intermittent_pct"]}</span>
                        <span>💬 <b>Aktif Üretici/Yorumcu:</b> %{sc["nielsen"]["creators_pct"]}</span>
                    </div>
                </div>
                <div style='font-size: 0.9rem; color: #222; line-height: 1.5; padding: 10px 14px; background: white; border-left: 3px solid #666;'>
                    <b>🔍 Etnografik & Antropolojik Okuma:</b> {sc["aciklama"]}
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
            
            df_export = pd.DataFrame(detailed_table)
            st.dataframe(df_export, use_container_width=True)
            
            # Excel & CSV Export Butonları
            import io
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                df_export.to_excel(writer, sheet_name="Etnografik_Kodlama", index=False)
            
            col_exp1, col_exp2 = st.columns(2)
            col_exp1.download_button(
                label="📊 MAXQDA / Excel Kodlama Matrisini İndir (.xlsx)" if lang == "tr" else "📊 Download MAXQDA / Excel Matrix (.xlsx)",
                data=excel_buffer.getvalue(),
                file_name=f"etnografi_matrisi_{st.session_state.video_id}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            col_exp2.download_button(
                label="📄 CSV Kodlama Matrisini İndir (.csv)" if lang == "tr" else "📄 Download CSV Matrix (.csv)",
                data=df_export.to_csv(index=False).encode('utf-8-sig'),
                file_name=f"etnografi_matrisi_{st.session_state.video_id}.csv",
                mime="text/csv",
                use_container_width=True
            )

# ----------------- TAB 3: ARAŞTIRMACI SAHA DEFTERİ (FIELD NOTES) -----------------
with tab_sahanotu:
    st.markdown("### 📓 Etnografik Saha Defteri ve Araştırmacı Özdüşünümselliği (Reflexivity)")
    st.caption(
        "Kozinets (2015) ve Christine Hine'a (2015) göre dijital etnografide araştırmacının sahaya dair kişisel "
        "gözlemleri, metodolojik şüpheleri ve sezgileri en az algoritmik veri kadar değerlidir." if lang == "tr" else
        "According to Kozinets (2015) and Christine Hine (2015), the ethnographer's personal reflections, methodological "
        "doubts, and insights are just as essential as the computational data."
    )
    
    if "field_notes" not in st.session_state:
        st.session_state.field_notes = ""
        
    saved_note = st.text_area(
        "Saha Gözlem ve Özdüşünümsellik Notlarınız:" if lang == "tr" else "Fieldwork & Reflexivity Notes:",
        value=st.session_state.field_notes,
        height=240,
        placeholder="Örn: Bu dijital sahada izleyicilerin teknolojik gelecek kaygısını mizah ve ironi ile maskelemeye çalıştıklarını gözlemledim..." if lang == "tr" else "E.g., In this digital field, I observed participants masking technological precarity with humor and irony..."
    )
    col_fn1, col_fn2 = st.columns(2)
    if col_fn1.button("💾 Saha Notunu Kaydet" if lang == "tr" else "💾 Save Field Note", use_container_width=True):
        st.session_state.field_notes = saved_note
        st.success("Saha notunuz oturuma kaydedildi!" if lang == "tr" else "Field note saved to session!")
    
    if st.session_state.field_notes:
        col_fn2.download_button(
            "📥 Saha Notlarını İndir (.txt)" if lang == "tr" else "📥 Download Field Notes (.txt)",
            data=st.session_state.field_notes,
            file_name=f"etnografik_saha_notlari_{st.session_state.video_id}.txt",
            mime="text/plain",
            use_container_width=True
        )

# ----------------- TAB 4: META-ANALİZ & SAHA ARŞİVİ -----------------
with tab_meta:
    st.markdown(f"<h2 class='agent-header'>{UI_TXT[lang]['meta_title']}</h2>", unsafe_allow_html=True)
    st.caption(UI_TXT[lang]["meta_desc"])
    
    # Verileri Çek
    all_saved = get_all_analyses()
    meta_df = get_meta_analysis_dataframe()
    
    if meta_df.empty:
        st.info(f"ℹ️ {UI_TXT[lang]['meta_empty_state']}")
    else:
        # 1. Üst Metrik Kartları
        m_c1, m_c2, m_c3, m_c4 = st.columns(4)
        m_c1.metric(UI_TXT[lang]["meta_stat_total"], len(meta_df))
        total_comments_num = int(meta_df['orneklem_sayisi'].sum()) if 'orneklem_sayisi' in meta_df.columns else 0
        m_c2.metric(UI_TXT[lang]["meta_stat_comments"], f"{total_comments_num:,}")
        avg_cvr = meta_df['cvr'].mean() if 'cvr' in meta_df.columns else 0.0
        avg_lurker = meta_df['lurker_orani'].mean() if 'lurker_orani' in meta_df.columns else 0.0
        m_c3.metric(UI_TXT[lang]["meta_stat_avg_cvr"], f"%{avg_cvr:.3f}")
        m_c4.metric(UI_TXT[lang]["meta_stat_avg_lurker"], f"%{avg_lurker:.1f}")
        
        st.write("")
        
        # 2. Sahalar Arası Karşılaştırmalı Görselleştirmeler
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown(f"#### 🌐 {UI_TXT[lang]['meta_community_dist']}")
            topluluk_sayilari = meta_df['topluluk_turu'].value_counts().reset_index()
            topluluk_sayilari.columns = ['Topluluk Türü', 'Saha Sayısı']
            fig_topluluk = px.pie(
                topluluk_sayilari, 
                names='Topluluk Türü', 
                values='Saha Sayısı',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_topluluk.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_topluluk, use_container_width=True)
            
        with col_g2:
            st.markdown(f"#### 👻 {UI_TXT[lang]['meta_lurker_comparison']}")
            plot_df = meta_df.copy()
            plot_df['kisa_baslik'] = plot_df['baslik'].apply(lambda x: (str(x)[:28] + '...') if len(str(x)) > 30 else str(x))
            fig_lurker = px.bar(
                plot_df,
                x='kisa_baslik',
                y=['cvr', 'lurker_orani'],
                barmode='group',
                labels={'kisa_baslik': 'Saha (Video)', 'value': 'Oran (%)', 'variable': 'Metrik'},
                color_discrete_map={'cvr': '#8B0000', 'lurker_orani': '#4A5568'}
            )
            fig_lurker.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_lurker, use_container_width=True)
            
        # Fleiss' Kappa Karşılaştırması
        if 'kappa_sentiment' in meta_df.columns:
            st.markdown(f"#### 🎓 {UI_TXT[lang]['meta_consensus_comparison']}")
            fig_kappa = px.bar(
                plot_df,
                x='kisa_baslik',
                y=['kappa_sentiment', 'kappa_category', 'kappa_role'],
                barmode='group',
                labels={'kisa_baslik': 'Saha (Video)', 'value': "Fleiss' Kappa (κ)", 'variable': 'Kodlama Alanı'},
                color_discrete_sequence=['#1A365D', '#2B6CB0', '#4299E1']
            )
            fig_kappa.add_hline(y=0.61, line_dash="dash", line_color="green", annotation_text="Önemli Düzeyde Uyum (κ >= 0.61)")
            fig_kappa.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_kappa, use_container_width=True)
            
        st.divider()
        
        # 3. Arşiv Tablosu ve Oturuma Yükleme
        st.markdown(f"### {UI_TXT[lang]['meta_saved_fields']}")
        
        display_df = meta_df[['video_id', 'baslik', 'kanal', 'topluluk_turu', 'orneklem_sayisi', 'cvr', 'lurker_orani', 'tarih']].copy()
        display_df.columns = [
            'Video ID', 
            'Video Başlığı' if lang == 'tr' else 'Title',
            'Kanal' if lang == 'tr' else 'Channel',
            'Topluluk Türü' if lang == 'tr' else 'Community Type',
            'Yorum Sayısı' if lang == 'tr' else 'Sample N',
            'CVR (%)',
            'Lurker (%)',
            'Analiz Tarihi' if lang == 'tr' else 'Date'
        ]
        st.dataframe(display_df, use_container_width=True)
        
        # Saha Seçici & Aksiyonlar
        col_act1, col_act2, col_act3 = st.columns([2, 1, 1])
        selected_vid = col_act1.selectbox(
            "İncelemek veya Oturuma Yüklemek İçin Saha Seçin:" if lang == "tr" else "Select Field to Inspect or Load:",
            options=[s.get("video_id") for s in all_saved],
            format_func=lambda vid: f"{vid} - {next((s.get('title', vid) for s in all_saved if s.get('video_id') == vid), vid)[:50]}",
            key="meta_field_select_box"
        )
        
        if col_act2.button(UI_TXT[lang]["meta_btn_load"], use_container_width=True, key="btn_load_meta_field"):
            loaded_field = get_analysis(selected_vid)
            if loaded_field:
                st.session_state.video_id = loaded_field.get("video_id", DEFAULT_VIDEO_ID)
                st.session_state.video_metadata = {
                    "title": loaded_field.get("title", "Arşiv Saha"),
                    "uploader": loaded_field.get("uploader", "Arşiv Kanal"),
                    "views": str(loaded_field.get("views", "0")),
                    "likes": str(loaded_field.get("likes", "0")),
                    "comment_count": str(loaded_field.get("comment_count", "0")),
                    "upload_date": loaded_field.get("upload_date", ""),
                    "thumbnail": loaded_field.get("thumbnail", f"https://img.youtube.com/vi/{st.session_state.video_id}/maxresdefault.jpg"),
                    "url": loaded_field.get("url", f"https://www.youtube.com/watch?v={st.session_state.video_id}")
                }
                st.session_state.analysis_result = {
                    "topluluk_turu": loaded_field.get("topluluk_turu", "genel"),
                    "topluluk_turu_str": loaded_field.get("topluluk_turu_str", "Genel Topluluk"),
                    "model_info": loaded_field.get("model_info", "Kural Tabanlı"),
                    "duygu": loaded_field.get("duygu", {}),
                    "rol": loaded_field.get("rol", {}),
                    "consensus_stats": loaded_field.get("consensus_stats", {}),
                    "sessiz_cogunluk": loaded_field.get("sessiz_cogunluk", {}),
                    "rapor": loaded_field.get("rapor", ""),
                    "llm_results": loaded_field.get("llm_results", [])
                }
                st.session_state.comments_data = loaded_field.get("comments", [])
                st.session_state.comment_index = 0
                st.session_state.is_sample_mode = False
                st.success(UI_TXT[lang]["meta_field_loaded"].format(title=st.session_state.video_metadata.get('title', selected_vid)))
                st.rerun()
                
        if col_act3.button(UI_TXT[lang]["meta_btn_delete"], use_container_width=True, key="btn_del_meta_field"):
            if delete_analysis(selected_vid):
                st.warning(UI_TXT[lang]["meta_field_deleted"])
                st.rerun()
                
        st.write("")
        # 4. Birleşik Külliyat / Korpus Dışa Aktarımı (.xlsx)
        combined_xlsx = export_combined_corpus()
        st.download_button(
            label=UI_TXT[lang]["meta_btn_export_all"],
            data=combined_xlsx,
            file_name="kolektif_dijital_etnografi_korpusu.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="btn_download_corpus_xlsx"
        )

    # Firebase Bilgilendirme ve Kurulum Kartı
    with st.expander(UI_TXT[lang]["firebase_card_title"], expanded=False):
        if db_status.get("firestore_connected"):
            st.success(f"🟢 {UI_TXT[lang]['firebase_connected_msg']}")
        else:
            st.warning(f"🟠 {UI_TXT[lang]['firebase_local_msg']}")
            st.markdown("""
            **Firebase Firestore 3 Adımda Nasıl Bağlanır?**
            1. [Firebase Console](https://console.firebase.google.com/) -> Proje Oluşturun -> **Firestore Database** etkinleştirin (Test/Production mod).
            2. **Project Settings** -> **Service Accounts** sekmesine gidin -> **Generate new private key** butonuna basarak JSON dosyasını indirin.
            3. Bu dosyayı proje kök dizinine `firebase_credentials.json` adıyla yapıştırın (veya Streamlit Secrets'a `FIREBASE_CREDENTIALS` olarak içeriğini yapıştırın).
            
            *Sistem dosyayı otomatik algılar ve yerel arşivdeki verileri Firestore'a senkronize eder.*
            """ if lang == "tr" else """
            **How to Connect Firebase Firestore in 3 Steps:**
            1. Go to [Firebase Console](https://console.firebase.google.com/) -> Create Project -> Enable **Firestore Database**.
            2. Navigate to **Project Settings** -> **Service Accounts** -> Click **Generate new private key** and download the JSON.
            3. Save this file as `firebase_credentials.json` in the root folder (or add its contents to Streamlit Secrets as `FIREBASE_CREDENTIALS`).
            
            *The platform automatically detects the file and syncs data to Firestore.*
            """)

# ----------------- TAB 5: BELLEK VE LOG KAYITLARI -----------------
with tab_loglar:
    st.markdown(UI_TXT[lang]["logs_title"])
    st.caption(UI_TXT[lang]["logs_desc"])
    
    log_df = pd.DataFrame(agent.get_logs())
    st.dataframe(log_df, use_container_width=True)
