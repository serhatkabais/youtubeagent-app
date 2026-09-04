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

COMMUNITY_LEXICONS = {
    "kodlama_ve_yazilim": {
        "words": ["python", "docker", "api", "port", "hata", "kod", "server", "sunucu", "webhook", "node", "n8n", "github", "terminal", "versiyon", "bug", "sql", "database"],
        "label_tr": "Yazılım Geliştirme & Sistem Topluluğu",
        "label_en": "Software Engineering & Systems Community"
    },
    "gorsel_ve_tasarim": {
        "words": ["midjourney", "tasarım", "çizim", "sanat", "art", "render", "görsel", "illüstrasyon", "photoshop", "telif", "hırsızlık", "estetik", "yaratıcı", "animasyon"],
        "label_tr": "Yaratıcı Sanatlar & Görsel Tasarım Topluluğu",
        "label_en": "Creative Arts & Visual Design Community"
    },
    "felsefe_ve_etik": {
        "words": ["bilinç", "insanlık", "agi", "felsefe", "etik", "varoluşsal", "matrix", "singularity", "zihin", "düşünce", "ruh", "kıyamet"],
        "label_tr": "Akademik & Felsefi Teknoloji Topluluğu",
        "label_en": "Academic & Philosophical Technology Community"
    }
}

def topluluk_turu_tespit_et(yorumlar):
    """
    Yorum havuzundaki kelime sikliklarina gore toplulugun etnografik turunu otomatik tespit eder.
    """
    scores = {k: 0 for k in COMMUNITY_LEXICONS}
    for y in yorumlar:
        txt = y.get("comment", "").lower()
        for c_type, info in COMMUNITY_LEXICONS.items():
            for w in info["words"]:
                if w in txt:
                    scores[c_type] += 1

    best_type = max(scores, key=scores.get)
    if scores[best_type] == 0:
        return "genel"
    return best_type

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
    [ARAC 2] Yorumlari yazan izleyicilerin/kullanicilarin topluluktaki rollerini 
    Kozinets (2015/2020) Netnografik Tipolojisine gore tespit eder:
    - Icerideki / Akran Mentoru (Insider): Yuksek uzmanlik ve topluluk bagliligi
    - Tutkulu / Uretici Izleyici (Devotee): Yuksek uzmanlik/merak, bireysel odak
    - Sosyallesen / Topluluk Destekcisi (Mingler): Guclu sosyal bag, dayanisma
    - Turist / Pasif Izleyici (Tourist): Yuzeysel/cevredekiler katilimi
    """
    sonuclar = {}
    
    for y in yorumlar:
        yorum_text = y.get("comment", "").lower()
        
        # Akran mentorlugu ve uzman yanit kontrolu (Insider)
        cevap_mi = "@" in yorum_text or any(w in yorum_text for w in ["dene", "emin ol", "kullanirsan", "kurmayi dene", "oneririm", "yazman gerekiyor", "github", "link", "cozum", "port", "terminal"])
        
        if cevap_mi:
            rol = "Icerideki / Akran Mentoru"
        else:
            if any(w in yorum_text for w in ["otomasyon", "kod", "n8n", "pipeline", "entegrasyon", "model", "proje", "tasarim", "workflow"]):
                rol = "Tutkulu / Uretici Izleyici"
            elif any(w in yorum_text for w in ["tesekkur", "hocam", "abi", "cansin", "ogrenmenin", "emegine", "harika"]):
                rol = "Sosyallesen / Topluluk Destekcisi"
            elif len(yorum_text.split()) <= 3 or any(w in yorum_text for w in ["ilk yorum", "super", "guzel", "👍", "🔥"]):
                rol = "Turist / Pasif Izleyici"
            else:
                rol = "Tutkulu / Uretici Izleyici"
                
        sonuclar[rol] = sonuclar.get(rol, 0) + 1
        
    return sonuclar

def tekil_yorum_izleyici_onerisi(yorum_text, duygu, rol, topluluk_turu):
    """
    Tekil yorumun icerigine, duygulanim iklimine ve Kozinets netnografik rolune gore
    etnografik cozumleme ve mudahale/arastirma notu uretir.
    """
    duygu_lower = duygu.lower()
    rol_lower = rol.lower()
    
    if "gelecek" in duygu_lower or "kaygi" in duygu_lower:
        return "Etnografik Çözümleme (Sara Ahmed Duygulanım Boyutu): İzleyici, teknolojik prekarite ve mesleki tehdit algısı yaşamaktadır. Teknoloji ikame edici değil, tamamlayıcı zekâ (augmented intelligence) olarak konumlandırılmalı; bilişsel dayanıklılığı güçlendiren uygulamalı atölyeler tasarlanmalıdır."
            
    if "hata" in duygu_lower or "sorun" in duygu_lower:
        return "Etnografik Çözümleme (Socio-Teknik Sürtünme): İzleyici araç entegrasyonunda teknik bir eşikle karşılaşmıştır. Topluluk içi asenkron hata-çözüm havuzu ve akran mentörlüğü teşvik edilerek topluluğun kendi kendini onarma kapasitesi harekete geçirilmelidir."
        
    if "motivasyon" in duygu_lower or "heyecan" in duygu_lower:
        if "mentor" in rol_lower or "icerideki" in rol_lower:
            return "Etnografik Çözümleme (Kozinets - Insider/Sosyal Sermaye): İzleyici organik bir pedagojik liderlik sergilemektedir. Topluluk içi tartışma yöneticisi (moderatör) veya asistan mentör olarak konumlandırılması, ağın sosyal sermayesini katlayacaktır."
        else:
            return "Etnografik Çözümleme (Kozinets - Devotee/Üretici Merak): İzleyici yüksek keşif tutkusuna sahiptir. Bilişsel tembellik riskine karşı, ona hazır komutları kopyalamak yerine sistem mimarisini ve mantıksal problem çözmeyi sorgulatan derinleştirici meydan okumalar verilmelidir."
            
    if "etik" in duygu_lower or "felsefi" in duygu_lower:
        return "Etnografik Çözümleme (Eleştirel Siber-Bilinç): İzleyici yapay zekânın ontolojik sınırlarını, telif adaletini ve insan emeğinin değerini sorgulamaktadır. Bu eleştirel sorgulama, toplulukta yapay zekâ felsefesi ve etik tasarım temalı tartışma başlıklarıyla zenginleştirilmelidir."
        
    if "destek" in duygu_lower or "tesekkur" in duygu_lower:
        return "Etnografik Çözümleme (Kozinets - Mingler/Aidiyet): İzleyici topluluk agorasına aidiyet hissetmekte ve duygusal dayanışma üretmektedir. Teşekkür geri bildirimi takdir edilerek izleyici daha derin teknik üretim halkalarına davet edilmelidir."
        
    if "turist" in rol_lower or "pasif" in rol_lower:
        return "Etnografik Çözümleme (Meşru Çevresel Katılım - Lave & Wenger): İzleyici çevre halkada gözlemci konumundadır. Açık uçlu sorular ve mikro etkileşimlerle periferal katılımdan aktif topluluk paydaşlığına geçişi desteklenmelidir."
        
    return "Etnografik Çözümleme: İzleyicinin çevrimiçi katılımı aktiftir. Öz-düzenlemeli öğrenme (self-regulated learning) sürecini derinleştirmek için açık kaynaklı araştırma projeleri ve keşif görevleri önerilmelidir."

def izleyici_raporu_olusturucu(duygu_analizler, rol_analizler, topluluk_turu, sessiz_cogunluk=None):
    """
    [ARAC 3] Yorum istatistiklerinden ve sessiz çoğunluk metriklerinden yola cikarak netnografik ve antropolojik saha raporu uretir.
    """
    rapor = "## Çevrimiçi Topluluk Etnografik İklim & Kültürel Analiz Raporu\n\n"
    
    lex_info = COMMUNITY_LEXICONS.get(topluluk_turu, {})
    turu_str = lex_info.get("label_tr", "Genel Çevrimiçi Öğrenme Topluluğu")
    
    rapor += f"### Saptanan Siber-Topluluk Türü: **{turu_str}**\n"
    
    total_comments = sum(duygu_analizler.values())
    
    # 1. Kulturel Kaygi Orani
    kaygi_kategorileri = ["Mesleki Gelecek Kaygisi", "Felsefi/Varolussal Sorgulama", "Etik ve Telif Hassasiyeti"]
    kaygi_sayisi = sum(duygu_analizler.get(k, 0) for k in kaygi_kategorileri)
    kaygi_oran = (kaygi_sayisi / total_comments) * 100 if total_comments > 0 else 0
    
    # 2. Akran Mentorlugu Orani (Kozinets - Insider)
    mentor_sayisi = rol_analizler.get("Icerideki / Akran Mentoru", rol_analizler.get("Akran Mentoru", 0))
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
 
    # 7. Topluluk Katilim Sagligi Indeksi (Sosyal Sermaye)
    saglik_skoru = ((mentor_sayisi + destek_sayisi) / total_comments) * 100 if total_comments > 0 else 0
    if saglik_skoru >= 30:
        saglik_derecesi = "Yüksek Sosyal Sermaye (Organik Dayanışma Baskın Topluluk)"
    elif saglik_skoru >= 15:
        saglik_derecesi = "Orta Düzey Sosyal Sermaye (Dengeli Etkileşim)"
    else:
        saglik_derecesi = "Düşük Sosyal Sermaye (Bireysel / Yüzeysel Tüketim Baskın)"
 
    rapor += f"- **İncelenen Toplam Dijital Etkileşim (Yorum):** `{total_comments}` birim analiz edildi.\n"
    rapor += f"- **Kolektif Kaygı ve Teknolojik Prekarite Oranı:** %{kaygi_oran:.1f}\n"
    rapor += f"- **Akran Mentörlüğü & İçeridekiler (Kozinets Insider):** %{mentor_oran:.1f}\n"
    rapor += f"- **Keşif Tutkusu & Üretken Motivasyon Oranı:** %{cosku_oran:.1f}\n"
    rapor += f"- **Teknik Eşik / Sosyo-Teknik Sürtünme Oranı:** %{hata_oran:.1f}\n"
    rapor += f"- **Eleştirel Şüphecilik ve Etik Sorgulama Oranı:** %{etik_oran:.1f}\n"
    rapor += f"- **Sosyal Destek ve Aidiyet İfadeleri Oranı:** %{destek_oran:.1f}\n"
    rapor += f"- **Topluluk Sosyal Sermaye Endeksi:** `{saglik_derecesi}` (Skor: %{saglik_skoru:.1f})\n\n"

    # Sessiz Çoğunluk & Katılım Eşitsizliği (90-9-1) Bölümü
    if sessiz_cogunluk:
        rapor += "### Görünmez Kitle ve Katılım Eşitsizliği (Sessiz Çoğunluk / Lurkers & 90-9-1 Kuralı)\n"
        rapor += f"- **Topluluk Canlılık Tipolojisi:** `{sessiz_cogunluk['tipoloji_baslik']}`\n"
        rapor += f"- **Yorum/İzlenme Oranı (CVR):** %{sessiz_cogunluk['cvr']:.3f}\n"
        rapor += f"- **Beğeni/İzlenme Oranı (LVR):** %{sessiz_cogunluk['lvr']:.3f}\n"
        rapor += f"- **Sessiz İzleyici (Lurker) Oranı:** %{sessiz_cogunluk['lurker_ratio']:.2f}\n"
        rapor += f"- **Katılım Eşitsizliği Dağılımı (Nielsen Modeli):** %{sessiz_cogunluk['nielsen']['lurkers_pct']} Sessiz İzleyici, %{sessiz_cogunluk['nielsen']['intermittent_pct']} Hafif Etkileşim (Beğeni), %{sessiz_cogunluk['nielsen']['creators_pct']} Aktif Yorumcu\n"
        rapor += f"- **Etnografik Çözümleme:** {sessiz_cogunluk['aciklama']}\n\n"
 
    rapor += "### Etnografik ve Dijital Antropolojik Değerlendirme\n"
    rapor += f"İncelenen siber topluluk, **{turu_str}** karakteristiği sergilemektedir. "
    rapor += "Yorum havuzunda dilsel örüntüler, topluluğun hem pratik araç adaptasyonu yaşadığını hem de algoritmik dönüşümün getirdiği sosyo-duygusal çalkantıları paylaştığını göstermektedir. Kozinets'in netnografik çerçevesinde akran dayanışması organik bir öğrenme ağı oluşturmaktadır.\n\n"
    rapor += "**Etnografik Araştırma Notu:** Toplulukta akran mentörlüğünü güçlendirecek açık kaynaklı işbirlikleri teşvik edilmeli; teknolojik anksiyete yaşayan katılımcılara yönelik 'tamamlayıcı zekâ' odaklı eleştirel yapay zekâ okuryazarlığı alanları açılmalıdır.\n"
        
    rapor += "\n> [!IMPORTANT]\n"
    rapor += "> **Dijital Etnografi & Etik Sınır Bildirimi:** Bu rapor, çevrimiçi topluluğun kamuya açık dijital ayak izlerinin hesaplamalı söylem analizi ile üretilmiştir. Nitel araştırmalarda araştırmacının özdüşünümselliği (reflexivity) esastır; otomatik bulgular araştırmacının derinlemesine saha gözlemleriyle birlikte yorumlanmalıdır."
    
    return rapor


def parse_int_metric(val):
    """
    Sayısal metinleri (örneğin '142,500', '4.820', '15 (Nitel Etnografik Örneklem)')
    güvenle tamsayıya dönüştürür.
    """
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    match = re.search(r'[\d,\.]+', str(val))
    if match:
        clean = match.group(0).replace(',', '').replace('.', '')
        if clean.isdigit():
            return int(clean)
    return 0


def analiz_et_sessiz_cogunluk(views, likes, comment_count, lang="tr"):
    """
    [ARAC 4] Jakob Nielsen'in (2006) Katılım Eşitsizliği (90-9-1 Kuralı) ve
    Nonnecke & Preece (2000) Lurker (Sessiz İzleyici) Kuramı temelinde
    videonun görünmeyen kitlesini, katılım eşitsizliğini ve topluluk canlılığını modeller.
    """
    v = parse_int_metric(views)
    l = parse_int_metric(likes)
    c = parse_int_metric(comment_count)

    # Oranlar (Yüzdelik)
    cvr = (c / v * 100) if v > 0 else 0.0  # Comment-to-View Ratio
    lvr = (l / v * 100) if v > 0 else 0.0  # Like-to-View Ratio
    active_interaction_ratio = cvr + lvr
    lurker_ratio = max(0.0, 100.0 - active_interaction_ratio) if v > 0 else 90.0

    # Nielsen 90-9-1 Dağılımı Tahmini
    if v > 0:
        actual_lurker_pct = round(lurker_ratio, 2)
        actual_intermittent_pct = round(lvr, 2)
        actual_creator_pct = round(cvr, 2)
    else:
        actual_lurker_pct = 90.0
        actual_intermittent_pct = 9.0
        actual_creator_pct = 1.0

    # Topluluk Canlılık Tipolojisi (Vitality Typology)
    if cvr >= 0.5:
        tipoloji_key = "hiper_aktif"
        baslik = "Hiper-Aktif Dijital Agora" if lang == "tr" else "Hyper-Active Digital Agora"
        badge_color = "#2E7D32"
        aciklama = (
            f"Yorum/İzlenme oranı (%{cvr:.2f}) eşiğin üzerindedir. İzleyiciler pasif tüketici değil, "
            f"topluluk agorasında aktif tartışma ve içerik ortak-üreticisi (prosumer) konumundadır. "
            f"Kozinets'in 'İçeridekiler' ve 'Tutkulular' rolleri bu ekolojide yüksek görünürlük kazanır."
            if lang == "tr" else
            f"The Comment-to-View ratio (%{cvr:.2f}) is significantly high. Viewers act not merely as passive consumers, "
            f"but as active co-producers (prosumers) in the digital agora. Kozinets' 'Insiders' and 'Devotees' roles flourish here."
        )
    elif cvr >= 0.15:
        tipoloji_key = "dengeli"
        baslik = "Dengeli Öğrenme Topluluğu" if lang == "tr" else "Balanced Learning Community"
        badge_color = "#1A365D"
        aciklama = (
            f"Yorum/İzlenme oranı (%{cvr:.2f}) sağlıklı bir çevrimiçi öğrenme eğrisine işaret eder. "
            f"Çekirdek bir akran mentörlüğü ve soru-cevap grubu bulunurken, izleyicilerin büyük çoğunluğu "
            f"(%{lurker_ratio:.1f}) Lave ve Wenger'in tanımladığı 'Meşru Çevresel Katılım' (legitimate peripheral participation) halindedir."
            if lang == "tr" else
            f"The Comment-to-View ratio (%{cvr:.2f}) indicates a balanced online learning environment. "
            f"A core peer-mentoring circle coexists with a wide majority (%{lurker_ratio:.1f}) engaged in Lave & Wenger's 'Legitimate Peripheral Participation'."
        )
    else:
        tipoloji_key = "sessiz_tuketim"
        baslik = "Sessiz Tüketim & Gösteri Toplumu" if lang == "tr" else "Passive Consumption & Spectacle Society"
        badge_color = "#8B0000"
        aciklama = (
            f"Yorum/İzlenme oranı düşük (%{cvr:.2f}), sessiz izleyici (lurker) oranı ise baskındır (%{lurker_ratio:.1f}). "
            f"Topluluk, içeriği asenkron tüketip ayrılan görünmez bir çoğunluktan oluşmaktadır. "
            f"Sosyo-teknik sürtünmeler ve tartışmalar kamusal alana taşınmamakta, bireysel bilişsel alanda kalmaktadır."
            if lang == "tr" else
            f"The Comment-to-View ratio is low (%{cvr:.2f}) and silent lurkers dominate (%{lurker_ratio:.1f}). "
            f"The audience consumes content asynchronously without leaving public traces; discussions remain within individual cognition rather than the public sphere."
        )

    return {
        "views": v,
        "likes": l,
        "comments": c,
        "cvr": round(cvr, 3),
        "lvr": round(lvr, 3),
        "lurker_ratio": round(lurker_ratio, 2),
        "tipoloji_key": tipoloji_key,
        "tipoloji_baslik": baslik,
        "badge_color": badge_color,
        "aciklama": aciklama,
        "nielsen": {
            "lurkers_pct": actual_lurker_pct,
            "intermittent_pct": actual_intermittent_pct,
            "creators_pct": actual_creator_pct
        },
        "teorik_referans": "Jakob Nielsen (2006) 90-9-1 Kuralı & Nonnecke & Preece (2000) Lurker Etnografisi" if lang == "tr" else "Jakob Nielsen (2006) 90-9-1 Rule & Nonnecke & Preece (2000) Lurker Ethnography"
    }
