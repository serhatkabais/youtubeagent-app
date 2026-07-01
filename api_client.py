# -*- coding: utf-8 -*-
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# API BAGLANTI TESTi
# ============================================================

def test_api_connection(provider, api_key, selected_model=None):
    """API baglantisini ve gecerlilgini test eder."""
    if not api_key:
        return False, None, "API anahtari bos olamaz."

    api_key = api_key.strip().strip('"').strip("'")

    try:
        if provider == "groq":
            url = "https://api.groq.com/openai/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                if selected_model:
                    return True, selected_model, f"Groq baglantisi basarili! Secilen model: {selected_model}"
                data = response.json()
                models = [m["id"] for m in data.get("data", [])]
                preferred = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"]
                selected_model = "llama-3.3-70b-versatile"
                for p in preferred:
                    if p in models:
                        selected_model = p
                        break
                return True, selected_model, f"Groq baglantisi basarili! Model: {selected_model}"
            else:
                return False, None, f"Groq API Hatasi (HTTP {response.status_code}): {response.text}"

        elif provider == "openrouter":
            url = "https://openrouter.ai/api/v1/models"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://localhost:8501",
                "X-Title": "Izleyici Iklimi Aynasi"
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                if selected_model:
                    return True, selected_model, f"OpenRouter baglantisi basarili! Secilen model: {selected_model}"
                data = response.json()
                models = [m["id"] for m in data.get("data", [])]
                free_models = [m for m in models if m.endswith(":free")]
                preferred_free = [
                    "meta-llama/llama-3.3-70b-instruct:free",
                    "qwen/qwen3-coder:free",
                    "google/gemma-4-31b-it:free",
                    "google/gemma-4-26b-a4b-it:free",
                    "meta-llama/llama-3.2-3b-instruct:free"
                ]
                selected_model = "meta-llama/llama-3.3-70b-instruct:free"
                for pf in preferred_free:
                    if pf in free_models:
                        selected_model = pf
                        break
                else:
                    if free_models:
                        selected_model = free_models[0]
                return True, selected_model, f"OpenRouter baglantisi basarili! Model: {selected_model}"
            else:
                return False, None, f"OpenRouter API Hatasi (HTTP {response.status_code}): {response.text}"

        elif provider == "gemini":
            if selected_model:
                test_url = f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent?key={api_key}"
                test_payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
                test_res = requests.post(test_url, json=test_payload, timeout=10)
                if test_res.status_code == 200:
                    return True, selected_model, f"Gemini baglantisi basarili! Secilen model: {selected_model}"
                else:
                    return False, None, f"Gemini API Hatasi (HTTP {test_res.status_code}): {test_res.text}"

            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [m["name"].replace("models/", "") for m in data.get("models", [])]
                preferred = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
                selected_model = "gemini-1.5-flash"
                for p in preferred:
                    if p in models:
                        selected_model = p
                        break
                return True, selected_model, f"Gemini baglantisi basarili! Model: {selected_model}"
            else:
                test_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                test_payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
                test_res = requests.post(test_url, json=test_payload, timeout=10)
                if test_res.status_code == 200:
                    return True, "gemini-1.5-flash", "Gemini baglantisi basarili! (varsayilan: gemini-1.5-flash)"
                else:
                    return False, None, f"Gemini API Hatasi (HTTP {test_res.status_code}): {test_res.text}"

    except Exception as e:
        return False, None, f"Baglanti hatasi: {str(e)}"

    return False, None, "Desteklenmeyen saglayici."


# ============================================================
# YENI KATEGORI VE ROL TAKSONOMILERI
# ============================================================

ANALYSIS_CATEGORIES = [
    "Heyecan ve Kesif Motivasyonu",
    "Mesleki Gelecek Kaygisi",
    "Etik ve Telif Hassasiyeti",
    "Teknik Sorun ve Destek Arayisi",
    "Maliyet ve Erisilebilirlik Sorunu",
    "Sosyal Destek ve Tesekkur",
    "Akran Mentorlugu ve Yonlendirme",
    "Yaratici Is Akisi Tartismasi",
    "Felsefi/Varolussal Sorgulama",
    "Ironi, Kinaye veya Sarkastik Yorum",
    "Icerik Talebi ve Oneri",
    "Genel Gozlem / Yuzeysel Katilim"
]

ANALYSIS_ROLES = [
    "Akran Mentoru",
    "Profesyonel Uygulayici",
    "Elestirel Dusunur",
    "Yeni Kesfeci / Merakli",
    "Hayal Kirikligi",
    "Pasif Destekci",
    "Ironik Gozlemci"
]


# ============================================================
# ORTAK LLM API CAGRI FONKSIYONU
# ============================================================

def _call_llm_api(provider, api_key, model, system_prompt, user_prompt, temperature=0.3):
    """Ortak LLM API cagri fonksiyonu."""
    api_key = api_key.strip().strip('"').strip("'")

    if provider in ("groq", "openrouter"):
        url = "https://api.groq.com/openai/v1/chat/completions" if provider == "groq" else "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        if provider == "openrouter":
            headers["HTTP-Referer"] = "https://localhost:8501"
            headers["X-Title"] = "Izleyici Iklimi Aynasi"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        res = requests.post(url, json=payload, headers=headers, timeout=90)
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"{provider.upper()} API Hatasi (HTTP {res.status_code}): {res.text[:500]}")

    elif provider == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": temperature}
        }
        res = requests.post(url, json=payload, timeout=90)
        if res.status_code == 200:
            res_json = res.json()
            if "candidates" in res_json and res_json["candidates"]:
                candidate = res_json["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"] and candidate["content"]["parts"]:
                    return candidate["content"]["parts"][0]["text"]
            raise Exception(f"Gemini API bos yanit dondurdu: {res.text[:500]}")
        else:
            raise Exception(f"Gemini API Hatasi (HTTP {res.status_code}): {res.text[:500]}")

    raise Exception(f"Desteklenmeyen saglayici: {provider}")


# ============================================================
# LLM JSON AYRISTIRICI
# ============================================================

def _parse_llm_json(raw_text):
    """LLM ciktisidan JSON dizisini ayristirir."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass
    return None


# ============================================================
# GELISMIS SYSTEM PROMPT - YORUM ANALIZI
# ============================================================

SYSTEM_PROMPT_ANALYSIS = """Sen, Turkce cevrimici topluluklarin dilini, kulturel kodlarini ve retorik kaliplarini derinlemesine cozumleyen bir Dijital Etnografi ve Soylem Analizi Uzmanisin.

## GOREV
Sana verilen YouTube yorumlarini tek tek analiz edecek ve her biri icin yapilandirilmis bir JSON ciktisi ureteceksin.

## KRITIK TALIMATLAR

### 1. Duygu Analizi (sentiment)
- "pozitif": Gercek olumlu duygu (sevinc, minnettarlik, heyecan)
- "negatif": Gercek olumsuz duygu (ofke, hayal kirikligi, korku)
- "notr": Bilgi aktarimi, soru sorma, tarafsiz gozlem
- "karisik": Ayni yorumda hem olumlu hem olumsuz duygu (Orn: "Arac super ama isimizi alacak")

### 2. Duygu Tonu (emotion)
heyecan, kaygi, hayal_kirikligi, minnettarlik, merak, ofke, ironi, korku, umut, hayret, bikkinlik, suphe, gurur, nostalji

### 3. Kategori Taksonomisi (category)
Asagidaki 12 kategoriden EN UYGUN olanini sec:
- "Heyecan ve Kesif Motivasyonu": Aractan/konudan heyecan duyan, denemek isteyen, olumlu saskinlik
- "Mesleki Gelecek Kaygisi": Is kaybi, sektor tehdidi, "biz ne yapacagiz", gelecek endisesi
- "Etik ve Telif Hassasiyeti": Emek hirsizligi, telif, izinsiz kullanim, akademik durustluk
- "Teknik Sorun ve Destek Arayisi": Hata, bug, "calismiyor", parametre sorunu, teknik soru
- "Maliyet ve Erisilebilirlik Sorunu": API maliyeti, ucretsiz alternatif arayisi, fiyat sikayeti
- "Sosyal Destek ve Tesekkur": Topluluk bagi, minnettarlik, takdir, tesekkur
- "Akran Mentorlugu ve Yonlendirme": Baskasinin sorusuna cevap veren, kaynak paylasan
- "Yaratici Is Akisi Tartismasi": Araclarin is akisina entegrasyonu, workflow, uretim sureci
- "Felsefi/Varolussal Sorgulama": YZ'nin dogasi, bilinc, insanlik gelecegi, derin dusunce
- "Ironi, Kinaye veya Sarkastik Yorum": Alayci, satirik, ustu kapali elestiri, sarkastik ovgu
- "Icerik Talebi ve Oneri": "Sunu da anlatsaniz", "devami gelsin", video onerisi
- "Genel Gozlem / Yuzeysel Katilim": Kisa, baglamsiz veya yuzeysel yorumlar ("ilk yorum", emoji)

### 4. Topluluk Rolu (role)
- "Akran Mentoru": Baskasina cevap veren, kaynak paylasan, cozum oneren
- "Profesyonel Uygulayici": Kendi is akisindan bahseden, deneyim paylasan
- "Elestirel Dusunur": Etik/felsefi sorgulayan, karsi arguman sunan
- "Yeni Kesfeci / Merakli": Denemeye hevesli, kesfetmek isteyen, sorular soran
- "Hayal Kirikligi": Teknik engelle karsilasanlar, maliyet sikayetcisi
- "Pasif Destekci": Kisa tesekkur/takdir, yuzeysel katilim
- "Ironik Gozlemci": Alayci/sarkastik perspektifle yorum yapan

### 5. Retorik Cihaz Algilama (rhetorical_devices)
Varsa su araclari tespit et:
- "ironi": Soylenenin tersini kasteden ifade
- "kinaye": Dolayli, ima yoluyla elestiri
- "abarti": Durumu oldugundan buyuk/kucuk gosterme
- "sarkastik_ovgu": Ovuyor gibi gorunup aslinda elestiren
- "retorik_soru": Cevap beklemeden dusundurmek icin sorulan soru
- "argo_kullanim": Gunluk konusma dili, sokak agzi
- "emoji_vurgu": Emojilerle anlam pekistirme veya ton belirtme

### 6. TURKCE INTERNET DILI BILGISI (COK ONEMLI!)
Su kaliplari dogru analiz et:
- "abi cok iyi ya" -> Samimi heyecan (pozitif)
- "abi cok iyi ya, resmen isimizi alacaklar" -> Karisik duygu (heyecan + kaygi + hafif ironi)
- "harika, artik calisana gerek yok" -> Ironi / sarkastik
- "vay be" -> Baglama gore hayret veya ironi olabilir
- "efsane", "muthis", "kral" -> Samimi ovgu (genellikle)
- "hocam eline saglik" -> Sosyal destek
- "yapay zeka sanati oldurecek" -> Mesleki kaygi (negatif)
- "bitti bu is" -> Baglama gore: ya umutsuzluk ya da "is tamam" anlaminda olumlu
- "@kullanici sunu dene" -> Akran mentorlugu
- "ilk yorum", sadece emoji -> Yuzeysel katilim

## CIKTI FORMATI
Her yorum icin asagidaki JSON yapisini kullan. Yanitin SADECE gecerli bir JSON dizisi olmali, baska metin olmamali:

[
  {
    "id": 1,
    "sentiment": "pozitif|negatif|notr|karisik",
    "emotion": "ana duygu",
    "category": "taksonomi kategorisi",
    "role": "topluluk rolu",
    "rhetorical_devices": ["tespit edilen cihazlar"],
    "confidence": 0.85,
    "reasoning": "Kisa Turkce aciklama"
  }
]"""


# ============================================================
# LLM-FIRST YORUM ANALIZI
# ============================================================

def analyze_comments_with_llm(comments, provider, api_key, model, progress_callback=None):
    """
    Yorumlari batch halinde LLM'e gondererek her biri icin yapilandirilmis
    analiz ciktisi alir. Ironi, kinaye, abarti gibi retorik cihazlari tespit eder.
    """
    if not api_key:
        raise Exception("API anahtari bulunamadi veya bos.")

    BATCH_SIZE = 8
    all_results = []
    total = len(comments)

    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch = comments[batch_start:batch_end]

        user_prompt = f"Asagidaki {len(batch)} YouTube yorumunu analiz et:\n\n"
        for i, c in enumerate(batch):
            # Escape strings just in case
            comment_text = c.get("comment", "").replace('"', "'")
            user_prompt += f'[{i+1}] "{comment_text}"\n'

        try:
            raw_response = _call_llm_api(provider, api_key, model, SYSTEM_PROMPT_ANALYSIS, user_prompt)
            parsed = _parse_llm_json(raw_response)

            if parsed and isinstance(parsed, list):
                for idx, result in enumerate(parsed):
                    if idx < len(batch):
                        result["original_id"] = batch[idx].get("id", batch_start + idx + 1)
                        result["original_comment"] = batch[idx].get("comment", "")
                        result.setdefault("sentiment", "notr")
                        result.setdefault("emotion", "belirsiz")
                        result.setdefault("category", "Genel Gozlem / Yuzeysel Katilim")
                        result.setdefault("role", "Pasif Destekci")
                        result.setdefault("rhetorical_devices", [])
                        result.setdefault("confidence", 0.5)
                        result.setdefault("reasoning", "")
                all_results.extend(parsed[:len(batch)])
            else:
                for idx, c in enumerate(batch):
                    all_results.append({
                        "original_id": c.get("id", batch_start + idx + 1),
                        "original_comment": c.get("comment", ""),
                        "sentiment": "notr",
                        "emotion": "belirsiz",
                        "category": "Genel Gozlem / Yuzeysel Katilim",
                        "role": "Pasif Destekci",
                        "rhetorical_devices": [],
                        "confidence": 0.0,
                        "reasoning": "LLM ciktisi ayristirilamadi."
                    })
        except Exception as e:
            raise Exception(f"Batch {batch_start+1}-{batch_end} analiz hatasi: {str(e)}")

        if progress_callback:
            progress_callback(batch_end / total)

    return all_results


# ============================================================
# LLM RAPOR URETICI
# ============================================================

def get_llm_report(meta, statistics, comments_sample, provider, api_key, model, llm_analysis_results=None):
    """
    LLM analiz sonuclarini sentezleyerek kapsamli bir etnografik rapor uretir.
    """
    if not api_key:
        raise Exception("API anahtari bulunamadi veya bos.")

    if llm_analysis_results:
        category_dist = {}
        role_dist = {}
        sentiment_dist = {}
        ironic_comments = []
        mixed_comments = []

        for r in llm_analysis_results:
            cat = r.get("category", "Diger")
            category_dist[cat] = category_dist.get(cat, 0) + 1
            role = r.get("role", "Diger")
            role_dist[role] = role_dist.get(role, 0) + 1
            sent = r.get("sentiment", "notr")
            sentiment_dist[sent] = sentiment_dist.get(sent, 0) + 1
            if "ironi" in r.get("rhetorical_devices", []) or "kinaye" in r.get("rhetorical_devices", []):
                ironic_comments.append(r)
            if sent == "karisik":
                mixed_comments.append(r)

        sorted_results = sorted(llm_analysis_results, key=lambda x: x.get("confidence", 0), reverse=True)
        interesting_examples = []
        seen_cats = set()
        for r in sorted_results:
            cat = r.get("category", "")
            if cat not in seen_cats or len(interesting_examples) < 5:
                interesting_examples.append(r)
                seen_cats.add(cat)
            if len(interesting_examples) >= 15:
                break

        prompt = f"Asagidaki YouTube videosu altindaki {statistics.get('total')} yorumun yapay zeka destekli derinlemesine analizini sentezleyerek akademik tonda Turkce bir rapor yaz.\n\n"
        prompt += f"## VIDEO BILGILERI\n- Baslik: {meta.get('title')}\n- Yayinci: {meta.get('uploader')}\n- Izlenme: {meta.get('views')}\n\n"
        prompt += f"## LLM ANALIZ SONUCLARI\n\n### Duygu Dagilimi:\n{json.dumps(sentiment_dist, ensure_ascii=False, indent=2)}\n\n"
        prompt += f"### Kategori Dagilimi:\n{json.dumps(category_dist, ensure_ascii=False, indent=2)}\n\n"
        prompt += f"### Topluluk Rolu Dagilimi:\n{json.dumps(role_dist, ensure_ascii=False, indent=2)}\n\n"

        if ironic_comments:
            prompt += f"### Ironi/Kinaye Iceren Yorumlar ({len(ironic_comments)} adet):\n"
            for ic in ironic_comments[:5]:
                prompt += f'- "{ic.get("original_comment", "")[:120]}" -> {ic.get("reasoning", "")}\n'
            prompt += "\n"

        if mixed_comments:
            prompt += f"### Karisik Duygulu Yorumlar ({len(mixed_comments)} adet):\n"
            for mc in mixed_comments[:5]:
                prompt += f'- "{mc.get("original_comment", "")[:120]}" -> {mc.get("reasoning", "")}\n'
            prompt += "\n"

        prompt += "### Dikkat Cekici Yorum Ornekleri:\n"
        for ex in interesting_examples[:10]:
            prompt += f'- [{ex.get("category")}] [{ex.get("sentiment")}] "{ex.get("original_comment", "")[:120]}" -> {ex.get("reasoning", "")}\n'

        prompt += f"""

## RAPOR TALIMATLARI

Lutfen bu verileri sentezleyerek su basliklari iceren zengin, derinlemesine, akademik tonda bir Turkce rapor yaz:

### Topluluk Profili ve Genel Duygu Haritasi
Duygu dagilimini yorumla. Pozitif/negatif/karisik oranlarini degerlendir. Toplulugun genel atmosferini tanimla.

### Tematik Analiz ve Kategori Degerlendirmesi
Hangi temalar baskin? Kategori dagiliminden ne tur bir topluluk profili cikiyor? Baskin kaygilar ve motivasyonlar neler?

### Retorik ve Alt-Metin Analizi
Ironi, kinaye ve sarkastik yorumlari ayrintili degerlendir. Bu retorik araclar toplulugun gercek duygularini nasil maskeliyor?

### Topluluk Dinamikleri ve Rol Yapilanmasi
Akran mentorlugu orani ne durumda? Elestirel dusunurler mi yoksa pasif destekciler mi baskin?

### Icerik Ureticileri ve Arastirmacilar Icin Yol Haritasi
Somut, uygulanabilir mudahale onerileri sun.

En sona su etik uyariyi ekle:
> **Degerlendirme ve Etik Sinir Uyarisi:** Bu rapor, cevrimici toplulugun dil jargonlari ve davranissal ayak izlerinin yapay zeka destekli otomatik analizi ile uretilmistir. Bu veriler kesin birer hukum teskil etmez.
"""
    else:
        prompt = f"Sen bir Cevrimici Izleyici Topluluklari Iklim ve Jargon Cozumleyicisisin.\n"
        prompt += f"Asagidaki video ve topluluk istatistiklerine gore derinlemesine nitel bir izleyici ve siber-kulturel iklim degerlendirmesi raporu yaz.\n\n"
        prompt += f"VIDEO BILGILERI:\n- Baslik: {meta.get('title')}\n- Yayinci: {meta.get('uploader')}\n- Izlenme: {meta.get('views')}\n\n"
        prompt += f"SAYISAL ISTATISTIKLER:\n"
        prompt += f"- Toplam Analiz Edilen Yorum: {statistics.get('total')}\n"
        prompt += f"- Kulturel Kaygi Orani: %{statistics.get('kaygi', 0):.1f}\n"
        prompt += f"- Akran Mentorlugu Orani: %{statistics.get('mentor', 0):.1f}\n"
        prompt += f"- Motivasyon/Cosku Orani: %{statistics.get('cosku', 0):.1f}\n"
        prompt += f"- Teknik Tikanma/Hata Orani: %{statistics.get('hata', 0):.1f}\n"
        prompt += f"- Elestirel Suphecilik Orani: %{statistics.get('etik', 0):.1f}\n"
        prompt += f"- Sosyal Destek/Tesekkur Orani: %{statistics.get('destek', 0):.1f}\n"
        prompt += f"- Topluluk Indeksi: {statistics.get('indeks')}\n\n"
        prompt += "YORUM ORNEKLERI:\n"
        for c in comments_sample[:15]:
            prompt += f"- {c.get('comment', '')}\n"
        prompt += "\nLutfen bu verileri sentezleyerek zengin, akademik tonda Turkce bir rapor yaz.\n"

    try:
        system_msg = "Sen bir Dijital Etnografi ve Soylem Analizi Uzmanisin. Turkce akademik tonda yazarsin."
        return _call_llm_api(provider, api_key, model, system_msg, prompt, temperature=0.5)
    except Exception as e:
        raise Exception(f"Rapor uretim hatasi ({provider}): {str(e)}")


# ============================================================
# DINAMIK MODEL SORGULAMA
# ============================================================

def get_available_gemini_models(api_key):
    if not api_key:
        return []
    api_key = api_key.strip().strip('"').strip("'")
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = []
            for m in data.get("models", []):
                name = m.get("name", "").replace("models/", "")
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    models.append(name)
            return sorted(list(set(models)))
    except Exception as e:
        print(f"Error fetching Gemini models: {e}")
    return []


def get_available_groq_models(api_key):
    if not api_key:
        return []
    api_key = api_key.strip().strip('"').strip("'")
    try:
        url = "https://api.groq.com/openai/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = [m["id"] for m in data.get("data", [])]
            return sorted(models)
    except Exception as e:
        print(f"Error fetching Groq models: {e}")
    return []


def get_available_openrouter_models(api_key):
    if not api_key:
        return []
    api_key = api_key.strip().strip('"').strip("'")
    try:
        url = "https://openrouter.ai/api/v1/models"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://localhost:8501",
            "X-Title": "Izleyici Iklimi Aynasi"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = [m["id"] for m in data.get("data", [])]
            return sorted(models)
    except Exception as e:
        print(f"Error fetching OpenRouter models: {e}")
    return []

# ============================================================
# MULTI-LLM MUTABAKAT VE AKADEMİK GÜVENİLİRLİK (FLEISS' KAPPA)
# ============================================================

from concurrent.futures import ThreadPoolExecutor

def calculate_fleiss_kappa(ratings_matrix):
    """
    Fleiss' Kappa katsayısını hesaplar.
    ratings_matrix: Her bir satırı gözlemci oyları olan liste. (Örn: [['pozitif', 'pozitif', 'negatif'], ...])
    """
    N = len(ratings_matrix)
    if N == 0:
        return 0.0
    n = 3 # 3 rater/model
    
    # Tüm benzersiz kategorileri al
    categories = list(set(val for row in ratings_matrix for val in row))
    k = len(categories)
    if k <= 1:
        return 1.0 # Tek kategori varsa tam uyuşum
        
    counts = []
    for row in ratings_matrix:
        row_counts = {cat: 0 for cat in categories}
        for val in row:
            row_counts[val] += 1
        counts.append(row_counts)
        
    P_i_list = []
    for i in range(N):
        sum_sq = sum(c**2 for c in counts[i].values())
        P_i = (sum_sq - n) / (n * (n - 1))
        P_i_list.append(P_i)
        
    P_mean = sum(P_i_list) / N
    
    p_j_list = []
    for cat in categories:
        sum_cat = sum(counts[i][cat] for i in range(N))
        p_j = sum_cat / (N * n)
        p_j_list.append(p_j)
        
    P_e = sum(p**2 for p in p_j_list)
    
    if P_e == 1.0:
        return 0.0
        
    kappa = (P_mean - P_e) / (1.0 - P_e)
    return kappa

def interpret_kappa(kappa):
    """Kappa skorunun akademik yorumunu döner."""
    if kappa < 0:
        return "Uyuşma Yok / Rastgele"
    elif kappa <= 0.20:
        return "Önemsiz Derecede Uyuşum (Slight Agreement)"
    elif kappa <= 0.40:
        return "Kabul Edilebilir Derecede Uyuşum (Fair Agreement)"
    elif kappa <= 0.60:
        return "Orta Derecede Uyuşum (Moderate Agreement)"
    elif kappa <= 0.80:
        return "Önemli Derecede Uyuşum (Substantial Agreement)"
    else:
        return "Neredeyse Mükemmel Uyuşum (Almost Perfect Agreement)"

def _get_consensus_value(val1, val2, val3):
    """En az 2 oy alan değeri ve kaç oy aldığını döner."""
    from collections import Counter
    counts = Counter([val1, val2, val3])
    most_common = counts.most_common(1)[0]
    if most_common[1] >= 2:
        return most_common[0], most_common[1]
    else:
        return val1, 1 # uyuşmazlık durumunda birincil modelin tahmini, 1 oy

def analyze_comments_with_llm_consensus(comments, provider, api_key, models, progress_callback=None):
    """
    3 farklı modelle yorumları paralel analiz eder ve çoğunluk kararına göre birleştirir.
    models: list of 3 model names.
    """
    if len(models) < 3:
        raise Exception("Mutabakat analizi için en az 3 model gereklidir.")

    results = {}
    progress_states = {models[0]: 0.0, models[1]: 0.0, models[2]: 0.0}
    
    def get_progress_wrapper(model_name):
        def cb(progress):
            progress_states[model_name] = progress
            if progress_callback:
                avg_progress = sum(progress_states.values()) / 3.0
                progress_callback(avg_progress)
        return cb

    def run_analysis(model_name):
        return analyze_comments_with_llm(
            comments, provider, api_key, model_name, get_progress_wrapper(model_name)
        )

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(run_analysis, m): m for m in models}
        for future in futures:
            model_name = futures[future]
            try:
                results[model_name] = future.result()
            except Exception as e:
                raise Exception(f"Model {model_name} analiz sırasında hata verdi: {str(e)}")

    m1_results = results[models[0]]
    m2_results = results[models[1]]
    m3_results = results[models[2]]

    consensus_results = []
    ratings_sentiment = []
    ratings_category = []
    ratings_role = []

    for i in range(len(comments)):
        c1 = m1_results[i]
        c2 = m2_results[i]
        c3 = m3_results[i]

        sent_val, sent_votes = _get_consensus_value(c1["sentiment"], c2["sentiment"], c3["sentiment"])
        cat_val, cat_votes = _get_consensus_value(c1["category"], c2["category"], c3["category"])
        role_val, role_votes = _get_consensus_value(c1["role"], c2["role"], c3["role"])

        ratings_sentiment.append([c1["sentiment"], c2["sentiment"], c3["sentiment"]])
        ratings_category.append([c1["category"], c2["category"], c3["category"]])
        ratings_role.append([c1["role"], c2["role"], c3["role"]])

        min_votes = min(sent_votes, cat_votes, role_votes)
        if sent_votes == 3 and cat_votes == 3 and role_votes == 3:
            agreement_level = "Tam Mutabakat"
        elif min_votes == 1:
            agreement_level = "Uyuşmazlık"
        else:
            agreement_level = "Çoğunluk Kararı"

        consensus_results.append({
            "original_id": c1["original_id"],
            "original_comment": c1["original_comment"],
            "sentiment": sent_val,
            "emotion": c1.get("emotion", "belirsiz"),
            "category": cat_val,
            "role": role_val,
            "rhetorical_devices": list(set(c1.get("rhetorical_devices", []) + c2.get("rhetorical_devices", []) + c3.get("rhetorical_devices", []))),
            "confidence": round((sent_votes + cat_votes + role_votes) / 9.0, 2),
            "reasoning": f"Modeller arası mutabakat: {agreement_level}. Birincil Model Gerekçesi: {c1.get('reasoning', '')}",
            "consensus_details": {
                "agreement_level": agreement_level,
                "votes": {
                    "sentiment": {models[0]: c1["sentiment"], models[1]: c2["sentiment"], models[2]: c3["sentiment"]},
                    "category": {models[0]: c1["category"], models[1]: c2["category"], models[2]: c3["category"]},
                    "role": {models[0]: c1["role"], models[1]: c2["role"], models[2]: c3["role"]}
                }
            }
        })

    kappa_sent = calculate_fleiss_kappa(ratings_sentiment)
    kappa_cat = calculate_fleiss_kappa(ratings_category)
    kappa_role = calculate_fleiss_kappa(ratings_role)

    consensus_count = sum(1 for r in consensus_results if r["consensus_details"]["agreement_level"] in ["Tam Mutabakat", "Çoğunluk Kararı"])
    consensus_rate = (consensus_count / len(comments)) * 100 if len(comments) > 0 else 0.0

    stats = {
        "fleiss_kappa_sentiment": round(kappa_sent, 3),
        "fleiss_kappa_category": round(kappa_cat, 3),
        "fleiss_kappa_role": round(kappa_role, 3),
        "fleiss_kappa_sentiment_text": interpret_kappa(kappa_sent),
        "fleiss_kappa_category_text": interpret_kappa(kappa_cat),
        "fleiss_kappa_role_text": interpret_kappa(kappa_role),
        "consensus_rate": round(consensus_rate, 1)
    }

    return consensus_results, stats
