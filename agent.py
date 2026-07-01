import os
from tools import duygu_ve_kaygi_analizi, dijital_rol_dedektoru, izleyici_raporu_olusturucu, topluluk_turu_tespit_et

class IklimAynasiAgent:
    def __init__(self):
        # Yönerge 3. Madde: Rol / Sistem Talimatı Zorunluluğu
        self.role = "Çevrimiçi İzleyici Toplulukları İklim ve Jargon Çözümleyici Karar Destek Ajanı"
        self.system_instructions = (
            "Sen, çevrimiçi/gayriresmi eğitim videolarının altındaki yorumlarda izleyicilerin kullandığı "
            "örtük dili, jargonları, gelecek kaygılarını, heyecanlarını ve topluluk içi rollerini inceleyerek "
            "eğitim tasarımcılarına ve içerik üreticilerine izleyici iklimini raporlayan bir karar destek ajanısın."
        )
        # Yönerge 3. Madde: Bellek / Kayıt Zorunluluğu (İşlem Günlüğü Logları)
        self.logs = []
        self.log_action("Başlatma", "Ajan başarıyla başlatıldı. İzleyici İklimi Aynası konsepti yüklendi.")

    def log_action(self, islem, detay):
        """Ajanın yaptığı tüm kararları ve işlem geçmişini loglar."""
        self.logs.append({
            "islem": islem,
            "detay": detay
        })

    def video_analiz_et(self, yorumlar, meta=None, api_info=None):
        """
        [KARAR AKIŞI] Tek bir video için yorumları analiz eder, 
        uygun araçları tetikler ve sonuçları birleştirir.
        Gelişmiş LLM API'si (Gemini/Groq/OpenRouter) mevcutsa nitel 
        pedagojik raporu LLM ile yazar, yoksa kural tabanlı template kullanır.
        """
        self.log_action("Analiz Başladı", f"Yorumların analizi tetiklendi. Yorum sayısı: {len(yorumlar)}")
        
        # Karar Akışı: Veri boşsa doğrudan durdur
        if not yorumlar:
            self.log_action("Hata", "Gelen veri kümesi boş.")
            return None
            
        # Topluluk Türünün Otomatik Tespiti
        self.log_action("Topluluk Türü Tespiti", "Yorum kelimelerine göre topluluk türü analiz ediliyor...")
        topluluk_turu = topluluk_turu_tespit_et(yorumlar)
        turu_str = "Genel / Karma Eğitim Topluluğu"
        
        self.log_action("Topluluk Türü Saptandı", f"Otomatik saptanan tür: {turu_str}")
        
        # Araç 1'in Tetiklenmesi (Duygu ve Kaygı Analizi)
        self.log_action("Araç Tetikleme", f"duygu_ve_kaygi_analizi() çağrılıyor. (Tür: {topluluk_turu})")
        duygu_sonuclari = duygu_ve_kaygi_analizi(yorumlar, topluluk_turu)
        
        # Araç 2'nin Tetiklenmesi (Topluluk Rol Dedektörü)
        self.log_action("Araç Tetikleme", f"dijital_rol_dedektoru() çağrılıyor. (Tür: {topluluk_turu})")
        rol_sonuclari = dijital_rol_dedektoru(yorumlar, topluluk_turu)
        
        # Künye ve API Bilgilerini kontrol et / doldur
        if not meta:
            meta = {"title": "Bilinmeyen Video", "uploader": "Bilinmeyen Kanal", "views": "Bilinmiyor"}
            
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
                self.log_action("API Algılandı", f"Aktif servis: {active_p}. Model test ediliyor...")
                success, resolved_model, msg = test_api_connection(active_p, active_k)
                if success:
                    api_info = {
                        "provider": active_p,
                        "api_key": active_k,
                        "model": resolved_model
                    }
                    self.log_action("API Test Başarılı", f"Saptanan model: {resolved_model}")
                else:
                    self.log_action("API Test Hatası", f"{msg}. Çevrimdışı modda devam ediliyor.")
        
        # Raporlama Aşaması
        akademik_rapor = None
        model_info = "Kural Tabanlı Analiz (Çevrimdışı Fallback)"
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
                    self.log_action("Nitel Raporlama (Mutabakat Modu)", f"Paralel modeller çağrılıyor: {', '.join(models_names)}")
                    llm_analysis_results, consensus_stats = analyze_comments_with_llm_consensus(
                        yorumlar, models_config, progress_cb
                    )
                    model_info = f"Çoklu LLM Mutabakat Modu ({', '.join(models_names)})"
                else:
                    self.log_action("Nitel Raporlama", f"{api_info['provider']} ({api_info['model']}) üzerinden detaylı analiz başlıyor...")
                    llm_analysis_results = analyze_comments_with_llm(
                        yorumlar, api_info["provider"], api_info["api_key"], api_info["model"], progress_cb
                    )
                    model_info = f"{api_info['provider'].upper()} API ({api_info['model']})"

                # LLM sonuçlarına göre istatistikleri derle
                total = len(yorumlar)
                kaygi_sayisi = sum(1 for r in llm_analysis_results if r.get("category") in ["Mesleki Gelecek Kaygisi", "Felsefi/Varolussal Sorgulama", "Etik ve Telif Hassasiyeti"])
                mentor_sayisi = sum(1 for r in llm_analysis_results if r.get("role") == "Akran Mentoru")
                cosku_sayisi = sum(1 for r in llm_analysis_results if r.get("category") in ["Heyecan ve Kesif Motivasyonu", "Yaratici Is Akisi Tartismasi"])
                hata_sayisi = sum(1 for r in llm_analysis_results if r.get("category") in ["Teknik Sorun ve Destek Arayisi", "Maliyet ve Erisilebilirlik Sorunu"])
                etik_sayisi = sum(1 for r in llm_analysis_results if r.get("category") in ["Etik ve Telif Hassasiyeti", "Felsefi/Varolussal Sorgulama"])
                destek_sayisi = sum(1 for r in llm_analysis_results if r.get("category") == "Sosyal Destek ve Tesekkur")

                stats = {
                    "total": total,
                    "kaygi": (kaygi_sayisi / total) * 100 if total > 0 else 0,
                    "mentor": (mentor_sayisi / total) * 100 if total > 0 else 0,
                    "cosku": (cosku_sayisi / total) * 100 if total > 0 else 0,
                    "hata": (hata_sayisi / total) * 100 if total > 0 else 0,
                    "etik": (etik_sayisi / total) * 100 if total > 0 else 0,
                    "destek": (destek_sayisi / total) * 100 if total > 0 else 0,
                }
                
                saglik_skoru = ((mentor_sayisi + destek_sayisi) / total) * 100 if total > 0 else 0
                if saglik_skoru >= 30:
                    stats["indeks"] = "🟢 Yüksek Sosyal Sermaye (A Sınıfı)"
                elif saglik_skoru >= 15:
                    stats["indeks"] = "🟡 Orta Sosyal Sermaye (B Sınıfı)"
                else:
                    stats["indeks"] = "🔴 Düşük Sosyal Sermaye (C Sınıfı)"
                
                # 2. Sentez Raporunu Oluştur
                self.log_action("Sentez Raporlama", "Analiz sonuçları birleştirilip rapor yazılıyor...")
                
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
                    meta, stats, yorumlar, report_provider, report_key, primary_model, llm_analysis_results
                )
                if not akademik_rapor:
                    raise Exception("Model boş rapor döndürdü.")
                
                # LLM analizini geriye dönük arayüzle uyumlu hale getirmek için duygu/rol dict'lerini güncelle
                duygu_sonuclari = {}
                rol_sonuclari = {}
                for r in llm_analysis_results:
                    cat = r.get("category", "Genel Gozlem")
                    duygu_sonuclari[cat] = duygu_sonuclari.get(cat, 0) + 1
                    rol = r.get("role", "Pasif Destekci")
                    rol_sonuclari[rol] = rol_sonuclari.get(rol, 0) + 1
                    
            except Exception as e:
                self.log_action("LLM Analiz/Raporlama Hatası", str(e))
                raise e
        else:
            # Fallback: Kural Tabanlı Rapor Oluşturucu (Çevrimdışı Mod)
            self.log_action("Araç Tetikleme", "izleyici_raporu_olusturucu() çağrılıyor (Çevrimdışı Mod)...")
            akademik_rapor = izleyici_raporu_olusturucu(duygu_sonuclari, rol_sonuclari, topluluk_turu)
            model_info = "Kural Tabanlı Analiz (Çevrimdışı Fallback)"
            consensus_stats = None
            
        self.log_action("Analiz Tamamlandı", "Tüm analizler ve rapor başarıyla birleştirildi.")
        
        return {
            "topluluk_turu": topluluk_turu,
            "topluluk_turu_str": turu_str,
            "duygu": duygu_sonuclari,
            "rol": rol_sonuclari,
            "rapor": akademik_rapor,
            "model_info": model_info,
            "llm_results": llm_analysis_results,
            "consensus_stats": consensus_stats
        }

        
    def get_logs(self):
        """İşlem günlüğünü dışarıya aktarır."""
        return self.logs

