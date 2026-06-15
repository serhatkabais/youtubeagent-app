import os
import io
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Türkçe Karakter Desteği için Arial Yazı Tipini Kaydet
font_dir = r"C:\Windows\Fonts"
arial_normal = os.path.join(font_dir, "arial.ttf")
arial_bold = os.path.join(font_dir, "arialbd.ttf")

if os.path.exists(arial_normal) and os.path.exists(arial_bold):
    pdfmetrics.registerFont(TTFont("Arial", arial_normal))
    pdfmetrics.registerFont(TTFont("Arial-Bold", arial_bold))
    FONT_NAME = "Arial"
    FONT_BOLD = "Arial-Bold"
else:
    FONT_NAME = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

def escape_html_for_pdf(text):
    """
    ReportLab Paragraph XML ayrıştırıcısının hata vermesini önlemek için 
    &, <, > gibi karakterleri güvenli XML varlıklarına dönüştürür 
    ve emojileri temizler.
    """
    if not text:
        return ""
    text = str(text)
    
    # Emojileri ve tanımsız özel simgeleri temizle
    text = text.replace("📝", "")
    text = text.replace("🔍", "")
    text = text.replace("💡", "")
    text = text.replace("📺", "")
    text = text.replace("📊", "")
    text = text.replace("📋", "")
    text = text.replace("⚠️", "[UYARI]")
    text = text.replace("🟢", "[A]")
    text = text.replace("🟡", "[B]")
    text = text.replace("🔴", "[C]")
    
    # Ampersand ve açılı ayraçları XML-uyumlu yap (ReportLab Paragraph için zorunlu)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    
    # BMP dışındaki tüm Plane 1+ Unicode karakterlerini sil (Emojileri tamamen temizlemek için kesin çözüm)
    text = "".join(c for c in text if ord(c) <= 0xFFFF)
    return text

def clean_and_format_report(md_text):
    """
    Rapor içeriğindeki markdown yapılarını bozmadan ReportLab Paragraph 
    HTML etiketlerine dönüştürür ve ampersand çakışmalarını çözer.
    """
    if not md_text:
        return ""
    
    # Önce genel temizliği yap (ampersand kaçışı dahil)
    text = escape_html_for_pdf(md_text)
    
    # Markdown yapılarını HTML etiketlerine dönüştür
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'### (.*?)(?:\n|$)', r'<font size="11" color="#2B6CB0"><b>\1</b></font><br/>', text)
    text = re.sub(r'## (.*?)(?:\n|$)', r'<font size="13" color="#1A365D"><b>\1</b></font><br/>', text)
    
    # Streamlit markdown callout yönlendirmelerini düzelt
    text = text.replace("&amp;gt; [!IMPORTANT]", "<b>[ÖNEMLİ UYARI]</b>")
    text = text.replace("&amp;gt; [!WARNING]", "<b>[UYARI]</b>")
    text = text.replace("&amp;gt; [!NOTE]", "<b>[NOT]</b>")
    
    # Satır sonlarını br yap
    text = text.replace("\n", "<br/>")
    return text

def generate_analysis_pdf(meta, analysis, comments):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    
    # Özel Stiller
    title_style = ParagraphStyle(
        'PDFTitle',
        parent=styles['Heading1'],
        fontName=FONT_BOLD,
        fontSize=18,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=10,
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'PDFSubtitle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=15,
        alignment=1
    )
    
    h1_style = ParagraphStyle(
        'PDFH1',
        parent=styles['Heading2'],
        fontName=FONT_BOLD,
        fontSize=12,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'PDFBody',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9,
        textColor=colors.HexColor("#2D3748"),
        leading=13,
        spaceAfter=5
    )

    story = []
    
    # Başlık
    story.append(Paragraph("İZLEYİCİ İKLİMİ AYNASI RAPOR ÇIKTISI", title_style))
    story.append(Paragraph("İzleyici Analizi Nitel Analiz Karar Destek Raporu", subtitle_style))
    story.append(Spacer(1, 5))
    
    # Video Künyesi (Emojiler temizlendi)
    story.append(Paragraph("Analiz Edilen Video Künyesi", h1_style))
    story.append(Paragraph(f"<b>Video Başlığı:</b> {escape_html_for_pdf(meta['title'])}", body_style))
    story.append(Paragraph(f"👤 <b>Yayınlayan Kanal:</b> {escape_html_for_pdf(meta['uploader'])}", body_style))
    story.append(Paragraph(f"📅 <b>Yayın Tarihi:</b> {escape_html_for_pdf(meta.get('upload_date', 'Bilinmiyor'))}", body_style))
    story.append(Paragraph(f"👀 <b>İzlenme:</b> {escape_html_for_pdf(meta['views'])} | Beğeni: {escape_html_for_pdf(meta.get('likes', 'Bilinmiyor'))}", body_style))
    story.append(Spacer(1, 5))
    
    # Saptanan İklim (Emojiler temizlendi)
    story.append(Paragraph("Siber-Kültürel İklim Özeti", h1_style))
    story.append(Paragraph(f"<b>Saptanan Topluluk İklim Türü:</b> {escape_html_for_pdf(analysis['topluluk_turu_str'])}", body_style))
    story.append(Paragraph(f"<b>Kullanılan Analiz Modeli:</b> {escape_html_for_pdf(analysis.get('model_info', 'Kural Tabanlı Analiz (Çevrimdışı)'))}", body_style))
    story.append(Spacer(1, 5))
    
    # Grafiklerin oluşturulması ve PDF'e eklenmesi
    try:
        import plotly.express as px
        import pandas as pd
        from reportlab.platypus import Image
        
        # Duygu pastası
        duygu_df = pd.DataFrame(list(analysis["duygu"].items()), columns=["Kategori", "Sıklık"])
        fig_d = px.pie(
            duygu_df, 
            values="Sıklık", 
            names="Kategori", 
            title="Duygu ve Kaygı Dağılımı",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_d.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        img_d_bytes = fig_d.to_image(format="png", width=320, height=240)
        
        # Rol bar grafiği
        rol_df = pd.DataFrame(list(analysis["rol"].items()), columns=["Rol", "Sıklık"])
        fig_r = px.bar(
            rol_df, 
            x="Rol", 
            y="Sıklık", 
            title="Dijital Rol Dağılımı",
            color="Rol",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_r.update_layout(showlegend=False, margin=dict(l=10, r=10, t=30, b=10))
        img_r_bytes = fig_r.to_image(format="png", width=320, height=240)
        
        # In-memory Image flowables
        img_d = Image(io.BytesIO(img_d_bytes), width=220, height=165)
        img_r = Image(io.BytesIO(img_r_bytes), width=220, height=165)
        
        # Tablo
        g_table = Table([[img_d, img_r]], colWidths=[230, 230])
        g_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        story.append(Paragraph("Grafiksel Dağılımlar", h1_style))
        story.append(g_table)
        story.append(Spacer(1, 5))
    except Exception as chart_err:
        story.append(Paragraph(f"<i>Grafikler oluşturulamadı (Gerekli kütüphane eksik veya yükleniyor): {chart_err}</i>", body_style))
        story.append(Spacer(1, 5))
    
    # Rapor Metni (Dinamik markdown temizleyici çağrılıyor)
    story.append(Paragraph("Nitel Değerlendirme ve İzleyici Odaklı Öneriler", h1_style))
    html_rapor = clean_and_format_report(analysis["rapor"])
    story.append(Paragraph(html_rapor, body_style))
    story.append(Spacer(1, 10))
    
    # Yorumlar Kodlama Tablosu (Emojiler temizlendi)
    story.append(Paragraph("Etnografik Kodlama Tablosu (Seçilen Örneklem)", h1_style))
    table_data = [
        [Paragraph("<b>Kullanıcı</b>", body_style), Paragraph("<b>Temizlenmiş Yorum</b>", body_style), Paragraph("<b>Kategori</b>", body_style), Paragraph("<b>Dijital Rol</b>", body_style)]
    ]
    
    from tools import duygu_ve_kaygi_analizi, dijital_rol_dedektoru
    for c in comments[:20]: # Sayfa taşmasını önlemek için raporda ilk 20 yorumu gösteriyoruz
        c_girdi = [c]
        c_duygu = list(duygu_ve_kaygi_analizi(c_girdi, analysis["topluluk_turu"]).keys())[0]
        c_rol = list(dijital_rol_dedektoru(c_girdi, analysis["topluluk_turu"]).keys())[0]
        
        # Yorum metnini kısalt (tabloya sığması için)
        c_text = c["comment"]
        if len(c_text) > 85:
            c_text = c_text[:82] + "..."
            
        table_data.append([
            Paragraph(escape_html_for_pdf(c["username"]), body_style),
            Paragraph(escape_html_for_pdf(c_text), body_style),
            Paragraph(escape_html_for_pdf(c_duygu), body_style),
            Paragraph(escape_html_for_pdf(c_rol), body_style)
        ])
        
    t = Table(table_data, colWidths=[70, 210, 100, 110])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t)
    
    # Sayfa Sınırı Uyarısı (Eğer 20'den fazla yorum varsa)
    if len(comments) > 20:
        story.append(Spacer(1, 5))
        story.append(Paragraph(f"<i>Not: Yorum listesi uzunluğu nedeniyle tablolama ilk 20 yorum ile sınırlandırılmıştır. Toplam incelenen yorum: {len(comments)}</i>", body_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
