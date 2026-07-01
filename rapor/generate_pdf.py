import os
import sys
import subprocess

def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# ReportLab kütüphanesini yükle ve içe aktar
install_and_import("reportlab")

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Türkçe Karakter Desteği için Arial Yazı Tipini Kaydet (Windows Uyumlu)
font_dir = r"C:\Windows\Fonts"
arial_normal = os.path.join(font_dir, "arial.ttf")
arial_bold = os.path.join(font_dir, "arialbd.ttf")

if os.path.exists(arial_normal) and os.path.exists(arial_bold):
    pdfmetrics.registerFont(TTFont("Arial", arial_normal))
    pdfmetrics.registerFont(TTFont("Arial-Bold", arial_bold))
    FONT_NAME = "Arial"
    FONT_BOLD = "Arial-Bold"
else:
    # Fallback (Eğer Arial bulunamazsa standart Helvetica kullanılır fakat Türkçe karakterler bozulabilir)
    FONT_NAME = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

def build_pdf(filename="proje_raporu.pdf"):
    # Dosya klasörünü oluştur
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
    
    # Doküman Yapılandırması (A4)
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Özel Stil Tanımlamaları
    title_style = ParagraphStyle(
        'RaporTitle',
        parent=styles['Heading1'],
        fontName=FONT_BOLD,
        fontSize=20,
        textColor=colors.HexColor("#1A365D"),  # Koyu Lacivert
        spaceAfter=15,
        alignment=1  # Center
    )
    
    subtitle_style = ParagraphStyle(
        'RaporSubtitle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=11,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    h1_style = ParagraphStyle(
        'RaporH1',
        parent=styles['Heading2'],
        fontName=FONT_BOLD,
        fontSize=14,
        textColor=colors.HexColor("#2B6CB0"),  # Mavi
        spaceBefore=12,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'RaporBody',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        textColor=colors.HexColor("#2D3748"),
        leading=14,
        spaceAfter=8
    )
    
    code_style = ParagraphStyle(
        'RaporCode',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=8,
        textColor=colors.HexColor("#2D3748"),
        backColor=colors.HexColor("#EDF2F7"),
        borderColor=colors.HexColor("#CBD5E0"),
        borderWidth=1,
        borderPadding=6,
        leading=11,
        spaceAfter=10
    )
    
    warning_style = ParagraphStyle(
        'RaporWarning',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9,
        textColor=colors.HexColor("#C53030"),
        backColor=colors.HexColor("#FFF5F5"),
        borderColor=colors.HexColor("#FEB2B2"),
        borderWidth=1,
        borderPadding=8,
        leading=12,
        spaceAfter=10
    )

    story = []
    
    # ----------------- KAPAK SAYFASI -----------------
    story.append(Spacer(1, 100))
    story.append(Paragraph("EĞİTİMDE YAPAY ZEKÂ KULLANIMI", title_style))
    story.append(Paragraph("FİNAL AGENT PROJE RAPORU", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Konu:</b> Eğitim Videoları İzleyici Yorum Analiz Ajanı<br/>(Çevrimiçi Topluluk Etnografik İncelemesi)", subtitle_style))
    story.append(Spacer(1, 150))
    
    # Kapak Alt Bilgisi
    info_data = [
        [Paragraph("<b>Hazırlayan:</b>", body_style), Paragraph("Eğitim Teknolojileri Yüksek Lisans Öğrencisi", body_style)],
        [Paragraph("<b>Ajan Türü:</b>", body_style), Paragraph("Araç Kullanan & Öneri Ajanı (Tool-Using Agent)", body_style)],
        [Paragraph("<b>Tarih:</b>", body_style), Paragraph("Haziran 2026", body_style)],
        [Paragraph("<b>Metodoloji:</b>", body_style), Paragraph("Dijital Etnografya ve Dijital Antropoloji", body_style)]
    ]
    info_table = Table(info_data, colWidths=[100, 300])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(info_table)
    story.append(PageBreak())
    
    # ----------------- İÇERİK SAYFASI 1 -----------------
    story.append(Paragraph("1. Projenin Genel Tanımı ve Kapsamı", h1_style))
    story.append(Paragraph(
        "Bu proje, asenkron ve gayriresmi (informal) izleyici topluluklarında yapay zekâ okuryazarlığını, "
        "gelecek kaygılarını, akran yardımlaşması kültürünü ve dijital rolleri karşılaştırmalı olarak analiz eden bir "
        "karar destek ajanı modelidir.",
        body_style
    ))
    
    story.append(Paragraph("2. Dijital Etnografya & Antropoloji Yaklaşımı", h1_style))
    story.append(Paragraph(
        "Çalışmada kullanılan iki temel yöntem bulunmaktadır:<br/>"
        "- <b>Dijital Etnografya:</b> Topluluk üyelerinin birbirlerine sundukları teknik önerileri, problem çözme yaklaşımlarını ve akran yardımlaşmasını (akran mentörlüğü) izler.<br/>"
        "- <b>Dijital Antropoloji:</b> Teknolojinin insan kimliği ve mesleki gelecek algısı üzerindeki dönüştürücü etkisini saptar (örneğin; tasarımcıların 'işsiz kalma korkusu' veya sistemcilerin 'bilişsel yükü devretme' süreçleri).",
        body_style
    ))
    
    # Tablo: Karşılaştırmalı Video Veri Seti
    story.append(Paragraph("Tablo 1: Analiz Edilen Örnek Video Veri Setleri", h1_style))
    table_data = [
        [Paragraph("<b>Kategori</b>", body_style), Paragraph("<b>Video Başlığı</b>", body_style), Paragraph("<b>Odak Kitle</b>", body_style)],
        [Paragraph("Yaratıcı", body_style), Paragraph("Yapay Zeka ile İçerik Üretimi", body_style), Paragraph("Yaratıcı Kaygı", body_style)],
        [Paragraph("Teknik", body_style), Paragraph("Yapay Zeka Ajanları ve Otomasyon", body_style), Paragraph("Otomasyon/Kod", body_style)]
    ]
    t = Table(table_data, colWidths=[100, 250, 130])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # ----------------- İÇERİK SAYFASI 2 -----------------
    story.append(Paragraph("3. Ajan Mimarisi ve Karar Akışı (`agent.py`)", h1_style))
    story.append(Paragraph(
        "Ajanımız, modüler olarak `agent.py` içinde tanımlanmış bir <b>İzleyiciEtnografiAgent</b> sınıfıdır. "
        "Rolü, 'Dijital Etnografya ve İzleyici Analizi Asistanı' olarak belirlenmiştir. Yönergedeki tüm şartları karşılar:<br/>"
        "- <b>Sistem Promptu:</b> Ajanın analiz sınırlarını ve etnografik rolünü netleştirir.<br/>"
        "- <b>Karar Akışı:</b> Gelen veri kümesini okur, kanal türüne göre ilgili analiz araçlarını sırayla tetikler.<br/>"
        "- <b>Bellek Loglama (Log):</b> Yapılan tüm araç çağrılarını ve işlem kararlarını oturum içi bellek nesnesinde saklar.",
        body_style
    ))
    
    story.append(Paragraph("4. Analiz Araçları ve Algoritmalar (`tools.py`)", h1_style))
    story.append(Paragraph(
        "Analizler `tools.py` içinde yer alan üç bağımsız araç (fonksiyon) tarafından yürütülür:<br/>"
        "1. <b>duygu_ve_kaygi_analizi():</b> Yorumları duygusal ve tematik kategorilere (Kaygı, Heyecan, Hata vb.) ayırır.<br/>"
        "2. <b>dijital_rol_dedektoru():</b> Yorum sahiplerinin topluluk rollerini (Akran Mentörü, Bağımsız İzleyici vb.) bulur.<br/>"
        "3. <b>izleyici_raporu_olusturucu():</b> Elde edilen verileri sentezleyerek içerik üreticilerine ve araştırmacılara yönelik öneriler hazırlar.",
        body_style
    ))
    
    story.append(Paragraph("5. Etnografik Araştırmada Etik ve Güvenlik Önlemleri", h1_style))
    story.append(Paragraph(
        "Araştırmanın etik ve akademik standartlara uygun olması için <b>`get_youtube_comments.py`</b> içinde iki kademeli veri arıtma uygulanmıştır:<br/>"
        "1. <b>Kullanıcı Adı Anonimleştirme:</b> Tüm kullanıcı adları SHA-256 algoritmasıyla hashlenebilir kimliklere dönüştürülmüştür (Örn: user_8f6ab984).<br/>"
        "2. <b>Mentions Maskeleme:</b> Yorum metinlerindeki @etiketlemeleri regex ile taranarak @[kullanici_maskelendi] haline getirilmiştir. Böylece geriye dönük arama yapılması ve kullanıcı kimliklerinin deşifre edilmesi engellenmiştir.",
        body_style
    ))
    
    # Etik Sınır Uyarısı
    story.append(Paragraph(
        "<b>⚠️ ETİK SINIR UYARISI:</b> Bu rapordaki ve yazılımdaki tüm analizler, izleyici araştırmacısı için bir karar destek aracıdır. "
        "Yapay zekanın kararları nihai olamaz; tasarım, içerik ve etik kararların alınmasında mutlaka insan (üretici/araştırmacı) denetimi gereklidir.",
        warning_style
    ))
    
    doc.build(story)
    print("PDF Report compiled successfully at: " + filename)

if __name__ == "__main__":
    build_pdf("proje_raporu.pdf")
