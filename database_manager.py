# -*- coding: utf-8 -*-
"""
database_manager.py
Dijital Etnografi ve Siber-Antropoloji Saha Arşivi ve Veri Tabanı Yöneticisi.
Desteklenen depolar:
1. Firebase Firestore (Bulut NoSQL - Kalıcı Çevrimiçi Depolama)
2. Yerel JSON Arşivi (data/fieldwork_archive.json - Kesintisiz Fallback)
"""

import os
import json
import glob
from datetime import datetime
import pandas as pd
import io

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

LOCAL_ARCHIVE_FILE = os.path.join("data", "fieldwork_archive.json")
_db_client = None
_db_status_message = "Başlatılmadı"
_db_is_connected = False


def find_firebase_credentials():
    """
    Firebase servis hesabı kimlik dosyasını veya ortam değişkenini bulur.
    1. FIREBASE_CREDENTIALS ortam değişkeni (dosya yolu veya JSON dizgesi)
    2. Proje kökündeki firebase_credentials.json veya *serviceAccount*.json
    """
    env_creds = os.getenv("FIREBASE_CREDENTIALS")
    if env_creds:
        if os.path.exists(env_creds):
            return env_creds
        if env_creds.strip().startswith("{"):
            try:
                json_data = json.loads(env_creds)
                return json_data
            except Exception:
                pass

    # Dosya araması
    candidates = [
        "firebase_credentials.json",
        "firebase_key.json",
        "serviceAccountKey.json"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c

    # Glob ile serviceAccount arama
    sa_matches = glob.glob("*serviceAccount*.json") + glob.glob("*firebase*.json")
    if sa_matches:
        return sa_matches[0]

    return None


class DBStatus(dict):
    """
    Hem sözlük olarak (.get("firestore_connected"))
    hem de 3'lü tuple (is_connected, client, msg) olarak açılabilen yapı.
    """
    def __init__(self, is_connected, client, msg):
        super().__init__(
            firestore_connected=is_connected,
            connected=is_connected,
            client=client,
            message=msg
        )
        self.is_connected = is_connected
        self.client = client
        self.message = msg

    def __iter__(self):
        return iter((self.is_connected, self.client, self.message))


class SaveResult(dict):
    """
    Hem sözlük olarak (.get("success"), .get("storage"))
    hem de 2'li tuple (success, msg) olarak açılabilen yapı.
    """
    def __init__(self, success, message, storage="local"):
        super().__init__(
            success=success,
            message=message,
            storage=storage
        )
        self.success = success
        self.message = message
        self.storage = storage

    def __iter__(self):
        return iter((self.success, self.message))


def init_database():
    """
    Firebase Firestore istemcisini ilklendirir.
    Başarısız olursa yerel arşiv moduna geçer.
    """
    global _db_client, _db_status_message, _db_is_connected

    if _db_client is not None:
        return DBStatus(_db_is_connected, _db_client, _db_status_message)

    if not FIREBASE_AVAILABLE:
        _db_is_connected = False
        _db_client = None
        _db_status_message = "Yerel Arşiv Modu (firebase-admin kütüphanesi yükleniyor)"
        return DBStatus(False, None, _db_status_message)

    creds_source = find_firebase_credentials()

    if not creds_source:
        _db_is_connected = False
        _db_client = None
        _db_status_message = "Yerel Arşiv Modu (Firebase anahtarı bekleniyor)"
        return DBStatus(False, None, _db_status_message)

    try:
        if not firebase_admin._apps:
            if isinstance(creds_source, dict):
                cred = credentials.Certificate(creds_source)
            else:
                cred = credentials.Certificate(creds_source)
            firebase_admin.initialize_app(cred)

        _db_client = firestore.client()
        _db_is_connected = True
        _db_status_message = "🟢 Firebase Firestore Bağlı (Bulut Arşivi Aktif)"
        return DBStatus(True, _db_client, _db_status_message)
    except Exception as e:
        _db_is_connected = False
        _db_client = None
        _db_status_message = f"Yerel Arşiv Modu (Firebase Hatası: {str(e)[:60]})"
        return DBStatus(False, None, _db_status_message)


def _ensure_local_archive_dir():
    os.makedirs(os.path.dirname(LOCAL_ARCHIVE_FILE), exist_ok=True)
    if not os.path.exists(LOCAL_ARCHIVE_FILE):
        with open(LOCAL_ARCHIVE_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def _load_local_archive():
    _ensure_local_archive_dir()
    try:
        with open(LOCAL_ARCHIVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_local_archive(data):
    _ensure_local_archive_dir()
    with open(LOCAL_ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_analysis(video_id, meta, analysis, comments):
    """
    Tamamlanan etnografik analizi Firebase Firestore'a ve yerel arşive kaydeder.
    """
    is_connected, db, _ = init_database()
    timestamp = datetime.now().isoformat()

    record = {
        "video_id": video_id,
        "title": meta.get("title", "Bilinmeyen Başlık"),
        "uploader": meta.get("uploader", "Bilinmeyen Kanal"),
        "views": str(meta.get("views", "0")),
        "likes": str(meta.get("likes", "0")),
        "comment_count": str(meta.get("comment_count", "0")),
        "upload_date": meta.get("upload_date", ""),
        "thumbnail": meta.get("thumbnail", ""),
        "url": meta.get("url", f"https://www.youtube.com/watch?v={video_id}"),
        "topluluk_turu": analysis.get("topluluk_turu", "genel"),
        "topluluk_turu_str": analysis.get("topluluk_turu_str", "Genel Topluluk"),
        "model_info": analysis.get("model_info", "Kural Tabanlı"),
        "duygu": analysis.get("duygu", {}),
        "rol": analysis.get("rol", {}),
        "consensus_stats": analysis.get("consensus_stats", {}),
        "sessiz_cogunluk": analysis.get("sessiz_cogunluk", {}),
        "rapor": analysis.get("rapor", ""),
        "llm_results": analysis.get("llm_results", []),
        "comments_sample_count": len(comments) if comments else 0,
        "created_at": timestamp,
        # Örneklem kodlama matrisi
        "comments": comments if comments else []
    }

    # 1. Yerel Arşive Kaydet / Güncelle (Daima Güvenli)
    local_data = _load_local_archive()
    # Mevcut kaydı varsa güncelle, yoksa ekle
    existing_idx = next((i for i, item in enumerate(local_data) if item.get("video_id") == video_id), None)
    if existing_idx is not None:
        local_data[existing_idx] = record
    else:
        local_data.insert(0, record)
    _save_local_archive(local_data)

    # 2. Firebase Firestore'a Kaydet (Varsa)
    if is_connected and db:
        try:
            doc_ref = db.collection("fieldwork_analyses").document(video_id)
            doc_ref.set(record)
            return SaveResult(True, "Firebase Firestore ve Yerel Arşive başarıyla kaydedildi.", storage="firestore")
        except Exception as e:
            return SaveResult(True, f"Yerel arşive kaydedildi, ancak Firebase hatası: {str(e)[:60]}", storage="local")

    return SaveResult(True, "Analiz yerel saha arşivine başarıyla kaydedildi.", storage="local")


def get_all_analyses():
    """
    Arşivlenmiş tüm video analizlerini döndürür.
    Önce Firebase'i dener, yoksa yerel arşivden çeker.
    """
    is_connected, db, _ = init_database()

    if is_connected and db:
        try:
            docs = db.collection("fieldwork_analyses").order_by("created_at", direction=firestore.Query.DESCENDING).stream()
            analyses = [doc.to_dict() for doc in docs]
            if analyses:
                return analyses
        except Exception:
            pass

    # Fallback to local
    return _load_local_archive()


def get_analysis(video_id):
    """Belirli bir video_id'ye ait analizi döndürür."""
    all_a = get_all_analyses()
    return next((a for a in all_a if a.get("video_id") == video_id), None)


def delete_analysis(video_id):
    """Analizi veri tabanından ve yerel arşivden siler."""
    is_connected, db, _ = init_database()
    if is_connected and db:
        try:
            db.collection("fieldwork_analyses").document(video_id).delete()
        except Exception:
            pass

    local_data = _load_local_archive()
    local_data = [item for item in local_data if item.get("video_id") != video_id]
    _save_local_archive(local_data)
    return True


def get_meta_analysis_dataframe():
    """
    Tüm arşivlenmiş analizleri çapraz-saha meta-analizi için
    derlenmiş bir pandas DataFrame olarak döndürür.
    """
    records = get_all_analyses()
    if not records:
        return pd.DataFrame()

    rows = []
    for r in records:
        sc = r.get("sessiz_cogunluk", {}) or {}
        cs = r.get("consensus_stats", {}) or {}
        duygu = r.get("duygu", {}) or {}
        rol = r.get("rol", {}) or {}

        # Baskın Duygu
        baskin_duygu = max(duygu, key=duygu.get) if duygu else "-"
        
        # Akran Mentörü Oranı
        total_comments = sum(duygu.values()) if duygu else 1
        mentor_count = rol.get("Icerideki / Akran Mentoru", rol.get("Akran Mentoru", 0))
        mentor_pct = round((mentor_count / total_comments * 100), 1) if total_comments > 0 else 0.0

        sample_count = r.get("comments_sample_count", len(r.get("comments", [])))
        if sample_count == 0 and r.get("comments"):
            sample_count = len(r.get("comments"))

        # Sayısal dönüşümler
        def _to_float(val, default=0.0):
            try:
                return float(val)
            except (ValueError, TypeError):
                return default

        cvr_val = _to_float(sc.get("cvr", 0.0))
        lvr_val = _to_float(sc.get("lvr", 0.0))
        lurker_val = _to_float(sc.get("lurker_ratio", 90.0), 90.0)

        rows.append({
            "video_id": r.get("video_id", ""),
            "baslik": r.get("title", "Bilinmeyen"),
            "kanal": r.get("uploader", "Bilinmeyen"),
            "topluluk_turu": r.get("topluluk_turu_str", "Genel"),
            "orneklem_sayisi": sample_count,
            "views": sc.get("views", r.get("views", 0)),
            "likes": sc.get("likes", r.get("likes", 0)),
            "comment_count": sc.get("comments", r.get("comment_count", 0)),
            "cvr": cvr_val,
            "lvr": lvr_val,
            "lurker_orani": lurker_val,
            "topluluk_canliligi": sc.get("tipoloji_baslik", "-"),
            "baskin_duygu": baskin_duygu,
            "mentor_pct": mentor_pct,
            "consensus_rate": cs.get("consensus_rate", 0),
            "kappa_sentiment": _to_float(cs.get("fleiss_kappa_sentiment", 0.0)),
            "kappa_category": _to_float(cs.get("fleiss_kappa_category", 0.0)),
            "kappa_role": _to_float(cs.get("fleiss_kappa_role", 0.0)),
            "tarih": r.get("created_at", "")[:10]
        })

    return pd.DataFrame(rows)


def export_combined_corpus():
    """
    Arşivdeki tüm videoları ve kodlanmış tüm yorumları iki sayfalı tek bir Excel dosyasında derler.
    Sheet 1: Saha_Ozetleri (Video-level metrikler)
    Sheet 2: Tum_Kodlanmis_Yorumlar (Büyük nitel külliyat)
    """
    records = get_all_analyses()
    excel_buffer = io.BytesIO()

    if not records:
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            pd.DataFrame(columns=["video_id", "baslik", "kanal", "topluluk_turu", "orneklem_sayisi", "cvr", "lurker_orani", "tarih"]).to_excel(writer, sheet_name="Saha_Ozetleri_Meta", index=False)
            pd.DataFrame(columns=["Video ID", "Video Başlığı", "Topluluk Türü", "Kullanıcı (SHA-256)", "Yorum Metni", "Beğeni", "Kategori", "Duygu", "Kozinets Rolü", "Mutabakat"]).to_excel(writer, sheet_name="Tum_Kodlanmis_Yorumlar", index=False)
        return excel_buffer.getvalue()

    df_meta = get_meta_analysis_dataframe()

    all_comments_rows = []
    for r in records:
        vid = r.get("video_id", "")
        vtitle = r.get("title", "")
        topluluk = r.get("topluluk_turu_str", "")
        comments = r.get("comments", [])
        
        for c in comments:
            c_text = c.get("comment", "")
            all_comments_rows.append({
                "Video ID": vid,
                "Video Başlığı": vtitle,
                "Topluluk Türü": topluluk,
                "Kullanıcı (SHA-256)": c.get("username", "anonim"),
                "Yorum Metni": c_text,
                "Beğeni": c.get("likes", 0),
                "Saptanan Kategori": c.get("category", c.get("sentiment_category", "-")),
                "Duygu/Duygulanım": c.get("sentiment", "-"),
                "Kozinets Rolü": c.get("role", "-"),
                "Mutabakat Durumu": c.get("consensus_details", {}).get("agreement_level", "-") if isinstance(c.get("consensus_details"), dict) else "-",
                "Tarih": c.get("time", "")
            })

    df_comments = pd.DataFrame(all_comments_rows) if all_comments_rows else pd.DataFrame(columns=["Video ID", "Video Başlığı", "Kullanıcı (SHA-256)", "Yorum Metni"])

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df_meta.to_excel(writer, sheet_name="Saha_Ozetleri_Meta", index=False)
        df_comments.to_excel(writer, sheet_name="Tum_Kodlanmis_Yorumlar", index=False)

    return excel_buffer.getvalue()
