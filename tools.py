# -*- coding: utf-8 -*-
import os
import json
import re

# Etnografik Kural Tabanli Kelime Sozlukleri (Yuksek Cozunurluklu Analiz icin)
# YENI 12-KATEGORILI TAKSONOMI
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
    Sadelestirilmis versiyon: Sadece genel topluluk döner.
    """
    return "genel"

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
    
    turu_str = "Genel / Karma Egitim Toplulugu"
    
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
    rapor += "Bu topluluk karma ve genel bir izleyici iklimi sergilemektedir. Hem pratik arac kullanimi meraki hem de genel yapay zeka okuryazarligi ihtiyaci mevcuttur. Belirgin tek bir jargon kumesi yerine sosyal tesekkur ve basit arayislar yogundur.\n\n"
    rapor += "**Egitsel Mudahale Onerisi:** Karma izleyici gruplarinda temel yapay zeka okuryazarligi dersleri onceliklendirilmelidir. Teknik ve yaratici becerileri harmanlayan disiplinlerarasi projeler gelistirilmeli, akran mentorlugunu artirmak icin isbirlikci calisma gruplari kurulmalidir.\n"
        
    rapor += "\n> [!IMPORTANT]\n"
    rapor += "> **Degerlendirme ve Etik Sinir Uyarisi:** Bu rapor, cevrimici toplulugun dil jargonlari ve davranissal ayak izlerinin otomatik analizi ile uretilmistir. Bu veriler kesin birer hukum teskil etmez. Mudahaler uygulanmadan once mutlaka arastirmaci degerlendirmesi ve insan odakli gozlemlerle dogrulanmalidir."
    
    return rapor
