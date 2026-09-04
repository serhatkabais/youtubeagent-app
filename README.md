# İzleyici İklimi Aynası (Audience Climate Mirror)
### Büyük Dil Modeli Destekli Hesaplamalı Netnografi ve Dijital Antropoloji Platformu

**İzleyici İklimi Aynası**, çevrimiçi gayriresmi video paylaşım ortamlarında (YouTube vb.) oluşan asenkron izleyici topluluklarının kültürel iklimini, siber-jargonlarını, kolektif duygulanımlarını ve dijital rollerini inceleyen bir **Hesaplamalı Netnografi (Computational Netnography)** ve **Dijital Antropoloji** araştırma platformudur.

## 1. Araştırma ve Kuramsal Çerçeve
Bu çalışma, büyük veri çağında nitel araştırmanın karşılaştığı *ölçeklenebilirlik* sorununu, Büyük Dil Modellerinin (LLM) hesaplamalı kapasitesi ile aşmayı hedefler:
1. **Robert Kozinets – Netnografi Metodolojisi (2015, 2020):** İzleyici topluluğundaki aktörleri 4 arketipe ayırır: İçeridekiler/Akran Mentörleri (Insiders), Tutkulular/Üreticiler (Devotees), Sosyalleşenler (Minglers), Turistler (Tourists).
2. **Sara Ahmed – Duygulanım Teorisi (Affect Theory, 2004):** Yorumlardaki gelecek kaygısı ve işsizlik korkusunu bireysel şikayetler olarak değil, dijital ağlarda biriken ve yapışan **kolektif duygulanım iklimi** olarak analiz eder.
3. **Clifford Geertz – Yoğun Betimleme (Thick Description, 1973):** İroni, kinaye ve sarkastik övgüleri çözümleyerek metnin ardındaki kültürel alt-metni aydınlatır.
4. **Christine Hine – Bağlantılı Dijital Etnografi (2015):** Platformların sadece iletişim aracı değil, kendi folkloru ve ritüelleri olan kültürel artefaktlar olduğunu kabul eder.

## 2. Ajan Mimarisi ve Metodoloji
* **Ajan Türü:** **Hesaplamalı Netnografi ve Siber-Kültür Araştırma Ajanı (Computational Netnography Copilot)**
* **Çoklu Model Mutabakatı:** 3 farklı model (Llama-3, Gemini, Qwen/DeepSeek) paralel çalışarak Fleiss' Kappa (κ) katsayısı ile kodlayıcılar arası güvenilirlik üretir.
* **Kriptografik Etik Arıtma:** Kullanıcı adları SHA-256 ile maskelenir, @mentions etiketleri temizlenir.
* **Nitel Dışa Aktarma:** Kodlama matrisi tek tıkla MAXQDA / Excel (.xlsx) ve CSV formatında indirilebilir.

## 3. Klasör Yapısı
- `app.py` : Streamlit tabanlı New Yorker / Academic editorial araştırma arayüzü.
- `agent.py` : Dijital Etnografi ve Netnografi Ajanı çekirdeği (`IklimAynasiAgent`).
- `tools.py` : Kozinets tipolojisi dedektörü, dinamik topluluk sınıflandırıcısı ve etnografik analiz araçları.
- `api_client.py` : Multi-LLM mutabakat ve Fleiss' Kappa hesaplama motoru (Groq, Gemini, OpenRouter).
- `pdf_generator.py` : Akademik saha raporunu dinamik PDF olarak derleyen motor.
- `data/`
  - `ornek_yorumlar.json` : 15 arketipsel yorum içeren anonimleştirilmiş benchmark veri seti.
- `final_agent_raporu.md` : Yüksek lisans tez taslağı ve akademik makale metni.
- `requirements.txt` : Python paket listesi.
- `README.md` : Kurulum, kuramsal çerçeve ve metodoloji belgeleri.

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

## 6. Örnek Etnografik Analiz Çıktısı
* **Girdi (Yorum):** *"Yazılımcılık bitti artık her şeyi n8n ve yapay zeka ajanları ile hallediyorum."*
* **Ajan Çıktısı:**
  - **Saptanan Siber-Topluluk:** `Yazılım Geliştirme & Sistem Topluluğu`
  - **Saptanan Kolektif Duygulanım:** `Heyecan ve Keşif Motivasyonu (Otomasyon Tutkusu)`
  - **Kozinets Netnografik Rolü:** `Tutkulu / Üretici İzleyici (Devotee)`
  - **Etnografik Saha Notu:** *"İzleyici yüksek araç keşfi tutkusu sergilemektedir. Bilişsel tembellik riskine karşı, ona hazır komutları kopyalamak yerine sistem mimarisini ve problem çözme süreçlerini sorgulatan derinleştirici meydan okumalar verilmelidir."*

## 7. Metodolojik Sınırlar ve Araştırmacı Özdüşünümselliği
Ajanın ürettiği etnografik kodlamalar birer analitik başlangıç noktasıdır. Nitel araştırmalarda araştırmacının özdüşünümselliği (reflexivity) esastır; otomatik bulgular araştırmacının saha gözlemleri ve eleştirel süzgeciyle doğrulanmalıdır.

## 8. Etnografik Saha Arketipleri (Test Senaryoları)
Platform, çevrimiçi topluluklardaki 5 temel etkileşim arketipi üzerinden test edilmiştir:
1. **Sosyalleşen (Kozinets Mingler):** *"Eğitim harikaydı, teşekkürler!"* (Duygusal bağ ve topluluk aidiyeti, sosyal sermaye üretimi).
2. **Kolektif Kaygı ve Prekarite (Sara Ahmed):** *"Bu yapay zeka araçları yüzünden yakında hepimiz işsiz kalacağız."* (Mesleki gelecek kaygısının siber uzamda yapışkanlığı).
3. **Siber-İroni ve Kinaye (Alt-Metin):** *"Çok iyi ya, harika, hepimiz işsiz kaldık desene..."* (Sarkastik retorik ile maskelenen gerçek varoluşsal kaygı).
4. **Akran Mentörü & İçerideki (Kozinets Insider):** *"Localhost'ta çalışırken port hatası alıyorum..."* / *"docker-compose'da portu 5679 yap düzelir."* (Topluluğun organik pedagojik liderliği).
5. **Turist / Periferal Katılım (Kozinets Tourist - Lave & Wenger):** *"ilk yorum", "👍"* (Yüzeysel periferal tüketim; mikro etkileşim desteği).
