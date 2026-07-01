import os
from PIL import Image, ImageDraw, ImageFont

def wrap_text(text, font, max_width):
    """Wraps text to fit within a maximum width in pixels."""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        w = bbox[2] - bbox[0]
        
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            
    if current_line:
        lines.append(' '.join(current_line))
        
    return lines

def get_box_height(title, bullet_points, font_title, font_text, box_w):
    """Calculates the height of a box dynamically based on its text content."""
    padding_top = 18
    title_height = 22
    padding_between_title_and_text = 10
    
    cur_y = padding_top + title_height + padding_between_title_and_text
    max_text_width = box_w - 55
    
    for pt in bullet_points:
        text_to_wrap = pt.strip("• ")
        wrapped_lines = wrap_text(text_to_wrap, font_text, max_text_width)
        for line in wrapped_lines:
            cur_y += 20
        cur_y += 4 # Extra spacing between points
        
    padding_bottom = 18
    return cur_y + padding_bottom

def draw_arch():
    # Canvas size: 1400 x 1200 (Expanded height to prevent overlap)
    width = 1400
    height = 1200
    
    # Creamy/soft background to match academic theme
    img = Image.new("RGB", (width, height), "#FDFBF7")
    draw = ImageDraw.Draw(img)
    
    # Fonts
    font_path = r"C:\Windows\Fonts\arial.ttf"
    font_bold_path = r"C:\Windows\Fonts\arialbd.ttf"
    
    if os.path.exists(font_path):
        font_title = ImageFont.truetype(font_bold_path, 32)
        font_box_title = ImageFont.truetype(font_bold_path, 18)
        font_box_text = ImageFont.truetype(font_path, 14)
        font_arrow = ImageFont.truetype(font_path, 13)
        font_arrow_bold = ImageFont.truetype(font_bold_path, 13)
    else:
        font_title = ImageFont.load_default()
        font_box_title = ImageFont.load_default()
        font_box_text = ImageFont.load_default()
        font_arrow = ImageFont.load_default()
        font_arrow_bold = ImageFont.load_default()
        
    # Draw Header & Subtitle
    draw.text((width // 2, 45), "İZLEYİCİ İKLİMİ AYNASI", fill="#1A365D", font=font_title, anchor="mm")
    draw.text((width // 2, 80), "Ajan Karar Akışı ve Metodolojik Yapı Şeması", fill="#4A5568", font=font_arrow, anchor="mm")
    draw.line((150, 105, width - 150, 105), fill="#D5CDB5", width=2)
    
    def draw_rounded_box(x, y, w, h, title, bullet_points, bg_color, border_color, radius=10):
        # Draw soft shadow
        draw.rounded_rectangle([x + 4, y + 4, x + w + 4, y + h + 4], radius=radius, fill="#EBE5D9")
        # Draw box
        draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=bg_color, outline=border_color, width=2)
        # Draw Title
        draw.text((x + 20, y + 18), title, fill="#1A365D", font=font_box_title)
        
        # Draw wrapped bullet points
        cur_y = y + 48
        max_text_width = w - 55 # Exact width available from x+35 to x+w-20
        
        for pt in bullet_points:
            # Bullet point symbol
            draw.text((x + 20, cur_y), "•", fill=border_color, font=font_box_text)
            
            # Wrap text (removing the bullet point symbol from wrap logic)
            text_to_wrap = pt.strip("• ")
            wrapped_lines = wrap_text(text_to_wrap, font_box_text, max_text_width)
            
            for line in wrapped_lines:
                draw.text((x + 35, cur_y), line, fill="#2D3748", font=font_box_text)
                cur_y += 20
            cur_y += 4 # Extra spacing between points
            
        return h

    # Draw arrow helper
    def draw_arrow(x1, y1, x2, y2, label="", flow="down", is_dashed=False):
        if is_dashed:
            steps = int(((x2-x1)**2 + (y2-y1)**2)**0.5 / 10)
            for s in range(steps):
                if s % 2 == 0:
                    px1 = x1 + (x2-x1) * s / steps
                    py1 = y1 + (y2-y1) * s / steps
                    px2 = x1 + (x2-x1) * (s+1) / steps
                    py2 = y1 + (y2-y1) * (s+1) / steps
                    draw.line((px1, py1, px2, py2), fill="#718096", width=2)
        else:
            draw.line((x1, y1, x2, y2), fill="#4A5568", width=2)
            
        if flow == "down":
            draw.polygon([(x2 - 6, y2 - 8), (x2 + 6, y2 - 8), (x2, y2)], fill="#4A5568")
            if label:
                draw.text((x1 + 10, (y1 + y2) // 2), label, fill="#4A5568", font=font_arrow_bold, anchor="lm")
        elif flow == "right":
            draw.polygon([(x2 - 8, y2 - 6), (x2 - 8, y2 + 6), (x2, y2)], fill="#4A5568")
            if label:
                draw.text(((x1 + x2) // 2, y1 - 14), label, fill="#4A5568", font=font_arrow_bold, anchor="mm")
        elif flow == "left":
            draw.polygon([(x2 + 8, y2 - 6), (x2 + 8, y2 + 6), (x2, y2)], fill="#4A5568")
            if label:
                draw.text(((x1 + x2) // 2, y1 - 14), label, fill="#4A5568", font=font_arrow_bold, anchor="mm")
        elif flow == "up":
            draw.polygon([(x2 - 6, y2 + 8), (x2 + 6, y2 + 8), (x2, y2)], fill="#4A5568")
            if label:
                draw.text((x1 + 10, (y1 + y2) // 2), label, fill="#4A5568", font=font_arrow_bold, anchor="lm")

    # Define box sizes and text content
    box1_title = "1. Kullanıcı Girdisi"
    box1_pts = [
        "YouTube Video Bağlantısı veya Video ID kodu.",
        "Ajan çalışması için model ve API sağlayıcı seçimi."
    ]
    box1_w = 400
    box1_h = get_box_height(box1_title, box1_pts, font_box_title, font_box_text, box1_w)
    
    box2_title = "2. Veri Çekimi ve Güvenlik Filtresi"
    box2_pts = [
        "get_youtube_comments.py modülüyle yorum havuzunun asenkron indirilmesi.",
        "Kullanıcı adlarının SHA-256 kriptografik algoritmasıyla maskelenmesi.",
        "Yorum metinlerindeki @etiketlemelerin regex filtreleriyle temizlenmesi."
    ]
    box2_w = 500
    box2_h = get_box_height(box2_title, box2_pts, font_box_title, font_box_text, box2_w)

    box3_title = "3. Otomatik Topluluk İklim Dedektörü"
    box3_pts = [
        "Heuristic kelime frekansı taramasıyla topluluk türü tespiti.",
        "Kitlenin eğitim alanındaki ilgi ve analiz profiline göre sınıflandırılması."
    ]
    box3_w = 500
    box3_h = get_box_height(box3_title, box3_pts, font_box_title, font_box_text, box3_w)

    box4a_title = "4A. Kural Tabanlı Karar Akışı"
    box4a_pts = [
        "Sözlük eşleşmesi (heuristic) ile 12 tematik kategorinin taranması.",
        "Kullanıcıların dijital rollerinin (Akran Mentörü vb.) bulunması.",
        "İroni ve sarkastik kalıplar için temel regex filtrelerinin işletilmesi.",
        "Sıfır token maliyetiyle yerel ve hızlı analiz fallback kanalı."
    ]
    box4a_w = 480
    box4a_h = get_box_height(box4a_title, box4a_pts, font_box_title, font_box_text, box4a_w)

    box4b_title = "4B. LLM-First Doğal Dil Analizi"
    box4b_pts = [
        "api_client.py modülüyle batch yorumların API'ye gönderilmesi.",
        "Gelişmiş dijital etnografi system prompt talimatları.",
        "Gizli ironi, kinaye ve dolaylı retorik araçların semantik analizi.",
        "Analiz güven skoru (confidence) ve gerekçelendirme üretimi."
    ]
    box4b_w = 480
    box4b_h = get_box_height(box4b_title, box4b_pts, font_box_title, font_box_text, box4b_w)

    box5_title = "5. Ajan İşlem Günlüğü (Bellek)"
    box5_pts = [
        "Tüm karar akış adımlarının self.logs listesinde saklanması.",
        "UI arayüzündeki günlük paneline dinamik aktarım."
    ]
    box5_w = 500
    box5_h = get_box_height(box5_title, box5_pts, font_box_title, font_box_text, box5_w)

    box6_title = "6. Karar Destek Çıktıları ve Pedagojik Müdahaleler"
    box6_pts = [
        "Plotly pastası ve bar grafikleriyle topluluk iklimi görselleştirmesi (app.py).",
        "Etnografik sentez raporu ve tekil yorum gezinti/öneri paneli.",
        "Yoruma özel bağlamsal pedagojik müdahale önerileri (tools.py -> tekil_yorum_izleyici_onerisi)."
    ]
    box6_w = 750
    box6_h = get_box_height(box6_title, box6_pts, font_box_title, font_box_text, box6_w)

    # Dynamic Layout Positions
    y1 = 130
    b1 = y1 + box1_h
    
    y2 = b1 + 50
    b2 = y2 + box2_h
    
    y3 = b2 + 50
    b3 = y3 + box3_h
    
    y4 = b3 + 70
    b4a_bottom = y4 + box4a_h
    b4b_bottom = y4 + box4b_h
    b4_max = max(b4a_bottom, b4b_bottom)
    
    y5 = b4_max + 60
    b5 = y5 + box5_h
    
    y6 = b5 + 50
    b6 = y6 + box6_h
    
    # Draw Boxes
    # Box 1
    x1 = (width - box1_w) // 2
    draw_rounded_box(x1, y1, box1_w, box1_h, box1_title, box1_pts, bg_color="#FFFDF5", border_color="#D69E2E")
    
    # Box 2
    x2 = (width - box2_w) // 2
    draw_rounded_box(x2, y2, box2_w, box2_h, box2_title, box2_pts, bg_color="#F0FDF4", border_color="#38A169")
    
    # Box 3
    x3 = (width - box3_w) // 2
    draw_rounded_box(x3, y3, box3_w, box3_h, box3_title, box3_pts, bg_color="#F0F9FF", border_color="#3182CE")
    
    # Box 4A & 4B
    x4a = 150
    x4b = width - 150 - box4b_w
    draw_rounded_box(x4a, y4, box4a_w, box4a_h, box4a_title, box4a_pts, bg_color="#F8FAFC", border_color="#64748B")
    draw_rounded_box(x4b, y4, box4b_w, box4b_h, box4b_title, box4b_pts, bg_color="#EEF2FF", border_color="#4F46E5")
    
    # Box 5
    x5 = (width - box5_w) // 2
    draw_rounded_box(x5, y5, box5_w, box5_h, box5_title, box5_pts, bg_color="#FAF5FF", border_color="#805AD5")
    
    # Box 6
    x6 = (width - box6_w) // 2
    draw_rounded_box(x6, y6, box6_w, box6_h, box6_title, box6_pts, bg_color="#FFF5F5", border_color="#E53E3E")

    # Draw Arrows
    # Arrow 1 -> 2
    draw_arrow(width // 2, b1, width // 2, y2)
    
    # Arrow 2 -> 3
    draw_arrow(width // 2, b2, width // 2, y3)
    
    # Branching from 3
    y_branch = b3 + 25
    draw.line((width // 2, b3, width // 2, y_branch), fill="#4A5568", width=2)
    draw.line((x4a + box4a_w // 2, y_branch, x4b + box4b_w // 2, y_branch), fill="#4A5568", width=2)
    
    # Arrows down to 4A & 4B
    draw_arrow(x4a + box4a_w // 2, y_branch, x4a + box4a_w // 2, y4, label=" API Çevrimdışı ")
    draw_arrow(x4b + box4b_w // 2, y_branch, x4b + box4b_w // 2, y4, label=" API Çevrimiçi ")
    
    # Merging from 4A & 4B
    y_merge = b4_max + 25
    draw.line((x4a + box4a_w // 2, b4a_bottom, x4a + box4a_w // 2, y_merge), fill="#4A5568", width=2)
    draw.line((x4b + box4b_w // 2, b4b_bottom, x4b + box4b_w // 2, y_merge), fill="#4A5568", width=2)
    draw.line((x4a + box4a_w // 2, y_merge, x4b + box4b_w // 2, y_merge), fill="#4A5568", width=2)
    
    # Arrow down to 5
    draw_arrow(width // 2, y_merge, width // 2, y5)
    
    # Arrow 5 -> 6
    draw_arrow(width // 2, b5, width // 2, y6)
    
    # Feedback loop (Dashed arrow back to Box 1)
    draw.line((x6, y6 + box6_h // 2, 60, y6 + box6_h // 2), fill="#718096", width=2)
    draw.line((60, y6 + box6_h // 2, 60, y1 + box1_h // 2), fill="#718096", width=2)
    draw_arrow(60, y1 + box1_h // 2, x1, y1 + box1_h // 2, label="  Yeni Arama / Video Seçimi", flow="right", is_dashed=True)
    
    # Save Image
    output_path = r"D:\CODING TOOLS\ANTIGRAVITY\cumali-hoca-odev-final\agent_architecture.png"
    img.save(output_path, "PNG")
    print(f"Perfect diagram saved successfully to {output_path}")

if __name__ == "__main__":
    draw_arch()
