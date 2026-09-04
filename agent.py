import os
from tools import (
    duygu_ve_kaygi_analizi, 
    dijital_rol_dedektoru, 
    izleyici_raporu_olusturucu, 
    topluluk_turu_tespit_et, 
    analiz_et_sessiz_cogunluk,
    COMMUNITY_LEXICONS
)

class IklimAynasiAgent:
    def __init__(self):
        # Dijital Etnografi & Siber-Antropoloji Ajanı Kimliği
        self.role = "Dijital Etnografi ve Siber-Kültür Araştırma Ajanı (Audience Netnography Copilot)"
        self.system_instructions = (
            "Sen, çevrimiçi video platformlarındaki (YouTube vb.) asenkron dijital toplulukların dilini, "
            "siber-jargonlarını, kolektif duygulanım iklimlerini (Sara Ahmed), teknolojik kaygılarını ve "
            "Kozinets'in netnografik rollerini (İçeridekiler, Tutkulular, Sosyalleşenler, Turistler) çözümleyen "
            "bir Dijital Etnografi ve Siber-Antropoloji Araştırma Ajanısın."
        )
        # Etnografik Saha Günlüğü ve Özdüşünümsellik Kayıtları (Reflexivity Log)
        self.logs = []
        self.log_action("Saha Başlatıldı", "Ajan başarıyla başlatıldı. Dijital Etnografi ve Netnografi konsepti yüklendi.")

    def log_action(self, islem, detay):
        """Ajanın aldığı etnografik kararları ve işlem günlüğünü loglar."""
        self.logs.append({
            "islem": islem,
            "detay": detay
        })

    def video_analiz_et(self, yorumlar, meta=None, api_info=None, lang="tr"):
        """
        [ETNOGRAFİK SAHA ANALİZİ AKIŞI] Belirtilen dijital saha (video yorum havuzu) için
        nitel ve hesaplamalı çözümleme yapar, Kozinets rollerini ve kolektif duygulanımı haritalar.
        """
        self.log_action("Saha Çalışması Başladı" if lang == "tr" else "Fieldwork Started", f"Yorum havuzu analiz ediliyor. Gözlem sayısı: {len(yorumlar)}" if lang == "tr" else f"Analyzing comment pool. Observations count: {len(yorumlar)}")
        
        # Karar Akışı: Veri boşsa doğrudan durdur
        if not yorumlar:
            self.log_action("Hata" if lang == "tr" else "Error", "Gelen veri kümesi boş." if lang == "tr" else "Incoming dataset is empty.")
            return None
            
        # Künye ve API Bilgilerini kontrol et / doldur
        if not meta:
            meta = {"title": "Bilinmeyen Video" if lang == "tr" else "Unknown Video", "uploader": "Bilinmeyen Kanal" if lang == "tr" else "Unknown Channel", "views": "Bilinmiyor" if lang == "tr" else "Unknown"}

        # Araç 4'ün Tetiklenmesi: Sessiz Çoğunluk & Katılım Eşitsizliği (90-9-1) Analizi
        self.log_action("Sessiz Çoğunluk Analizi" if lang == "tr" else "Silent Majority Analysis", "İzlenme, beğeni ve yorum oranları üzerinden katılım eşitsizliği modelleniyor..." if lang == "tr" else "Modeling participation inequality based on views, likes and comments...")
        sessiz_cogunluk = analiz_et_sessiz_cogunluk(
            meta.get("views"), 
            meta.get("likes"), 
            meta.get("comment_count", len(yorumlar)), 
            lang=lang
        )

        # Siber-Topluluk Türünün Otomatik Tespiti
        self.log_action("Saha Tipolojisi Tespiti" if lang == "tr" else "Field Typology Detection", "Yorum kelimelerine göre topluluk türü analiz ediliyor..." if lang == "tr" else "Analyzing community type based on comment words...")
        topluluk_turu = topluluk_turu_tespit_et(yorumlar)
        lex_info = COMMUNITY_LEXICONS.get(topluluk_turu, {})
        turu_str = lex_info.get("label_tr" if lang == "tr" else "label_en", "Genel Çevrimiçi Topluluk" if lang == "tr" else "General Online Community")
        
        self.log_action("Saha Türü Saptandı" if lang == "tr" else "Field Type Detected", f"Saptanan topluluk kültürü: {turu_str}")
        
        # Araç 1'in Tetiklenmesi (Duygu ve Kaygı Analizi)
        self.log_action("Araç Tetikleme" if lang == "tr" else "Tool Triggering", f"duygu_ve_kaygi_analizi() çağrılıyor. (Tür: {topluluk_turu})" if lang == "tr" else f"Calling duygu_ve_kaygi_analizi(). (Type: {topluluk_turu})")
        duygu_sonuclari = duygu_ve_kaygi_analizi(yorumlar, topluluk_turu)
        
        # Araç 2'nin Tetiklenmesi (Topluluk Rol Dedektörü)
        self.log_action("Araç Tetikleme" if lang == "tr" else "Tool Triggering", f"dijital_rol_dedektoru() çağrılıyor. (Tür: {topluluk_turu})" if lang == "tr" else f"Calling dijital_rol_dedektoru(). (Type: {topluluk_turu})")
        rol_sonuclari = dijital_rol_dedektoru(yorumlar, topluluk_turu)
        
        # Künye ve API Bilgilerini kontrol et / doldur
        if not meta:
            meta = {"title": "Bilinmeyen Video" if lang == "tr" else "Unknown Video", "uploader": "Bilinmeyen Kanal" if lang == "tr" else "Unknown Channel", "views": "Bilinmiyor" if lang == "tr" else "Unknown"}
            
        if not api_info:
            from api_client import test_api_connection
            groq_key = os.getenv("GROQ_API_KEY")
            or_key = os.getenv("OPENROUTER_API_KEY")
            gemini_key = os.getenv("GEMINI_API_KEY")
            
            active_p = None
            active_k = None
            
            if groq_key and not groq_key.startswith("your_") and len(groq_key.strip()) > 10:
                active_p, active_k = "groq", groq_key
            elif or_key and not or_key.startswith("your_") and len(or_key.strip()) > 10:
                active_p, active_k = "openrouter", or_key
            elif gemini_key and not gemini_key.startswith("your_") and len(gemini_key.strip()) > 10:
                active_p, active_k = "gemini", gemini_key
                
            if active_p and active_k:
                self.log_action("API Algılandı" if lang == "tr" else "API Detected", f"Aktif servis: {active_p}. Model test ediliyor..." if lang == "tr" else f"Active service: {active_p}. Testing model...")
                success, resolved_model, msg = test_api_connection(active_p, active_k)
                if success:
                    api_info = {
                        "provider": active_p,
                        "api_key": active_k,
                        "model": resolved_model
                    }
                    self.log_action("API Test Başarılı" if lang == "tr" else "API Test Success", f"Saptanan model: {resolved_model}")
                else:
                    self.log_action("API Test Hatası" if lang == "tr" else "API Test Error", f"{msg}. Çevrimdışı modda devam ediliyor." if lang == "tr" else f"{msg}. Proceeding in offline mode.")
        
        # Raporlama Aşaması
        akademik_rapor = None
        model_info = "Kural Tabanlı Analiz (Çevrimdışı Fallback)" if lang == "tr" else "Rule-Based Analysis (Offline Fallback)"
        llm_analysis_results = None
        
        if api_info and (api_info.get("api_key") or (api_info.get("consensus_mode") and api_info.get("models_config"))):
            from api_client import get_llm_report, analyze_comments_with_llm, analyze_comments_with_llm_consensus
            
            try:
                progress_cb = None
                if "progress_callback" in api_info:
                    progress_cb = api_info["progress_callback"]
 
                consensus_stats = None
 
                if api_info.get("consensus_mode") and api_info.get("models_config"):
                    models_config = api_info["models_config"]
                    models_names = [cfg["model"] for cfg in models_config]
                    self.log_action("Nitel Raporlama (Mutabakat Modu)" if lang == "tr" else "Qualitative Reporting (Consensus Mode)", f"Paralel modeller çağrılıyor: {', '.join(models_names)}" if lang == "tr" else f"Calling parallel models: {', '.join(models_names)}")
                    llm_analysis_results, consensus_stats = analyze_comments_with_llm_consensus(
                        yorumlar, models_config, progress_cb, lang=lang
                    )
                    model_info = f"Çoklu LLM Mutabakat Modu ({', '.join(models_names)})" if lang == "tr" else f"Multi-LLM Consensus Mode ({', '.join(models_names)})"
                else:
                    self.log_action("Nitel Raporlama" if lang == "tr" else "Qualitative Reporting", f"{api_info['provider']} ({api_info['model']}) üzerinden detaylı analiz başlıyor..." if lang == "tr" else f"Detailed analysis starting via {api_info['provider']} ({api_info['model']})...")
                    llm_analysis_results = analyze_comments_with_llm(
                        yorumlar, api_info["provider"], api_info["api_key"], api_info["model"], progress_cb, lang=lang
                    )
                    model_info = f"{api_info['provider'].upper()} API ({api_info['model']})"
 
                # LLM sonuçlarına göre istatistikleri derle (Hem TR hem EN kategorileri destekler)
                total = len(yorumlar)
                kaygi_kats = ["Mesleki Gelecek Kaygisi", "Felsefi/Varolussal Sorgulama", "Etik ve Telif Hassasiyeti",
                              "Professional Future Anxiety", "Philosophical/Existential Inquiries", "Ethic and Copyright Sensitivity"]
                cosku_kats = ["Heyecan ve Kesif Motivasyonu", "Yaratici Is Akisi Tartismasi",
                              "Excitement and Discovery Motivation", "Creative Workflow Discussion"]
                hata_kats = ["Teknik Sorun ve Destek Arayisi", "Maliyet ve Erisilebilirlik Sorunu",
                             "Technical Issue and Support Seeking", "Cost and Accessibility Issue"]
                etik_kats = ["Etik ve Telif Hassasiyeti", "Felsefi/Varolussal Sorgulama",
                             "Ethic and Copyright Sensitivity", "Philosophical/Existential Inquiries"]
                destek_kats = ["Sosyal Destek ve Tesekkur", "Social Support and Gratitude"]

                kaygi_sayisi = sum(1 for r in llm_analysis_results if r.get("category") in kaygi_kats)
                mentor_sayisi = sum(1 for r in llm_analysis_results if any(m in r.get("role", "") for m in ["Akran Mentoru", "Peer Mentor", "Icerideki", "Insider"]))
                cosku_sayisi = sum(1 for r in llm_analysis_results if r.get("category") in cosku_kats)
                hata_sayisi = sum(1 for r in llm_analysis_results if r.get("category") in hata_kats)
                etik_sayisi = sum(1 for r in llm_analysis_results if r.get("category") in etik_kats)
                destek_sayisi = sum(1 for r in llm_analysis_results if r.get("category") in destek_kats)
 
                stats = {
                    "total": total,
                    "kaygi": (kaygi_sayisi / total) * 100 if total > 0 else 0,
                    "mentor": (mentor_sayisi / total) * 100 if total > 0 else 0,
                    "cosku": (cosku_sayisi / total) * 100 if total > 0 else 0,
                    "hata": (hata_sayisi / total) * 100 if total > 0 else 0,
                    "etik": (etik_sayisi / total) * 100 if total > 0 else 0,
                    "destek": (destek_sayisi / total) * 100 if total > 0 else 0,
                    "sessiz_cogunluk": sessiz_cogunluk
                }
                
                saglik_skoru = ((mentor_sayisi + destek_sayisi) / total) * 100 if total > 0 else 0
                if saglik_skoru >= 30:
                    stats["indeks"] = "🟢 Yüksek Sosyal Sermaye (A Sınıfı)" if lang == "tr" else "🟢 High Social Capital (Class A)"
                elif saglik_skoru >= 15:
                    stats["indeks"] = "🟡 Orta Sosyal Sermaye (B Sınıfı)" if lang == "tr" else "🟡 Medium Social Capital (Class B)"
                else:
                    stats["indeks"] = "🔴 Düşük Sosyal Sermaye (C Sınıfı)" if lang == "tr" else "🔴 Low Social Capital (Class C)"
                
                # 2. Sentez Raporunu Oluştur
                self.log_action("Sentez Raporlama" if lang == "tr" else "Synthesis Reporting", "Analiz sonuçları birleştirilip rapor yazılıyor..." if lang == "tr" else "Synthesizing results and writing report...")
                
                # Rapor üretirken mutabakat modunda birincil modeli kullanalım
                if api_info.get("consensus_mode"):
                    primary_model = api_info["models_config"][0]["model"]
                    report_provider = api_info["models_config"][0]["provider"]
                    report_key = api_info["models_config"][0]["api_key"]
                else:
                    primary_model = api_info["model"]
                    report_provider = api_info["provider"]
                    report_key = api_info["api_key"]
                
                akademik_rapor = get_llm_report(
                    meta, stats, yorumlar, report_provider, report_key, primary_model, llm_analysis_results, lang=lang
                )
                if not akademik_rapor:
                    raise Exception("Model boş rapor döndürdü." if lang == "tr" else "Model returned an empty report.")
                
                # LLM analizini geriye dönük arayüzle uyumlu hale getirmek için duygu/rol dict'lerini güncelle
                duygu_sonuclari = {}
                rol_sonuclari = {}
                for r in llm_analysis_results:
                    cat = r.get("category", "Genel Gozlem" if lang == "tr" else "General Observation")
                    duygu_sonuclari[cat] = duygu_sonuclari.get(cat, 0) + 1
                    rol = r.get("role", "Pasif Destekci" if lang == "tr" else "Passive Supporter")
                    rol_sonuclari[rol] = rol_sonuclari.get(rol, 0) + 1
                    
            except Exception as e:
                self.log_action("LLM Analiz/Raporlama Uyarısı" if lang == "tr" else "LLM Analysis Warning", f"{str(e)} - Çevrimdışı moda geçiliyor.")
                akademik_rapor = izleyici_raporu_olusturucu(duygu_sonuclari, rol_sonuclari, topluluk_turu, sessiz_cogunluk=sessiz_cogunluk)
                model_info = "Kural Tabanlı Analiz (Çevrimdışı Fallback)" if lang == "tr" else "Rule-Based Analysis (Offline Fallback)"
                consensus_stats = None
        else:
            # Fallback: Kural Tabanlı Rapor Oluşturucu (Çevrimdışı Mod)
            self.log_action("Araç Tetikleme" if lang == "tr" else "Tool Triggering", "izleyici_raporu_olusturucu() çağrılıyor (Çevrimdışı Mod)..." if lang == "tr" else "Calling izleyici_raporu_olusturucu() (Offline Mode)...")
            akademik_rapor = izleyici_raporu_olusturucu(duygu_sonuclari, rol_sonuclari, topluluk_turu, sessiz_cogunluk=sessiz_cogunluk)
            model_info = "Kural Tabanlı Analiz (Çevrimdışı Fallback)" if lang == "tr" else "Rule-Based Analysis (Offline Fallback)"
            consensus_stats = None
            
        self.log_action("Analiz Tamamlandı" if lang == "tr" else "Analysis Completed", "Tüm analizler ve rapor başarıyla birleştirildi." if lang == "tr" else "All analyses and report successfully merged.")
        
        return {
            "topluluk_turu": topluluk_turu,
            "topluluk_turu_str": turu_str,
            "duygu": duygu_sonuclari,
            "rol": rol_sonuclari,
            "rapor": akademik_rapor,
            "model_info": model_info,
            "llm_results": llm_analysis_results,
            "consensus_stats": consensus_stats,
            "sessiz_cogunluk": sessiz_cogunluk
        }

        
    def get_logs(self):
        """İşlem günlüğünü dışarıya aktarır."""
        return self.logs

