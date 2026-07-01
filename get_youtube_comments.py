import sys
import os
import json
import hashlib
import re

# Etnografik Etik Ilkesi: Kullanici adlarini SHA-256 ile maskeleme fonksiyonu
def anonimlestir_kullanici(username):
    if not username:
        return "anonim_user"
    # Kullanici adini hashle ve ilk 8 karakterini al
    user_hash = hashlib.sha256(username.encode('utf-8')).hexdigest()[:8]
    return f"user_{user_hash}"

# Etnografik Etik Ilkesi: Yorum metnindeki kisisel isimleri ve @mentions ifadelerini maskeleme
def yorum_temizle(comment_text):
    if not comment_text:
        return ""
    # E-posta adreslerini temizle
    text = re.sub(r'\S+@\S+', '[eposta_maskelendi]', comment_text)
    # Telefon numaralarini temizle
    text = re.sub(r'\d{10,11}', '[telefon_maskelendi]', text)
    # YouTube @mentions (kullanici etiketlemelerini) maskele
    text = re.sub(r'@\w+', '@[kullanici_maskelendi]', text)
    return text

def video_kunyesi_uret(video_id):
    """
    Belirtilen video_id'ye ait thumbnail gorseli ve standart YouTube meta verilerini
    yt-dlp kullanarak dinamik ve gercek zamanli olarak ceker.
    """
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    meta = {
        "title": f"YouTube Video ({video_id})",
        "uploader": "Bilinmeyen Eğitmen",
        "views": "Bilinmiyor",
        "likes": "Bilinmiyor",
        "comment_count": "Bilinmiyor",
        "upload_date": "Bilinmiyor",
        "thumbnail": thumbnail_url,
        "url": video_url
    }
    
    try:
        import yt_dlp
        ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            if info:
                meta["title"] = info.get("title", meta["title"])
                meta["uploader"] = info.get("uploader", meta["uploader"])
                
                # Izlenme, Begeni ve Yorum Sayilarini formatlayarak ekle
                views = info.get("view_count")
                meta["views"] = f"{views:,}" if views is not None else "Bilinmiyor"
                
                likes = info.get("like_count")
                meta["likes"] = f"{likes:,}" if likes is not None else "Bilinmiyor"
                
                comments = info.get("comment_count")
                meta["comment_count"] = f"{comments:,}" if comments is not None else "Bilinmiyor"
                
                # Yuklenme Tarihi (YYYYMMDD -> DD.MM.YYYY)
                date_str = info.get("upload_date")
                if date_str and len(date_str) == 8:
                    meta["upload_date"] = f"{date_str[6:8]}.{date_str[4:6]}.{date_str[0:4]}"
                
                # Thumbnail
                meta["thumbnail"] = info.get("thumbnail", thumbnail_url)
    except Exception as e:
        print(f"yt-dlp meta-extraction failed: {e}")
        
    return meta

def download_live_comments(video_id_or_url, max_comments=50):
    """
    YouTube API anahtari olmadan belirtilen video_id'ye veya URL'ye ait yorumlari 
    youtube-comment-downloader kullanarak ceker, aninda anonimlestirir 
    ve maskelenmis sekilde liste olarak doner.
    """
    try:
        from youtube_comment_downloader import YoutubeCommentDownloader
        downloader = YoutubeCommentDownloader()
        
        if video_id_or_url.startswith("http"):
            url = video_id_or_url
        else:
            url = f"https://www.youtube.com/watch?v={video_id_or_url}"
        
        # Yorumlari popülerlige göre çek
        generator = downloader.get_comments_from_url(url, sort_by=0)
        
        fetched = []
        count = 0
        for comment in generator:
            if count >= max_comments:
                break
                
            comment_text = comment.get("text", "")
            username = comment.get("author", "")
            likes = comment.get("votes", 0)
            
            try:
                likes = int(likes)
            except ValueError:
                likes = 0
                
            fetched.append({
                "id": count + 1,
                "username": anonimlestir_kullanici(username),
                "video_title": f"Video_{video_id_or_url}",
                "comment": yorum_temizle(comment_text),
                "likes": likes
            })
            count += 1
            
        return fetched
    except Exception as e:
        print(f"Error downloading comments for {video_id_or_url}: {e}")
        return []

if __name__ == "__main__":
    print("YouTube Comment Anonymizer Starting...")
    print("ETHICAL WARNING: Usernames will be hashed via SHA-256 and identifiers masked.")
    print("Bu dosya genellikle arayüzden çağrılmaktadır (app.py) veya canlı test için import edilmektedir.")
