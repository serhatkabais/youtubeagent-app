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
                chat_models = [m for m in models if not m.startswith("whisper") and "guard" not in m]
                preferred = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b", "qwen/qwen3.6-27b", "llama-3.3-70b-versatile"]
                selected_model = chat_models[0] if chat_models else (models[0] if models else "openai/gpt-oss-120b")
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
        MAX_RETRIES = 3
        RETRY_DELAYS = [5, 15, 30]  # saniye
        last_error = None
        
        for attempt in range(MAX_RETRIES + 1):
            res = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if res.status_code == 200:
                try:
                    res_json = res.json()
                except Exception:
                    raise Exception(f"{provider.upper()} API (HTTP 200) HTML/Metin dondurdu (Beklenen JSON degil): {repr(res.text[:300])}")
                    
                if "error" in res_json:
                    err_val = res_json["error"]
                    err_msg = err_val.get("message", str(err_val)) if isinstance(err_val, dict) else str(err_val)
                    err_code = err_val.get("code", 0) if isinstance(err_val, dict) else 0
                    # Retry on rate limit errors embedded in 200 responses
                    if err_code in (429, 502, 503) and attempt < MAX_RETRIES:
                        import time
                        time.sleep(RETRY_DELAYS[attempt])
                        continue
                    raise Exception(f"{provider.upper()} API Hatasi: {err_msg}")
                    
                if "choices" in res_json and len(res_json["choices"]) > 0:
                    return res_json["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"{provider.upper()} API beklenen formati ('choices') dondurmedi. Yanit: {repr(res.text[:300])}")
            
            elif res.status_code in (429, 502, 503):
                last_error = f"{provider.upper()} API Hatasi (HTTP {res.status_code}): {repr(res.text[:300])}"
                if attempt < MAX_RETRIES:
                    import time
                    time.sleep(RETRY_DELAYS[attempt])
                    continue
                else:
                    raise Exception(f"{last_error} (3 deneme sonrasi basarisiz)")
            else:
                raise Exception(f"{provider.upper()} API Hatasi (HTTP {res.status_code}): {repr(res.text[:300])}")

    elif provider == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": temperature}
        }
        res = requests.post(url, json=payload, timeout=120)
        if res.status_code == 200:
            try:
                res_json = res.json()
            except Exception:
                raise Exception(f"Gemini API (HTTP 200) HTML/Metin dondurdu: {repr(res.text[:300])}")
            if "candidates" in res_json and res_json["candidates"]:
                candidate = res_json["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"] and candidate["content"]["parts"]:
                    return candidate["content"]["parts"][0]["text"]
            raise Exception(f"Gemini API bos yanit dondurdu: {repr(res.text[:300])}")
        else:
            raise Exception(f"Gemini API Hatasi (HTTP {res.status_code}): {repr(res.text[:300])}")

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

SYSTEM_PROMPT_ANALYSIS_TR = """Sen, Turkce cevrimici topluluklarin dilini, kulturel kodlarini ve retorik kaliplarini derinlemesine cozumleyen bir Dijital Etnografi ve Soylem Analizi Uzmanisin.

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

### 4. Etnografik Topluluk Rolu (role - Kozinets Netnografik Tipolojisi)
- "Icerideki / Akran Mentoru": Baskasina cevap veren, kaynak paylasan, teknik/pedagojik cozum oneren (Kozinets Insider)
- "Tutkulu / Uretici Izleyici": Kendi is akisindan bahseden, teknolojiye ve uretime odakli, arac deneyen (Kozinets Devotee)
- "Elestirel Dusunur": Etik/felsefi boyutlari sorgulayan, karsi arguman ve alternatif perspektif sunan
- "Sosyallesen / Topluluk Destekcisi": Topluluk aidiyeti gosteren, samimi tesekkur eden, duygusal bag kuran (Kozinets Mingler)
- "Turist / Pasif Destekci": Kisa takdir, tek kelimelik veya emoji iceren yuzeysel periferal katilim (Kozinets Tourist)
- "Ironik Gozlemci": Alayci/sarkastik veya kinayeli perspektifle elestiren

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

### 7. DIL TESPITI VE CEVIRI (COK ONEMLI!)
- Her yorumun yazildigi orijinal dili tespit et ve "original_lang" alaninda ISO kodu olarak belirt (Orn: "tr", "en", "es", "de").
- Eger yorumun orijinal dili Turkce degilse, "translated_comment" alanina yorumun Turkce cevirisini yaz.
- Eger yorum zaten Turkce ise, "translated_comment" alanini bos birak veya orijinal yorumu aynen yaz.

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
    "reasoning": "Kisa Turkce aciklama",
    "original_lang": "tr|en|es|...",
    "translated_comment": "Orijinal yorum Turkce degilse Turkce cevirisi"
  }
]"""

SYSTEM_PROMPT_ANALYSIS_EN = """You are a Digital Ethnography and Discourse Analysis Expert analyzing online communities' language, cultural codes, and rhetorical patterns.

## TASK
You will analyze each YouTube comment provided and produce a structured JSON output for each.

## CRITICAL INSTRUCTIONS

### 1. Sentiment Analysis (sentiment)
- "positive": Real positive sentiment (joy, gratitude, excitement)
- "negative": Real negative sentiment (anger, disappointment, fear)
- "neutral": Information sharing, asking questions, objective observation
- "mixed": Both positive and negative sentiment in the same comment (e.g., "The tool is great but it will take our jobs")

### 2. Emotional Tone (emotion)
excitement, anxiety, disappointment, gratitude, curiosity, anger, irony, fear, hope, astonishment, weariness, skepticism, pride, nostalgia

### 3. Category Taxonomy (category)
Select the MOST APPROPRIATE from the following 12 categories:
- "Excitement and Discovery Motivation": Excitement about the tool/topic, eager to try, positive surprise
- "Professional Future Anxiety": Job loss, industry threat, "what will we do", future worry
- "Ethic and Copyright Sensitivity": Theft of labor, copyright, unauthorized use, academic integrity
- "Technical Issue and Support Seeking": Error, bug, "not working", parameter issue, technical question
- "Cost and Accessibility Issue": API cost, search for free alternatives, price complaint
- "Social Support and Gratitude": Community bond, gratitude, appreciation, thanks, "good job"
- "Peer Mentorship and Guidance": Answering others' questions, sharing resources
- "Creative Workflow Discussion": Integration of tools into workflow, production process
- "Philosophical/Existential Inquiries": Nature of AI, consciousness, future of humanity, deep thoughts
- "Irony, Satire or Sarcastic Comment": Mocking, satirical, implicit criticism, sarcastic praise
- "Content Request and Suggestion": "Please cover this too", "keep it coming", video suggestions
- "General Observation / Superficial Engagement": Short, out of context or superficial comments ("first comment", emoji)

### 4. Community Role (role)
- "Peer Mentor": Answering others, sharing resources, suggesting solutions
- "Professional Practitioner": Talking about their own workflow, sharing experience
- "Critical Thinker": Questioning ethical/philosophical aspects, presenting counter-arguments
- "New Explorer / Curious": Eager to try, wanting to discover, asking questions
- "Disappointed": Facing technical obstacles, complaining about cost
- "Passive Supporter": Short thanks/appreciation, superficial participation
- "Ironic Observer": Commenting with a mocking/sarcastic perspective

### 5. Rhetorical Device Detection (rhetorical_devices)
Detect any of the following if present:
- "irony": Expression conveying the opposite of the literal meaning
- "innuendo": Indirect, implicative criticism
- "hyperbole": Exaggeration or understatement of the situation
- "sarcastic_praise": Seeming to praise but actually criticizing
- "rhetorical_question": Question asked to provoke thought without expecting an answer
- "slang_use": Everyday colloquial speech, street talk
- "emoji_emphasis": Using emoticons to reinforce meaning or tone

### 6. INTERNET LANGUAGE KNOWLEDGE (VERY IMPORTANT!)
Understand specific Turkish/English internet slangs and idioms correctly:
- "abi cok iyi ya" or "bro this is so good" -> Genuine excitement (positive)
- "resmen isimizi alacaklar" or "they are taking our jobs" -> Professional anxiety (negative)
- "harika, artik calisana gerek yok" or "great, no need for workers anymore" -> Irony / sarcasm
- "hocam eline saglik" or "thanks for your effort" -> Social support
- "@username try this" -> Peer mentorship
- "first comment", just emojis -> Superficial engagement

### 7. LANGUAGE DETECTION AND TRANSLATION (VERY IMPORTANT!)
- Detect each comment's original language and write it in the "original_lang" field as an ISO code (e.g., "tr", "en", "es", "de").
- If the original language of the comment does NOT match English, provide a translation in English in the "translated_comment" field.
- If the comment is already in English, you can leave "translated_comment" empty or copy the original comment.

## OUTPUT FORMAT
Use the following JSON structure for each comment. Your response must be ONLY a valid JSON array, nothing else:

[
  {
    "id": 1,
    "sentiment": "positive|negative|neutral|mixed",
    "emotion": "main emotion",
    "category": "taksonomi category",
    "role": "community role",
    "rhetorical_devices": ["detected devices"],
    "confidence": 0.85,
    "reasoning": "Short English explanation",
    "original_lang": "tr|en|es|...",
    "translated_comment": "English translation if original comment is not in English"
  }
]"""


# ============================================================
# LLM-FIRST YORUM ANALIZI
# ============================================================

def analyze_comments_with_llm(comments, provider, api_key, model, progress_callback=None, lang="tr"):
    """
    Yorumlari batch halinde LLM'e gondererek her biri icin yapilandirilmis
    analiz ciktisi alir. Ironi, kinaye, abarti gibi retorik cihazlari tespit eder.
    Dil tespiti ve hedef dile (lang) gore ceviri yapar.
    """
    if not api_key:
        raise Exception("API anahtari bulunamadi veya bos.")

    BATCH_SIZE = 8
    all_results = []
    total = len(comments)
    system_prompt = SYSTEM_PROMPT_ANALYSIS_TR if lang == "tr" else SYSTEM_PROMPT_ANALYSIS_EN

    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch = comments[batch_start:batch_end]

        user_prompt = f"Asagidaki {len(batch)} YouTube yorumunu analiz et:\n\n" if lang == "tr" else f"Analyze the following {len(batch)} YouTube comments:\n\n"
        for i, c in enumerate(batch):
            comment_text = c.get("comment", "").replace('"', "'")
            user_prompt += f'[{i+1}] "{comment_text}"\n'

        try:
            raw_response = _call_llm_api(provider, api_key, model, system_prompt, user_prompt)
            parsed = _parse_llm_json(raw_response)

            if parsed and isinstance(parsed, list):
                for idx, result in enumerate(parsed):
                    if idx < len(batch):
                        result["original_id"] = batch[idx].get("id", batch_start + idx + 1)
                        result["original_comment"] = batch[idx].get("comment", "")
                        result.setdefault("sentiment", "notr" if lang == "tr" else "neutral")
                        result.setdefault("emotion", "belirsiz" if lang == "tr" else "undetermined")
                        result.setdefault("category", "Genel Gozlem / Yuzeysel Katilim" if lang == "tr" else "General Observation / Superficial Engagement")
                        result.setdefault("role", "Pasif Destekci" if lang == "tr" else "Passive Supporter")
                        result.setdefault("rhetorical_devices", [])
                        result.setdefault("confidence", 0.5)
                        result.setdefault("reasoning", "")
                        result.setdefault("original_lang", "tr" if lang == "tr" else "en")
                        result.setdefault("translated_comment", "")
                all_results.extend(parsed[:len(batch)])
            else:
                for idx, c in enumerate(batch):
                    all_results.append({
                        "original_id": c.get("id", batch_start + idx + 1),
                        "original_comment": c.get("comment", ""),
                        "sentiment": "notr" if lang == "tr" else "neutral",
                        "emotion": "belirsiz" if lang == "tr" else "undetermined",
                        "category": "Genel Gozlem / Yuzeysel Katilim" if lang == "tr" else "General Observation / Superficial Engagement",
                        "role": "Pasif Destekci" if lang == "tr" else "Passive Supporter",
                        "rhetorical_devices": [],
                        "confidence": 0.0,
                        "reasoning": "LLM ciktisi ayristirilamadi." if lang == "tr" else "LLM output could not be parsed.",
                        "original_lang": "tr" if lang == "tr" else "en",
                        "translated_comment": ""
                    })
        except Exception as e:
            raise Exception(f"Batch {batch_start+1}-{batch_end} analiz hatasi: {str(e)}")

        if progress_callback:
            progress_callback(batch_end / total)

    return all_results


# ============================================================
# LLM RAPOR URETICI
# ============================================================

def get_llm_report(meta, statistics, comments_sample, provider, api_key, model, llm_analysis_results=None, lang="tr"):
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
            cat = r.get("category", "Diger" if lang == "tr" else "Other")
            category_dist[cat] = category_dist.get(cat, 0) + 1
            role = r.get("role", "Diger" if lang == "tr" else "Other")
            role_dist[role] = role_dist.get(role, 0) + 1
            sent = r.get("sentiment", "notr" if lang == "tr" else "neutral")
            sentiment_dist[sent] = sentiment_dist.get(sent, 0) + 1
            rhet = r.get("rhetorical_devices", [])
            if any(x in rhet for x in ["ironi", "kinaye", "ironic", "sarcastic", "irony"]):
                ironic_comments.append(r)
            if sent in ("karisik", "mixed"):
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

        if lang == "tr":
            prompt = f"Asagidaki YouTube videosu altindaki {statistics.get('total')} yorumun yapay zeka destekli derinlemesine analizini sentezleyerek akademik tonda Turkce bir rapor yaz.\n\n"
            prompt += f"## VIDEO BILGILERI\n- Baslik: {meta.get('title')}\n- Yayinci: {meta.get('uploader')}\n- Izlenme: {meta.get('views')}\n"
            if statistics.get("sessiz_cogunluk"):
                sc = statistics["sessiz_cogunluk"]
                prompt += f"- Yorum/İzlenme Oranı (CVR): %{sc.get('cvr')}\n- Beğeni/İzlenme Oranı (LVR): %{sc.get('lvr')}\n- Sessiz Kitle (Lurker) Oranı: %{sc.get('lurker_ratio')}\n- Topluluk Canlılık Tipolojisi: {sc.get('tipoloji_baslik')}\n"
            prompt += "\n"
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

### Görünmez Kitle ve Katılım Eşitsizliği (Sessiz Çoğunluk / Lurkers & 90-9-1 Kuralı)
İzlenme, beğeni ve yorum oranlarını (CVR/LVR), Nielsen'in 90-9-1 katılım eşitsizliği ve Nonnecke & Preece'in Lurker kuramı çerçevesinde yorumla. Topluluktaki sessiz çoğunluğun bilişsel rolünü (Lave & Wenger meşru çevresel katılım) açıkla.

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
            prompt = f"Write an academic, deep qualitative ethnographic synthesis report in English, analyzing the {statistics.get('total')} YouTube comments under the video described below.\n\n"
            prompt += f"## VIDEO METADATA\n- Title: {meta.get('title')}\n- Publisher: {meta.get('uploader')}\n- Views: {meta.get('views')}\n"
            if statistics.get("sessiz_cogunluk"):
                sc = statistics["sessiz_cogunluk"]
                prompt += f"- Comment-to-View Ratio (CVR): %{sc.get('cvr')}\n- Like-to-View Ratio (LVR): %{sc.get('lvr')}\n- Silent Audience (Lurker) Ratio: %{sc.get('lurker_ratio')}\n- Community Vitality Typology: {sc.get('tipoloji_baslik')}\n"
            prompt += "\n"
            prompt += f"## LLM ANALYSIS STATISTICS\n\n### Sentiment Distribution:\n{json.dumps(sentiment_dist, ensure_ascii=False, indent=2)}\n\n"
            prompt += f"### Category Distribution:\n{json.dumps(category_dist, ensure_ascii=False, indent=2)}\n\n"
            prompt += f"### Community Role Distribution:\n{json.dumps(role_dist, ensure_ascii=False, indent=2)}\n\n"

            if ironic_comments:
                prompt += f"### Comments with Irony/Sarcasm ({len(ironic_comments)} items):\n"
                for ic in ironic_comments[:5]:
                    prompt += f'- "{ic.get("original_comment", "")[:120]}" -> {ic.get("reasoning", "")}\n'
                prompt += "\n"

            if mixed_comments:
                prompt += f"### Comments with Mixed Sentiment ({len(mixed_comments)} items):\n"
                for mc in mixed_comments[:5]:
                    prompt += f'- "{mc.get("original_comment", "")[:120]}" -> {mc.get("reasoning", "")}\n'
                prompt += "\n"

            prompt += "### Notable Comment Examples:\n"
            for ex in interesting_examples[:10]:
                prompt += f'- [{ex.get("category")}] [{ex.get("sentiment")}] "{ex.get("original_comment", "")[:120]}" -> {ex.get("reasoning", "")}\n'

            prompt += f"""
## REPORT INSTRUCTIONS

Please synthesize this data and write a rich, deep, academic-toned report in English containing the following headings:

### Community Profile and General Emotion Map
Interpret the sentiment distribution. Evaluate positive/negative/mixed ratios. Describe the general atmosphere of the community.

### The Silent Majority & Participation Inequality (Lurkers & 90-9-1 Rule)
Interpret the Comment-to-View (CVR) and Like-to-View (LVR) ratios within the framework of Jakob Nielsen's 90-9-1 rule and Nonnecke & Preece's Lurker theory. Explain the legitimate peripheral participation (Lave & Wenger) of the silent audience.

### Thematic Analysis and Category Evaluation
Which themes are dominant? What kind of community profile emerges from the category distribution? What are the dominant anxieties and motivations?

### Rhetorical and Subtext Analysis
Analyze comments with irony, sarcasm, and implicit subtext in detail. How do these rhetorical devices mask the community's authentic sentiments?

### Community Dynamics and Role Structure
What is the peer mentorship rate? Do critical thinkers or passive supporters dominate?

### Roadmap for Content Creators and Researchers
Provide concrete, actionable intervention recommendations.

Add the following ethical warning at the very end:
> **Evaluation and Ethical Boundaries Warning:** This report has been generated using AI-assisted automated analysis of online community jargon and behavioral footprints. These data do not constitute a definitive judgment.
"""
    else:
        if lang == "tr":
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
        else:
            prompt = f"You are an Online Audience Communities Climate and Jargon Analyzer.\n"
            prompt += f"Write an in-depth qualitative audience and cyber-cultural climate evaluation report in English based on the video and community statistics below.\n\n"
            prompt += f"VIDEO INFORMATION:\n- Title: {meta.get('title')}\n- Publisher: {meta.get('uploader')}\n- Views: {meta.get('views')}\n\n"
            prompt += f"NUMERICAL STATISTICS:\n"
            prompt += f"- Total Comments Analyzed: {statistics.get('total')}\n"
            prompt += f"- Cultural Anxiety Ratio: %{statistics.get('kaygi', 0):.1f}\n"
            prompt += f"- Peer Mentorship Ratio: %{statistics.get('mentor', 0):.1f}\n"
            prompt += f"- Motivation/Discovery Ratio: %{statistics.get('cosku', 0):.1f}\n"
            prompt += f"- Technical Blocker/Error Ratio: %{statistics.get('hata', 0):.1f}\n"
            prompt += f"- Critical Skepticism Ratio: %{statistics.get('etik', 0):.1f}\n"
            prompt += f"- Social Support/Gratitude Ratio: %{statistics.get('destek', 0):.1f}\n"
            prompt += f"- Community Index: {statistics.get('indeks')}\n\n"
            prompt += "COMMENT EXAMPLES:\n"
            for c in comments_sample[:15]:
                prompt += f"- {c.get('comment', '')}\n"
            prompt += "\nPlease synthesize this data and write a rich, academic-toned report in English.\n"

    try:
        system_msg = "Sen bir Dijital Etnografi ve Soylem Analizi Uzmanisin. Turkce akademik tonda yazarsin." if lang == "tr" else "You are a Digital Ethnography and Discourse Analysis Expert. You write in a professional academic English tone."
        return _call_llm_api(provider, api_key, model, system_msg, prompt, temperature=0.5)
    except Exception as e:
        raise Exception(f"Rapor uretim hatasi ({provider}): {str(e)}" if lang == "tr" else f"Report generation error ({provider}): {str(e)}")


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


def get_available_openrouter_models(api_key, detailed=False):
    """
    OpenRouter API'sinden anlik modelleri ceker.
    Ucretsiz modelleri [FREE] etiketiyle, ucretli modelleri ise 1M prompt jetonu basina 
    USD maliyetine gore en ucuzdan en pahaliya dogru siralayarak dondurur.
    detailed=True ise {'free': [...], 'paid': [...], 'all': [...]} seklinde yapilandirilmis sozluk doner.
    """
    if not api_key:
        return {"free": [], "paid": [], "all": []} if detailed else []
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
            data = response.json().get("data", [])
            free_list = []
            paid_list = []
            
            for m in data:
                mid = m.get("id", "")
                pricing = m.get("pricing", {}) or {}
                try:
                    p_prompt = float(pricing.get("prompt") or 0)
                    p_comp = float(pricing.get("completion") or 0)
                except Exception:
                    p_prompt = 0.0
                    p_comp = 0.0
                
                p_1m = round(p_prompt * 1_000_000, 3)
                is_free = mid.endswith(":free") or (p_prompt == 0 and p_comp == 0)
                
                if is_free:
                    free_list.append(f"[FREE] {mid}")
                else:
                    if p_1m >= 0.01:
                        price_str = f"${p_1m:.2f}/1M"
                    elif p_1m > 0:
                        price_str = f"${p_1m:.3f}/1M"
                    else:
                        price_str = "$0.00/1M"
                    paid_list.append((f"[{price_str}] {mid}", p_1m))
            
            free_list.sort()
            paid_list.sort(key=lambda x: x[1])
            paid_formatted = [x[0] for x in paid_list]
            
            if detailed:
                return {
                    "free": free_list,
                    "paid": paid_formatted,
                    "all": free_list + paid_formatted
                }
            return free_list + paid_formatted
    except Exception as e:
        print(f"Error fetching OpenRouter models: {e}")
    return {"free": [], "paid": [], "all": []} if detailed else []

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

def interpret_kappa(kappa, lang="tr"):
    """Kappa skorunun akademik yorumunu döner."""
    if lang == "tr":
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
    else:
        if kappa < 0:
            return "No Agreement / Random"
        elif kappa <= 0.20:
            return "Slight Agreement"
        elif kappa <= 0.40:
            return "Fair Agreement"
        elif kappa <= 0.60:
            return "Moderate Agreement"
        elif kappa <= 0.80:
            return "Substantial Agreement"
        else:
            return "Almost Perfect Agreement"
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

def analyze_comments_with_llm_consensus(comments, models_config, progress_callback=None, lang="tr"):
    """
    3 farklı modelle yorumları paralel analiz eder ve çoğunluk kararına göre birleştirir.
    models_config: list of 3 dicts: [{'provider': '...', 'api_key': '...', 'model': '...'}, ...]
    """
    if len(models_config) < 3:
        raise Exception("Mutabakat analizi için en az 3 model gereklidir." if lang == "tr" else "At least 3 models are required for consensus analysis.")

    results = {}

    def _safe_progress(value):
        """Thread-safe progress callback - silently ignores Streamlit context errors."""
        if not progress_callback:
            return
        try:
            progress_callback(value)
        except Exception:
            pass  # NoSessionContext vb. hataları yut, analizi durdurma

    progress_states = {"Model_1": 0.0, "Model_2": 0.0, "Model_3": 0.0}

    def get_progress_wrapper(model_idx_str):
        def cb(progress):
            progress_states[model_idx_str] = progress
            avg_progress = sum(progress_states.values()) / 3.0
            _safe_progress(avg_progress)
        return cb

    def run_analysis(idx, cfg):
        return analyze_comments_with_llm(
            comments, cfg["provider"], cfg["api_key"], cfg["model"], get_progress_wrapper(f"Model_{idx+1}"), lang=lang
        )

    # Modelleri sırayla (sequential) çalıştır - Streamlit thread uyumsuzluğunu tamamen önler
    for i, cfg in enumerate(models_config):
        model_name = cfg["model"]
        try:
            results[f"Model_{i+1}"] = run_analysis(i, cfg)
        except Exception as e:
            err_text = str(e)
            if not err_text:
                err_text = repr(e)
            raise Exception(f"Model {model_name} (Sira {i+1}) analiz sirasinda hata verdi: {err_text}" if lang == "tr" else f"Model {model_name} (Row {i+1}) failed during analysis: {err_text}")

    m1_results = results["Model_1"]
    m2_results = results["Model_2"]
    m3_results = results["Model_3"]

    consensus_results = []
    ratings_sentiment = []
    ratings_category = []
    ratings_role = []

    m1_name = models_config[0]["model"]
    m2_name = models_config[1]["model"]
    m3_name = models_config[2]["model"]
    
    lbl1 = f"Model_1 ({m1_name.split('/')[-1]})"
    lbl2 = f"Model_2 ({m2_name.split('/')[-1]})"
    lbl3 = f"Model_3 ({m3_name.split('/')[-1]})"

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
            agreement_level = "Tam Mutabakat" if lang == "tr" else "Full Consensus"
        elif min_votes == 1:
            agreement_level = "Uyuşmazlık" if lang == "tr" else "Disagreement"
        else:
            agreement_level = "Çoğunluk Kararı" if lang == "tr" else "Majority Decision"

        consensus_results.append({
            "original_id": c1["original_id"],
            "original_comment": c1["original_comment"],
            "sentiment": sent_val,
            "emotion": c1.get("emotion", "belirsiz" if lang == "tr" else "undetermined"),
            "category": cat_val,
            "role": role_val,
            "rhetorical_devices": list(set(c1.get("rhetorical_devices", []) + c2.get("rhetorical_devices", []) + c3.get("rhetorical_devices", []))),
            "confidence": round((sent_votes + cat_votes + role_votes) / 9.0, 2),
            "reasoning": f"Modeller arası mutabakat: {agreement_level}. Model 1 Gerekçesi: {c1.get('reasoning', '')}" if lang == "tr" else f"Consensus level: {agreement_level}. Model 1 Reasoning: {c1.get('reasoning', '')}",
            "consensus_details": {
                "agreement_level": agreement_level,
                "votes": {
                    "sentiment": {lbl1: c1["sentiment"], lbl2: c2["sentiment"], lbl3: c3["sentiment"]},
                    "category": {lbl1: c1["category"], lbl2: c2["category"], lbl3: c3["category"]},
                    "role": {lbl1: c1["role"], lbl2: c2["role"], lbl3: c3["role"]}
                }
            },
            "original_lang": c1.get("original_lang", "tr" if lang == "tr" else "en"),
            "translated_comment": c1.get("translated_comment", "")
        })

    kappa_sent = calculate_fleiss_kappa(ratings_sentiment)
    kappa_cat = calculate_fleiss_kappa(ratings_category)
    kappa_role = calculate_fleiss_kappa(ratings_role)

    valid_consensus = ["Tam Mutabakat", "Çoğunluk Kararı"] if lang == "tr" else ["Full Consensus", "Majority Decision"]
    consensus_count = sum(1 for r in consensus_results if r["consensus_details"]["agreement_level"] in valid_consensus)
    consensus_rate = (consensus_count / len(comments)) * 100 if len(comments) > 0 else 0.0

    stats = {
        "fleiss_kappa_sentiment": round(kappa_sent, 3),
        "fleiss_kappa_category": round(kappa_cat, 3),
        "fleiss_kappa_role": round(kappa_role, 3),
        "fleiss_kappa_sentiment_text": interpret_kappa(kappa_sent, lang),
        "fleiss_kappa_category_text": interpret_kappa(kappa_cat, lang),
        "fleiss_kappa_role_text": interpret_kappa(kappa_role, lang),
        "consensus_rate": round(consensus_rate, 1)
    }

    return consensus_results, stats
