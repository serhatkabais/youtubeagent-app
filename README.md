# İzleyici İklimi Aynası (İklim-Ajan)

Bu yapay zekâ ajanı, çevrimiçi/gayriresmi izleyici topluluklarındaki (YouTube eğitim kanalları vb.) izleyici iklimini, jargonları, gelecek kaygılarını, akran yardımlaşması kültürünü ve dijital rolleri analiz eden bir karar destek aracıdır.

## 1. Amaç
Projenin amacı, eğitim ve teknoloji içerikli yayınlarda asenkron olarak gerçekleşen informal izleyici etkileşimlerini siber-kültürel bir mercekten incelemektir. Ajan, girilen tek bir video bağlantısındaki tüm yorumları analiz ederek topluluğun iklim türünü otomatik tespit eder, kullanılan LLM model bilgisini belirtir, toplu istatistikler üretir ve her yoruma özel izleyici odaklı tavsiyeler geliştirir.

## 2. Agent Türü
* **Seçilen Agent Türü:** **Araç Kullanan Agent (Tool-Using Agent) ve Karar Destek Ajanı**
* **Gerekçe:** Ajanımız, kullanıcı girdisi olarak verilen yorumları aldıktan sonra karar akışı doğrultusunda `tools.py` içerisindeki analiz araçlarını (`topluluk_turu_tespit_et`, `duygu_ve_kaygi_analizi`, `dijital_rol_dedektoru`, `izleyici_raporu_olusturucu` ve `tekil_yorum_izleyici_onerisi`) çağırarak bu çıktıları birleştirmekte ve izleyici odaklı kararlar için tavsiyeler üretmektedir.

## 3. Klasör Yapısı
- `egitimde_yapay_zeka_final_agent_proje_odevi.pdf` : Orijinal ödev yönergesi.
- `app.py` : Streamlit tabanlı kullanıcı arayüzü, kullanılan LLM modeli gösterimi, otomatik künye ve tekil yorum gezinti paneli.
- `agent.py` : Ajan rolü, sistem talimatı ve işlem günlüğünü (bellek) yöneten ana sınıf (`IklimAynasiAgent`).
- `tools.py` : Etnografik analizleri yürüten otomatik topluluk tespiti, kural tabanlı duygu/rol dedektörleri ve izleyici odaklı tavsiye fonksiyonları.
- `data/`
  - `ornek_yorumlar.json` : Derlenmiş örnek yorum veri seti (isteğe bağlı).
- `prompts/`
  - `ai_development_log.md` : Geliştirme sürecinde yapay zekâ asistanlarına verilen promptların kayıt defteri.
- `.env.example` : Ortam değişkenleri şablonu.
- `requirements.txt` : Python paket listesi.
- `README.md` : Kurulum, çalıştırma ve genel proje belgeleri.

## 4. Kurulum
Aşağıdaki komutları sırasıyla terminalde çalıştırarak sanal ortamınızı oluşturun ve bağımlılıkları yükleyin:
```bash
# Sanal ortam oluşturma
python -m venv venv

# Sanal ortamı aktifleştirme (Windows)
venv\Scripts\activate

# Gerekli paketlerin yüklenmesi
pip install -r requirements.txt
```

## 5. Çalıştırma
Streamlit uygulamasını başlatmak için terminale şu komutu yazın:
```bash
streamlit run app.py
```

## 6. Örnek Kullanım
* **Girdi (Yorum):** *"Yazılımcılık bitti artık her şeyi n8n ve yapay zeka ajanları ile hallediyorum."*
* **Ajan Çıktısı:**
  - **Saptanan İklim Türü:** `Genel / Karma Eğitim Topluluğu`
  - **Saptanan Etnografik Duygu/Kaygı:** `Otomasyon ve Verimlilik`
  - **Saptanan Topluluk Rolü:** `Otomasyon Meraklısı / İzleyici`
  - **Kişiselleştirilmiş İzleyici Odaklı Öneri:** *"İzleyici verimlilik odağında yüksek motivasyona sahiptir. Ancak bilişsel tembellik riskine karşı, ona otomasyonun arka planındaki mantıksal mimariyi soran derinleştirici ödevler verilmelidir."*

## 7. Sınırlılıklar ve Etik Sınır
* Ajanın ürettiği izleyici odaklı müdahale önerileri birer karar destek girdisidir. Yapay zekâ analizlerinin hata payı ve veri yanlılığı (bias) göz önünde bulundurularak, tüm tasarım ve analiz kararları mutlaka **insan (üretici/araştırmacı) gözetiminde** uygulanmalıdır.

## 8. Test Senaryoları (Asgari 5 Senaryo)
Proje, ajanın karar akışını sınamak için aşağıdaki 5 farklı izleyici yorum senaryosu ile test edilmiştir:
1. **Normal/Pozitif İzleyici Profili:** *"Eğitim harikaydı, teşekkürler!"* (Ajan: Sosyal Destek ve Teşekkür olarak algılar, Pasif Destekçi rolünü atar, motivasyon artırıcı tavsiye verir.)
2. **Mesleki Gelecek Kaygısı Taşıyan Profil:** *"Bu yapay zeka araçları yüzünden yakında hepimiz işsiz kalacağız."* (Ajan: Gelecek Kaygısı olarak saptar, insan denetimini vurgulayan eğitsel bir atölye önerir.)
3. **İroni ve Kinaye İçeren Karmaşık Girdi:** *"Çok iyi ya, harika, hepimiz işsiz kaldık desene..."* (Ajan: Retorik aracı (İroni/Kinaye) tespit eder, arkasındaki gerçek duygunun kaygı olduğunu ayrıştırır.)
4. **Teknik Sorun Yaşayan ve Destek Arayan Profil:** *"Localhost'ta çalıştırırken port hatası alıyorum, nasıl çözeceğim?"* (Ajan: Teknik Sorun / Destek Arayışı olarak işaretler, asenkron SSS veya akran mentörlüğü mekanizması önerir.)
5. **Aşırı Kısa / Yüzeysel Girdi (Eksik/Uç Değer):** *"ilk yorum", "👍"* (Ajan: Genel Gözlem / Yüzeysel Katılım olarak sınıflandırır, derinleştirici müdahale üretmez.)
