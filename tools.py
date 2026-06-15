# -*- coding: utf-8 -*-
import os
import json
import re

# Etnografik Kural Tabanli Kelime Sozlukleri (Yuksek Cozunurluklu Analiz icin)
# YENI 12-KATEGORILI TAKSONOMI
JARGONS_SIHAY = {
    "Mesleki Gelecek Kaygisi": ["meslek", "bitti", "issiz", "ekmek", "korku", "yok edecek", "gelecek", "kaygi", "tehdit", "endise", "sektor", "yerimizi alacak", "ne yapacagiz"],
    "Heyecan ve Kesif Motivasyonu": ["harika", "inanilmaz", "deneyecegim", "super", "muhtesem", "demokratiklesme", "heyecan", "efsane", "mukemmel", "muthis", "buyuleyici", "kalite", "sanat", "saka"],
    "Etik ve Telif Hassasiyeti": ["etik disi", "izinsiz", "taranmasi", "karsiyim", "emek hirsizligi", "sanatci haklari", "intihal", "emek", "hirsizlik", "ozgun", "kopya"],
    "Teknik Sorun ve Destek Arayisi": ["parametre", "hata", "nasil", "kodlar", "yardimci", "hata aliyorum", "calismadi", "versiyon"],
    "Maliyet ve Erisilebilirlik Sorunu": ["ucretsiz", "bedava", "uyelik", "kredi", "dolar", "fatura", "maliyet", "parali"],
    "Yaratici Is Akisi Tartismasi": ["kurgu", "montaj", "video", "premiere", "capcut", "runway", "midjourney", "ses", "arkaplan", "render", "kamera", "animasyon", "workflow"],
    "Sosyal Destek ve Tesekkur": ["tesekkur", "emegine saglik", "cansin", "hocam", "abi", "kral", "dokturmussun", "iyi ki varsin", "eline saglik", "sagol", "selam"],
    "Akran Mentorlugu ve Yonlendirme": ["bunu dene", "emin ol", "kullanirsan", "cozum", "linkte var"],
    "Icerik Talebi ve Oneri": ["devami gelsin", "sunu da", "yaparsaniz sevinirim", "bekliyoruz"],
    "Ironi, Kinaye veya Sarkastik Yorum": ["yok artik", "tabii canim", "kesin oyledir", "isimize yarar (!)", "ne guzel", "issiz kaldik desene"]
}

JARGONS_MEYDAN = {
    "Teknik Sorun ve Destek Arayisi": ["webhook", "hata", "port", "baglanti", "docker", "connection", "localhost", "notebook", "kutuphane", "hata aliyorum", "kod", "python", "hata veriyor", "tetiklenmiyor"],
    "Heyecan ve Kesif Motivasyonu": ["otomatik", "saniyeler", "zaman kazandiriyor", "sayenizde", "is yukunu", "mucize", "kolaylastirdi", "verimlilik", "asistan", "hizli", "agent", "ajan"],
    "Etik ve Telif Hassasiyeti": ["sinav", "kopya", "odev", "ogrenme", "adil", "akademik durustluk"],
    "Felsefi/Varolussal Sorgulama": ["bilissel", "tembellik", "zihinsel", "denge", "etik", "guvenlik", "yapay zeka nereye", "tehlike", "bilinc"],
    "Yaratici Is Akisi Tartismasi": ["mimari", "tasarim", "framework", "sunucu", "vps", "mcp", "n8n", "claude", "gemini", "agentic", "otonom", "entegrasyon"],
    "Maliyet ve Erisilebilirlik Sorunu": ["api", "token", "maliyet", "fatura", "dolar", "can sikiyor", "ucretli", "ollama", "yerel model", "local", "llama", "harcama"],
    "Sosyal Destek ve Tesekkur": ["tesekkur", "emegine saglik", "cansin", "hocam", "abi", "kral", "rehber", "eline saglik", "sagol", "selam", "iyi ki varsin"],
    "Akran Mentorlugu ve Yonlendirme": ["kurmayi dene", "oneririm", "yazman gerekiyor", "github"]
}

JARGONS_GENEL = {
    "Mesleki Gelecek Kaygisi": ["meslek", "bitti", "issiz", "korku", "yok edecek", "gelecek", "kaygi", "tehdit", "endise"],
    "Teknik Sorun ve Destek Arayisi": ["hata", "baglanti", "docker", "hata aliyorum", "calismadi", "versiyon", "sunucu"],
    "Heyecan ve Kesif Motivasyonu": ["harika", "zaman kazandiriyor", "sayenizde", "mucize", "kolaylastirdi", "super", "muthis"],
    "Maliyet ve Erisilebilirlik Sorunu": ["api", "token", "maliyet", "fatura", "ucretli", "ucretsiz", "bedava"],
    "Sosyal Destek ve Tesekkur": ["tesekkur", "emegine saglik", "hocam", "abi", "kral", "eline saglik", "sagol"],
    "Icerik Talebi ve Oneri": ["devamini", "bekliyorum", "sunu da anlatin"]
}

def topluluk_turu_tespit_et(yorumlar):
    """
    Yorum havuzundaki kelime sikliklarina gore toplulugun turunu otomatik tespit eder.
    """
    creative_words = ["kurgu", "tasarim", "premiere", "video", "render", "midjourney", "sora", "gorsel", "capcut", "runway", "vfx", "sanat", "photoshop", "kamera", "montaj"]
    technical_words = ["docker", "webhook", "port", "n8n", "kod", "python", "api", "server", "localhost", "connection", "entegrasyon", "veritabani", "database", "mcp", "sunucu", "container"]
    
    creative_score = 0
    technical_score = 0
    
    for y in yorumlar:
        comment_lower = y.get("comment", "").lower()
        for w in creative_words:
            if w in comment_lower:
                creative_score += 1
        for w in technical_words:
            if w in comment_lower:
                technical_score += 1
                
    if creative_score > technical_score and creative_score >= 2:
        return "sihay"  # Yaratici / Tasarim
    elif technical_score > creative_score and technical_score >= 2:
        return "meydan"  # Teknik / Otomasyon
    else:
        return "genel"  # Genel / Karma

def kelime_sayaci_analiz(yorum, sozluk):
    """
    Yorum iceriginde belirli kategorilere ait kelimelerin sikligini kontrol eder.
    En yuksek eslesmeye sahip kategoriyi doner.
    """
    skorlar = {kat: 0 for kat in sozluk.keys()}
    yorum_temiz = yorum.lower()
    
    for kat, kelimeler in sozluk.items():
        for kelime in kelimeler:
            if kelime in yorum_temiz:
                skorlar[kat] += 1
                
    en_yuksek_skor = max(skorlar.values())
    if en_yuksek_skor == 0:
        return "Genel Gozlem / Yuzeysel Katilim"
    
    # En yuksek skora sahip kategoriyi dondur
    en_iyi_kategoriler = [kat for kat, skor in skorlar.items() if skor == en_yuksek_skor]
    return en_iyi_kategoriler[0]

def duygu_ve_kaygi_analizi(yorumlar, topluluk_turu):
    """
    [ARAC 1] Yorumlardaki duygu, kaygi ve temalari analiz eder.
    """
    if topluluk_turu == "sihay":
        sozluk = JARGONS_SIHAY
    elif topluluk_turu == "meydan":
        sozluk = JARGONS_MEYDAN
    else:
        sozluk = JARGONS_GENEL
        
    sonuclar = {}
    for y in yorumlar:
        kategori = kelime_sayaci_analiz(y.get("comment", ""), sozluk)
        sonuclar[kategori] = sonuclar.get(kategori, 0) + 1
        
    return sonuclar

def dijital_rol_dedektoru(yorumlar, topluluk_turu):
    """
    [ARAC 2] Yorumlari yazan izleyicilerin/kullanicilarin topluluktaki rollerini tespit eder.
    """
    sonuclar = {}
    
    for y in yorumlar:
        yorum_text = y.get("comment", "").lower()
        
        # Akran mentorlugu kontrolu
        cevap_mi = "@" in yorum_text or any(w in yorum_text for w in ["dene", "emin ol", "kullanirsan", "kurmayi dene", "oneririm", "yazman gerekiyor", "github", "link"])
        
        if cevap_mi:
            rol = "Akran Mentoru"
        else:
            if topluluk_turu == "sihay":
                if any(w in yorum_text for w in ["kurgu", "tasarim", "premiere", "is akis", "calisiyorum", "render"]):
                    rol = "Profesyonel Uygulayici"
                elif any(w in yorum_text for w in ["etik", "sanatci", "telif", "emek"]):
                    rol = "Elestirel Dusunur"
                elif any(w in yorum_text for w in ["nasil", "yapabilirim", "ogrenmek"]):
                    rol = "Yeni Kesfeci / Merakli"
                elif any(w in yorum_text for w in ["calismadi", "hata", "parali"]):
                    rol = "Hayal Kirikligi"
                else:
                    rol = "Pasif Destekci"
            elif topluluk_turu == "meydan":
                if any(w in yorum_text for w in ["sirket", "docker", "port", "sistem", "entegrasyon", "otomasyon"]):
                    rol = "Profesyonel Uygulayici"
                elif any(w in yorum_text for w in ["etik", "bilissel", "tehlike", "felsefi"]):
                    rol = "Elestirel Dusunur"
                elif any(w in yorum_text for w in ["nasil", "baslarim", "rehber"]):
                    rol = "Yeni Kesfeci / Merakli"
                elif any(w in yorum_text for w in ["hata", "calismiyor", "token", "ucretli"]):
                    rol = "Hayal Kirikligi"
                else:
                    rol = "Pasif Destekci"
            else:  # genel
                if any(w in yorum_text for w in ["nasil", "harika"]):
                    rol = "Yeni Kesfeci / Merakli"
                elif any(w in yorum_text for w in ["calismiyor", "hata"]):
                    rol = "Hayal Kirikligi"
                else:
                    rol = "Pasif Destekci"
                    
        sonuclar[rol] = sonuclar.get(rol, 0) + 1
        
    return sonuclar

def tekil_yorum_izleyici_onerisi(yorum_text, duygu, rol, topluluk_turu):
    """
    Tekil yorumun icerigine, duygu ve rol siniflarina gore kisisellestirilmis 
    bir izleyici odakli mudahale onerisi uretir.
    """
    yorum_lower = yorum_text.lower()
    
    if "gelecek" in duygu.lower() or "kaygi" in duygu.lower():
        if "tasarim" in rol.lower() or "uygulayici" in rol.lower():
            return "Izleyici mesleki gelecek konusunda yuksek tehdit algilamaktadir. Yapay zekanini yaraticiligi yok etmeyecegi, aksine bir 'co-creator' (ortak uretici) olarak is akisini destekleyecegi uygulamali atolyelerle gosterilmelidir."
        else:
            return "Izleyici yapay zekanin bilissel veya ekonomik etkileri nedeniyle endiselidir. Mufredata teknoloji okuryazarligi ve etik kullanim modulleri eklenerek yapay zekanin sinirlari ve insan denetimi rolu anlatilmalidir."
            
    if "hata" in duygu.lower() or "sorun" in duygu.lower():
        return "Izleyici teknik bir engelle karsilasmis ve tikanmistir. Akran mentorlugu mekanizmalari devreye sokulmali veya benzer hatalarin cozumlerini barindiran asenkron bir 'Sikca Sorulan Sorular' (FAQ) bilgi tabani onerilmelidir."
        
    if "motivasyon" in duygu.lower() or "heyecan" in duygu.lower():
        if "mentor" in rol.lower():
            return "Bu izleyici akranlarina yardim etme egilimindedir. Izleyicinin asistan ogretmen veya akran mentoru olarak konumlandirilmasi, topluluk ici ogrenme baglarini guclendirecektir."
        else:
            return "Izleyici verimlilik odaginda yuksek motivasyona sahiptir. Ancak bilissel tembellik riskine karsi, ona otomasyonun arka planindaki mantiksal mimariyi ve problem cozme sureclerini soran derinlestirici odevler verilmelidir."
            
    if "etik" in duygu.lower() or "felsefi" in duygu.lower():
        return "Izleyici konunun etik, akademik durustluk veya felsefi boyutlarini sorgulamaktadir. Sinifta yapay zekanin etik sinirlari ve fikri mulkiyet tartismalarini iceren bir forum veya munazara duzenlenmesi faydali olacaktir."
        
    if "destek" in duygu.lower() or "tesekkur" in duygu.lower():
        return "Izleyici topluluga aidiyet hissetmekte ve motivasyonu yuksektir. Tesekkur geri bildirimi takdir edilmeli, izleyici motivasyonunun surmesi icin bir sonraki seviye kaynaklara yonlendirilmelidir."
        
    return "Izleyicinin katilimi aktiftir. Kendi kendine ogrenme surecini desteklemek amaciyla konuya dair zenginlestirici ek kaynaklar ve kesif odakli projeler onerilmelidir."

def izleyici_raporu_olusturucu(duygu_analizler, rol_analizler, topluluk_turu):
    """
    [ARAC 3] Girilen tek videonun yorum istatistiklerinden yola cikarak izleyici ve antropolojik rapor uretir.
    """
    rapor = "## Topluluk Izleyici Iklimi & Kulturel Analiz Raporu\n\n"
    
    turu_str = {
        "sihay": "Yaratici & Tasarim Odakli Topluluk",
        "meydan": "Teknik & Otomasyon Odakli Topluluk",
        "genel": "Genel / Karma Egitim Toplulugu"
    }.get(topluluk_turu, "Bilinmeyen Topluluk")
    
    rapor += f"### Saptanan Iklim Turu: **{turu_str}**\n"
    
    total_comments = sum(duygu_analizler.values())
    
    # 1. Kulturel Kaygi Orani
    kaygi_kategorileri = ["Mesleki Gelecek Kaygisi", "Felsefi/Varolussal Sorgulama", "Etik ve Telif Hassasiyeti"]
    kaygi_sayisi = sum(duygu_analizler.get(k, 0) for k in kaygi_kategorileri)
    kaygi_oran = (kaygi_sayisi / total_comments) * 100 if total_comments > 0 else 0
    
    # 2. Akran Mentorlugu Orani
    mentor_sayisi = rol_analizler.get("Akran Mentoru", 0)
    mentor_oran = (mentor_sayisi / total_comments) * 100 if total_comments > 0 else 0
 
    # 3. Ogrenme Motivasyonu ve Kesif Coskusu
    cosku_kategorileri = ["Heyecan ve Kesif Motivasyonu", "Yaratici Is Akisi Tartismasi"]
    cosku_sayisi = sum(duygu_analizler.get(k, 0) for k in cosku_kategorileri)
    cosku_oran = (cosku_sayisi / total_comments) * 100 if total_comments > 0 else 0
 
    # 4. Teknik Tikanma ve Soru/Hata Orani
    hata_kategorileri = ["Teknik Sorun ve Destek Arayisi", "Maliyet ve Erisilebilirlik Sorunu"]
    hata_sayisi = sum(duygu_analizler.get(k, 0) for k in hata_kategorileri)
    hata_oran = (hata_sayisi / total_comments) * 100 if total_comments > 0 else 0
 
    # 5. Elestirel Suphecilik ve Etik/Felsefi Kaygi Orani
    etik_sayisi = (
        duygu_analizler.get("Etik ve Telif Hassasiyeti", 0) + 
        duygu_analizler.get("Felsefi/Varolussal Sorgulama", 0)
    )
    etik_oran = (etik_sayisi / total_comments) * 100 if total_comments > 0 else 0
 
    # 6. Sosyal Destek ve Tesekkur Orani
    destek_sayisi = duygu_analizler.get("Sosyal Destek ve Tesekkur", 0)
    destek_oran = (destek_sayisi / total_comments) * 100 if total_comments > 0 else 0
 
    # 7. Topluluk Katilim Sagligi Indeksi
    saglik_skoru = ((mentor_sayisi + destek_sayisi) / total_comments) * 100 if total_comments > 0 else 0
    if saglik_skoru >= 30:
        saglik_derecesi = "Yuksek Sosyal Sermaye (A Sinifi Topluluk)"
    elif saglik_skoru >= 15:
        saglik_derecesi = "Orta Sosyal Sermaye (B Sinifi Topluluk)"
    else:
        saglik_derecesi = "Dusuk Sosyal Sermaye (C Sinifi Topluluk - Bireysel Katilim Yogun)"
 
    rapor += f"- **Izleyicilerin Toplam Sayisi:** `{total_comments}` yorum analizi yapildi.\n"
    rapor += f"- **Kulturel Kaygi ve Tehdit Algisi Orani:** %{kaygi_oran:.1f}\n"
    rapor += f"- **Akran Mentorlugu ve Sosyal Sermaye Orani:** %{mentor_oran:.1f}\n"
    rapor += f"- **Izleme Motivasyonu ve Kesif Coskusu Orani:** %{cosku_oran:.1f}\n"
    rapor += f"- **Teknik Tikanma ve Soru/Hata Orani:** %{hata_oran:.1f}\n"
    rapor += f"- **Elestirel Suphecilik ve Etik/Felsefi Dusunce Orani:** %{etik_oran:.1f}\n"
    rapor += f"- **Sosyal Destek ve Tesekkur Orani:** %{destek_oran:.1f}\n"
    rapor += f"- **Topluluk Katilim Sagligi Indeksi:** `{saglik_derecesi}` (Sosyal Sermaye Skoru: %{saglik_skoru:.1f})\n\n"
 
    
    rapor += "### Etnografik Degerlendirme\n"
    if topluluk_turu == "sihay":
        rapor += "Bu toplulukta estetik uretim kaygilari on plandadir. Izleyiciler yapay zekayi mesleklerini ellerinden alacak ekonomik bir tehdit olarak gorme egilimindedir. Teknik sorunlar daha cok pratik arayuz ve parametre ayarlarina odaklanmaktadir.\n\n"
        rapor += "**Egitsel Mudahale Onerisi:** Yaratici sureclerde yapay zeka entegrasyonu anlatilirken, yapay zekanin insanin ozgunlugunu oldurmeyecegi, aksine hizlandirici bir asistan oldugu vurgulanmalidir. Egitim mufredatlarina 'Yapay Zeka ile Birlikte Yaratim (Human-AI Co-Creation)' atolyeleri eklenmelidir.\n"
    elif topluluk_turu == "meydan":
        rapor += "Bu toplulukta is sureclerinin otomatizasyonu ve verimlilik motivasyonu cok yuksektir. Ancak izleyicilerin karsilastigi en buyuk engeller teknik entegrasyon hatalari (port cakismasi, docker hatalari vb.) ve API maliyetleridir. Bilissel yuku yapay zekaya devretme hevesi mevcuttur.\n\n"
        rapor += "**Egitsel Mudahale Onerisi:** Izleyicilere sadece otomasyon akislari (no-code) kurmak degil, sistem mimarisi, veri guvenligi ve debugging (hata ayiklama) surecleri de derinlemesine ogretilmelidir. Yapay zekanin getirecegi 'bilissel tembellik' riskine karsi, izleyicileri kodun arkasindaki mantigi sorgulamaya iten odevler kurgulanmalidir.\n"
    else:
        rapor += "Bu topluluk karma ve genel bir izleyici iklimi sergilemektedir. Hem pratik arac kullanimi meraki hem de genel yapay zeka okuryazarligi ihtiyaci mevcuttur. Belirgin tek bir jargon kumesi yerine sosyal tesekkur ve basit arayislar yogundur.\n\n"
        rapor += "**Egitsel Mudahale Onerisi:** Karma izleyici gruplarinda temel yapay zeka okuryazarligi dersleri onceliklendirilmelidir. Teknik ve yaratici becerileri harmanlayan disiplinlerarasi projeler gelistirilmeli, akran mentorlugunu artirmak icin isbirlikci calisma gruplari kurulmalidir.\n"
        
    rapor += "\n> [!IMPORTANT]\n"
    rapor += "> **Degerlendirme ve Etik Sinir Uyarisi:** Bu rapor, cevrimici toplulugun dil jargonlari ve davranissal ayak izlerinin otomatik analizi ile uretilmistir. Bu veriler kesin birer hukum teskil etmez. Mudahaler uygulanmadan once mutlaka arastirmaci degerlendirmesi ve insan odakli gozlemlerle dogrulanmalidir."
    
    return rapor
